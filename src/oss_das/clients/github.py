"""GitHub repository discovery and metadata collection."""

from __future__ import annotations

import re
from collections.abc import Iterator
from typing import Any

import httpx

from oss_das.clients.base import JsonClient, NotFoundError, SourceError
from oss_das.clients.forge import SearchResult, candidate, path_signals
from oss_das.models import ForgeKind

#: GitHub refuses to serve past the thousandth search result regardless of
#: paging, so a query broader than this cannot be collected exhaustively.
SEARCH_RESULT_LIMIT = 1000


class GitHubClient(JsonClient):
    kind = ForgeKind.GITHUB

    def __init__(
        self,
        token: str | None = None,
        *,
        host: str = "github.com",
        client: httpx.Client | None = None,
    ) -> None:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "oss-das-research",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self.host = host
        super().__init__(
            base_url="https://api.github.com", headers=headers, client=client
        )

    def paginate(
        self, path: str, *, params: dict[str, str | int] | None = None
    ) -> Iterator[dict[str, Any]]:
        request_params = {"per_page": 100, **(params or {})}
        next_path: str | None = path
        while next_path:
            response = self.get_response(next_path, params=request_params)
            payload = response.json()
            if not isinstance(payload, list):
                raise TypeError(f"expected a list from {response.url}")
            yield from payload
            next_path = response.links.get("next", {}).get("url")
            request_params = None

    def _candidate(self, item: dict[str, Any]) -> dict[str, Any]:
        return candidate(
            kind=self.kind,
            host=self.host,
            repository=item["full_name"],
            name=item["name"],
            description=item.get("description"),
            html_url=item["html_url"],
            stars=item.get("stargazers_count"),
            language=item.get("language"),
        )

    def search_repositories(self, query: str) -> SearchResult:
        """Page through a search and report how many hits GitHub claims to hold.

        A single page caps at 100, so the previous one-request search silently
        truncated the broadest query in this study to its first 100 of several
        hundred matches. Paging fixes that, and returning ``total_count``
        alongside makes the remaining cap visible instead of invisible.
        """
        items: list[dict[str, Any]] = []
        total = 0
        for page in range(1, SEARCH_RESULT_LIMIT // 100 + 1):
            payload = self.get_json(
                "/search/repositories",
                params={"q": query, "per_page": 100, "page": page},
            )
            total = payload.get("total_count", 0)
            batch = payload.get("items", [])
            items.extend(batch)
            if len(batch) < 100 or len(items) >= min(total, SEARCH_RESULT_LIMIT):
                break
        return SearchResult(
            [self._candidate(item) for item in items], total, total > len(items)
        )

    def list_namespace_repositories(self, namespace: str) -> list[dict[str, Any]]:
        """List an owner's repositories, whether it is an org or a user account.

        GitHub serves the two under different paths and 404s the wrong one, so
        an absent organization is a routine result here rather than an error.
        """
        try:
            items = list(self.paginate(f"/orgs/{namespace}/repos"))
        except NotFoundError:
            items = list(self.paginate(f"/users/{namespace}/repos"))
        return [self._candidate(item) for item in items]

    def repository(self, repository: str) -> dict[str, Any]:
        return self._candidate(self.get_json(f"/repos/{repository}"))

    def readme(self, repository: str) -> str:
        """One request, whatever the README is called; GitHub resolves the name."""
        response = self.get_response(
            f"/repos/{repository}/readme",
            headers={"Accept": "application/vnd.github.raw+json"},
        )
        return response.text

    def commit_activity(self, repository: str) -> dict[str, Any]:
        """Total commits and the date of the newest one.

        GitHub publishes no commit count, so the total is read from the
        pagination header of a one-per-page listing: the last page number is
        the commit count. An empty repository has neither.
        """
        response = self.get_response(
            f"/repos/{repository}/commits", params={"per_page": 1}
        )
        payload = response.json()
        if not isinstance(payload, list) or not payload:
            return {"commits": None, "commits_missing_reason": "not_published"}
        last = response.links.get("last", {}).get("url", "")
        match = re.search(r"[?&]page=(\d+)", last)
        return {
            "commits": int(match.group(1)) if match else len(payload),
            "commits_missing_reason": None,
            "last_commit_at": payload[0]
            .get("commit", {})
            .get("committer", {})
            .get("date"),
        }

    def collect_repository(self, repository: str) -> dict[str, Any]:
        repo = self.get_json(f"/repos/{repository}")
        contributors = list(self.paginate(f"/repos/{repository}/contributors"))
        releases = list(self.paginate(f"/repos/{repository}/releases"))
        tree = self.get_json(
            f"/repos/{repository}/git/trees/{repo['default_branch']}",
            params={"recursive": "1"},
        )
        paths = [str(item.get("path", "")) for item in tree.get("tree", [])]
        non_bot_contributors = [
            item
            for item in contributors
            if item.get("type") != "Bot"
            and not str(item.get("login", "")).endswith("[bot]")
        ]
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
            "repository": repository,
            "github_id": repo["id"],
            "html_url": repo["html_url"],
            "description": repo.get("description"),
            "stars": repo["stargazers_count"],
            "forks": repo["forks_count"],
            "contributors": len(non_bot_contributors),
            "contributors_basis": "linked accounts, bots removed",
            "created_at": repo["created_at"],
            "pushed_at": repo.get("pushed_at"),
            "archived": repo["archived"],
            # Collection runs authenticated, so a private repository answers
            # normally and would otherwise be catalogued as public software.
            "visibility": "private" if repo.get("private") else "public",
            "language": repo.get("language"),
            "license_detected": (repo.get("license") or {}).get("spdx_id"),
            "license_detected_vocabulary": "spdx",
            "release_count": len(published),
            "latest_release_at": latest,
            **path_signals(paths, self.kind),
            "tree_truncated": bool(tree.get("truncated")),
            "source_url": f"https://api.github.com/repos/{repository}",
        }
        record["language_bytes"] = self._language_bytes(repository)
        try:
            record.update(self.commit_activity(repository))
        except SourceError as error:
            record.update(
                commits=None,
                commits_missing_reason="unavailable",
                commits_error=str(error),
            )
        return record

    def _language_bytes(self, repository: str) -> dict[str, int]:
        try:
            payload = self.get_json(f"/repos/{repository}/languages")
        except SourceError:
            return {}
        return payload if isinstance(payload, dict) else {}
