"""Measure a reference ecosystem's dependency graph without cloning it.

The catalogue's own dependency measurement reads manifests *and* scans every
Python file for imports, which needs a full mirror of each repository. A few
hundred repositories cannot be mirrored, so this module reads only what an API
can serve: one recursive tree listing per repository, then the manifests that
listing names.

That is the same evidence as ``dependency_record``'s ``declared`` half, parsed
by the same functions, so a graph built here and a graph built there are
measuring the same thing.
"""

from __future__ import annotations

import tomllib
from typing import Any

import httpx

from oss_das.clients.base import SourceError
from oss_das.clients.github import GitHubClient
from oss_das.collection import SOURCE_FAILURES
from oss_das.measure import (
    DEPENDENCY_KINDS,
    DEPENDENCY_MANIFESTS,
    TOOLING,
    _strongest,
    declared_dependencies,
)

#: Raw file host. Manifests are fetched here rather than through the contents
#: API because it does not spend the core rate-limit budget, which the tree
#: listings need.
RAW = "https://raw.githubusercontent.com"

#: Every way reading one repository is allowed to fail without ending the run.
READ_FAILURES = (*SOURCE_FAILURES, httpx.RequestError)


def manifest_paths(paths: list[str]) -> list[str]:
    """The manifests in one repository's tree, in a stable order."""
    return sorted(p for p in paths if DEPENDENCY_MANIFESTS.search(p))


def distribution_name(pyproject: str) -> str | None:
    """The name a project publishes under, from its own pyproject.

    A repository is depended on by the name it puts on the distribution, which
    is often not the name of the repository -- ``daspy`` ships as
    ``daspy-toolbox``. Without this the graph would miss those edges entirely.
    """
    try:
        parsed = tomllib.loads(pyproject)
    except (tomllib.TOMLDecodeError, ValueError):
        return None
    for path in (("project", "name"), ("tool", "poetry", "name")):
        cursor: Any = parsed
        for key in path:
            cursor = cursor.get(key, {}) if isinstance(cursor, dict) else {}
        if isinstance(cursor, str) and cursor.strip():
            return cursor.strip()
    return None


class RepositoryReader:
    """Read one repository's tree and manifests over the API."""

    def __init__(self, github: GitHubClient, *, timeout: float = 30.0) -> None:
        self.github = github
        self.raw = httpx.Client(
            base_url=RAW,
            timeout=timeout,
            follow_redirects=True,
            headers={"User-Agent": "oss-das-research"},
        )

    def close(self) -> None:
        self.raw.close()

    def __enter__(self) -> RepositoryReader:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def tree(self, repository: str, ref: str) -> tuple[list[str], bool]:
        """Every blob path in one repository, and whether the listing was cut.

        GitHub truncates a tree past 100k entries or 7MB. A truncated listing
        can silently omit a manifest, so the flag is recorded rather than
        dropped: a repository measured from a partial tree is a repository
        whose zero edges mean nothing.
        """
        payload = self.github.get_json(
            f"/repos/{repository}/git/trees/{ref}", params={"recursive": "1"}
        )
        paths = [
            str(item.get("path", ""))
            for item in payload.get("tree", [])
            if item.get("type") == "blob"
        ]
        return paths, bool(payload.get("truncated"))

    def blob(self, repository: str, ref: str, path: str) -> str:
        response = self.raw.get(f"/{repository}/{ref}/{path}")
        if response.status_code != 200:
            raise SourceError(f"{response.status_code} for {repository}/{path}")
        return response.text


def dependency_record(
    repository: str, ref: str, reader: RepositoryReader
) -> dict[str, Any]:
    """One repository's declared dependencies, read over the API.

    The record mirrors ``measure.dependency_record``'s shape so the same
    readers work on both, minus the fields that need a clone.
    """
    record: dict[str, Any] = {
        "repository": repository,
        "ref": ref,
        "manifests": [],
        "distribution": None,
        "tree_truncated": False,
        "declared": {},
        "error": "",
        "missing": {},
    }
    try:
        paths, truncated = reader.tree(repository, ref)
    except READ_FAILURES as error:
        record["missing"] = {"declared": "fetch_error"}
        record["error"] = str(error)
        return record

    record["tree_truncated"] = truncated
    manifests = manifest_paths(paths)
    record["manifests"] = manifests
    if not manifests:
        # Not an error: a repository with no manifest declares nothing, and
        # that is the measurement. It is excluded at figure time, not here.
        return record

    declared: dict[str, str] = {}
    for path in manifests:
        try:
            text = reader.blob(repository, ref, path)
        except READ_FAILURES as error:
            record["error"] = str(error)
            continue
        if path == "pyproject.toml" and record["distribution"] is None:
            record["distribution"] = distribution_name(text)
        for name, kind in declared_dependencies(text, path):
            if not TOOLING.match(name):
                _strongest(declared, name.lower(), kind)
    record["declared"] = dict(sorted(declared.items()))
    assert all(kind in DEPENDENCY_KINDS for kind in declared.values())
    return record
