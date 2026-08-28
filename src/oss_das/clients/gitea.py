"""Gitea and Forgejo discovery and metadata collection for any instance.

Codeberg and the project-run forges that seismology groups host themselves
both speak this API. Searching them is mostly how this census can state that
it looked outside GitHub and GitLab, rather than assuming nothing is there.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import httpx

from oss_das.clients.base import JsonClient, NotFoundError, SourceError
from oss_das.clients.forge import (
    README_NAMES,
    SearchResult,
    candidate,
    path_signals,
)
from oss_das.models import ForgeKind

#: Matching cap per query, for the same reason GitLab has one: a short
#: acronym matches far more noise than any reviewer will read.
SEARCH_RESULT_LIMIT = 300


class GiteaClient(JsonClient):
    kind = ForgeKind.GITEA

    def __init__(
        self,
        host: str = "codeberg.org",
        token: str | None = None,
        *,
        client: httpx.Client | None = None,
    ) -> None:
        headers = {"User-Agent": "oss-das-research"}
        if token:
            headers["Authorization"] = f"token {token}"
        self.host = host
        super().__init__(
            base_url=f"https://{host}/api/v1", headers=headers, client=client
        )

    def paginate(
        self,
        path: str,
        *,
        params: dict[str, str | int] | None = None,
        key: str | None = None,
        limit: int | None = None,
    ) -> Iterator[dict[str, Any]]:
        page = 1
        seen = 0
        while True:
            payload = self.get_json(
                path, params={**(params or {}), "limit": 50, "page": page}
            )
            batch = (
                payload.get(key, []) if key and isinstance(payload, dict) else payload
            )
            if not isinstance(batch, list):
                raise TypeError(f"expected a list from {self.base_url}{path}")
            for item in batch:
                yield item
                seen += 1
                if limit is not None and seen >= limit:
                    return
            if len(batch) < 50:
                return
            page += 1

    def _candidate(self, item: dict[str, Any]) -> dict[str, Any]:
        return candidate(
            kind=self.kind,
            host=self.host,
            repository=item["full_name"],
            name=item["name"],
            description=item.get("description"),
            html_url=item["html_url"],
            stars=item.get("stars_count"),
            language=item.get("language"),
        )

    def search_repositories(self, query: str) -> SearchResult:
        """Search repository names and descriptions on this instance."""
        items = list(
            self.paginate(
                "/repos/search",
                params={"q": query},
                key="data",
                limit=SEARCH_RESULT_LIMIT,
            )
        )
        return SearchResult(
            [self._candidate(item) for item in items],
            None,
            len(items) >= SEARCH_RESULT_LIMIT,
        )

    def list_namespace_repositories(self, namespace: str) -> list[dict[str, Any]]:
        items = self.paginate(f"/orgs/{namespace}/repos")
        return [self._candidate(item) for item in items]

    def repository(self, repository: str) -> dict[str, Any]:
        return self._candidate(self.get_json(f"/repos/{repository}"))

    def readme(self, repository: str) -> str:
        """Try the usual README names; the raw endpoint serves the default branch."""
        for name in README_NAMES:
            try:
                response = self.get_response(f"/repos/{repository}/raw/{name}")
            except NotFoundError:
                continue
            return response.text
        raise NotFoundError(f"{self.host}/{repository}: no README")

    def collect_repository(self, repository: str) -> dict[str, Any]:
        repo = self.get_json(f"/repos/{repository}")
        releases = list(self.paginate(f"/repos/{repository}/releases"))
        tree = self.get_json(
            f"/repos/{repository}/git/trees/{repo['default_branch']}",
            params={"recursive": "1", "per_page": 1000},
        )
        paths = [str(item.get("path", "")) for item in tree.get("tree", [])]
        published = [item for item in releases if not item.get("draft")]
        latest = max(
            (
                item.get("published_at")
                for item in published
                if item.get("published_at")
            ),
            default=None,
        )
        record: dict[str, Any] = {
            "forge_kind": self.kind.value,
            "forge_host": self.host,
            "repository": repo["full_name"],
            "gitea_id": repo["id"],
            "html_url": repo["html_url"],
            "description": repo.get("description"),
            "stars": repo.get("stars_count"),
            "forks": repo.get("forks_count"),
            "created_at": repo.get("created_at"),
            "pushed_at": repo.get("updated_at"),
            "archived": bool(repo.get("archived")),
            "visibility": "private" if repo.get("private") else "public",
            "language": repo.get("language"),
            # Gitea's repository payload carries no license field at all, so
            # there is nothing to cross-check the curated license against.
            "license_detected": None,
            "license_detected_vocabulary": None,
            "license_detected_missing_reason": "not_published",
            "release_count": len(published),
            "latest_release_at": latest,
            **path_signals(paths, self.kind),
            "tree_truncated": bool(tree.get("truncated")),
            "source_url": f"https://{self.host}/api/v1/repos/{repository}",
        }
        record.update(self._contributors(repository))
        record["language_bytes"] = {}
        record["commits"] = None
        record["commits_missing_reason"] = "unavailable"
        return record

    def _contributors(self, repository: str) -> dict[str, Any]:
        """Count contributors where the instance offers them.

        The contributors endpoint arrived in later Gitea releases, so an older
        self-hosted forge answers 404. That is a gap in the source, not a
        project without contributors, and it is recorded as such.
        """
        basis = "linked accounts"
        try:
            people = list(self.paginate(f"/repos/{repository}/contributors"))
        except (SourceError, TypeError) as error:
            return {
                "contributors": None,
                "contributors_missing_reason": "unavailable",
                "contributors_error": str(error),
                "contributors_basis": basis,
            }
        return {
            "contributors": len(people),
            "contributors_missing_reason": None,
            "contributors_basis": basis,
        }
