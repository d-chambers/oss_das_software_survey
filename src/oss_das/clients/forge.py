"""Shared shape for the code hosts this census reads.

GitHub, GitLab, and Gitea answer different URLs with different field names,
but the census asks all three the same questions. Normalizing here means a
project hosted on an institutional GitLab appears in the dataset on exactly
the same terms as one on GitHub, rather than being quietly unreportable.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any, NamedTuple, Protocol

from oss_das.models import ForgeKind

#: Path prefixes that count as published documentation, on any host.
DOC_PREFIXES = ("docs/", "documentation/", "doc/")

#: README filenames tried, in order, on hosts that cannot resolve the name.
README_NAMES = ("README.md", "README.rst", "README.txt", "README", "readme.md")

#: Path prefixes that count as a test suite, on any host.
TEST_PREFIXES = ("tests/", "test/")

#: Where each host keeps its pipeline definitions. A GitLab project stores CI
#: in a single top-level file, so probing for GitHub's directory alone would
#: report every GitLab project as having no CI at all.
CI_PATHS: dict[ForgeKind, tuple[str, ...]] = {
    ForgeKind.GITHUB: (".github/workflows/",),
    ForgeKind.GITLAB: (".gitlab-ci.yml", ".gitlab/workflows/", ".gitlab-ci.yaml"),
    ForgeKind.GITEA: (".gitea/workflows/", ".woodpecker/", ".woodpecker.yml"),
}


class SearchResult(NamedTuple):
    """One search probe's hits and what is known about their completeness."""

    #: Normalized candidates the host actually served.
    hits: list[dict[str, Any]]
    #: Matches the host claims exist, or None when it publishes no count.
    reported_total: int | None
    #: True when hits are known to be a partial answer, False when known
    #: complete, None when the host gave no basis to tell.
    truncated: bool | None


class ForgeClient(Protocol):
    """What every code-host client must be able to answer."""

    kind: ForgeKind
    host: str

    def search_repositories(self, query: str) -> SearchResult:
        """Return matching candidates plus what the host said about coverage.

        Truncation is reported explicitly rather than inferred, because the
        hosts differ in what they will admit: GitHub publishes a match total,
        while GitLab and Gitea publish none, so "no total" has to stay
        distinguishable from "this list is complete".
        """

    def list_namespace_repositories(self, namespace: str) -> list[dict[str, Any]]:
        """Return normalized candidates for every repository under one owner."""

    def collect_repository(self, repository: str) -> dict[str, Any]:
        """Return one normalized point-in-time record for a single repository."""

    def repository(self, repository: str) -> dict[str, Any]:
        """Return one repository as a normalized candidate, or raise SourceError."""

    def readme(self, repository: str) -> str:
        """Return the README text, or raise SourceError when the host has none."""


def _matches(path: str, patterns: Iterable[str]) -> bool:
    return any(
        path.startswith(pattern) if pattern.endswith("/") else path == pattern
        for pattern in patterns
    )


def path_signals(paths: Iterable[str], kind: ForgeKind) -> dict[str, Any]:
    """Report which maintenance artifacts exist in a repository tree.

    These checks establish that a file is present, never that it is any good;
    the evidence path is recorded so a reader can judge the claim instead of
    trusting the boolean.
    """
    lowered = [str(path).lower() for path in paths]
    groups = {
        "docs": DOC_PREFIXES,
        "tests": TEST_PREFIXES,
        "ci": CI_PATHS[kind],
    }
    evidence = {
        name: next((path for path in lowered if _matches(path, patterns)), None)
        for name, patterns in groups.items()
    }
    return {
        "has_docs": evidence["docs"] is not None,
        "has_tests": evidence["tests"] is not None,
        "has_ci": evidence["ci"] is not None,
        "signal_evidence": evidence,
    }


def candidate(
    *,
    kind: ForgeKind,
    host: str,
    repository: str,
    name: str,
    description: str | None,
    html_url: str,
    stars: int | None,
    language: str | None = None,
) -> dict[str, Any]:
    """Build the one candidate shape that discovery works with."""
    return {
        "forge_kind": kind.value,
        "forge_host": host,
        "repository": repository,
        "name": name,
        "description": description,
        "html_url": html_url,
        "stars_at_discovery": stars,
        "language": language,
    }
