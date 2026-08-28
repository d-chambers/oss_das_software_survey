"""GitLab discovery and metadata collection for any instance.

The same client serves gitlab.com and self-hosted institutional instances,
because the DAS ecosystem does not live on one host: GEOFON publishes
``dastools`` on the GFZ instance, and a census that only reads GitHub would
report that package as not existing.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any
from urllib.parse import quote

import httpx

from oss_das.clients.base import JsonClient, NotFoundError, SourceError
from oss_das.clients.forge import (
    README_NAMES,
    SearchResult,
    candidate,
    path_signals,
)
from oss_das.models import ForgeKind

#: How many search hits to walk before giving up on a query. A short acronym
#: matches tens of thousands of unrelated projects on a large instance, and
#: paging all of them would spend hours to review noise. The cap is recorded
#: with the results so a hit list that stopped early is never read as the
#: complete answer.
SEARCH_RESULT_LIMIT = 300


class GitLabClient(JsonClient):
    kind = ForgeKind.GITLAB

    def __init__(
        self,
        host: str = "gitlab.com",
        token: str | None = None,
        *,
        client: httpx.Client | None = None,
    ) -> None:
        headers = {"User-Agent": "oss-das-research"}
        if token:
            headers["PRIVATE-TOKEN"] = token
        self.host = host
        super().__init__(
            base_url=f"https://{host}/api/v4", headers=headers, client=client
        )

    @staticmethod
    def _encode(repository: str) -> str:
        """URL-encode a namespace path, which GitLab uses as a project id."""
        return quote(repository, safe="")

    def paginate(
        self,
        path: str,
        *,
        params: dict[str, str | int] | None = None,
        limit: int | None = None,
    ) -> Iterator[dict[str, Any]]:
        request_params: dict[str, str | int] = {"per_page": 100, **(params or {})}
        page = 1
        seen = 0
        while True:
            payload = self.get_json(path, params={**request_params, "page": page})
            if not isinstance(payload, list):
                raise TypeError(f"expected a list from {self.base_url}{path}")
            for item in payload:
                yield item
                seen += 1
                if limit is not None and seen >= limit:
                    return
            if len(payload) < 100:
                return
            page += 1

    def _candidate(self, item: dict[str, Any]) -> dict[str, Any]:
        return candidate(
            kind=self.kind,
            host=self.host,
            repository=item["path_with_namespace"],
            name=item["name"],
            description=item.get("description"),
            html_url=item["web_url"],
            stars=item.get("star_count"),
        )

    def search_repositories(self, query: str) -> SearchResult:
        """Search public projects by name and description.

        Unauthenticated GitLab exposes no full-text search over README
        content, so this asks a strictly narrower question than the GitHub
        search beside it. It also reports no match total, so a result set that
        filled the cap is reported as truncated at the cap; anything shorter
        is genuinely everything the host had.
        """
        items = list(
            self.paginate(
                "/projects",
                params={"search": query, "visibility": "public", "order_by": "id"},
                limit=SEARCH_RESULT_LIMIT,
            )
        )
        return SearchResult(
            [self._candidate(item) for item in items],
            None,
            len(items) >= SEARCH_RESULT_LIMIT,
        )

    def list_namespace_repositories(self, namespace: str) -> list[dict[str, Any]]:
        items = self.paginate(f"/groups/{self._encode(namespace)}/projects")
        return [self._candidate(item) for item in items]

    def repository(self, repository: str) -> dict[str, Any]:
        return self._candidate(self.get_json(f"/projects/{self._encode(repository)}"))

    def readme(self, repository: str) -> str:
        """Try the usual README names against the default branch."""
        project = self._encode(repository)
        for name in README_NAMES:
            try:
                response = self.get_response(
                    f"/projects/{project}/repository/files/{quote(name, safe='')}/raw",
                    params={"ref": "HEAD"},
                )
            except NotFoundError:
                continue
            return response.text
        raise NotFoundError(f"{self.host}/{repository}: no README")

    def collect_repository(self, repository: str) -> dict[str, Any]:
        project = self._encode(repository)
        repo = self.get_json(f"/projects/{project}", params={"license": "true"})
        releases = list(self.paginate(f"/projects/{project}/releases"))
        paths = [
            str(item.get("path", ""))
            for item in self.paginate(
                f"/projects/{project}/repository/tree",
                params={"recursive": "true", "ref": repo.get("default_branch", "")},
            )
        ]
        latest = max(
            (item.get("released_at") for item in releases if item.get("released_at")),
            default=None,
        )
        record: dict[str, Any] = {
            "forge_kind": self.kind.value,
            "forge_host": self.host,
            "repository": repo["path_with_namespace"],
            "gitlab_id": repo["id"],
            "html_url": repo["web_url"],
            "description": repo.get("description"),
            "stars": repo.get("star_count"),
            "forks": repo.get("forks_count"),
            "created_at": repo.get("created_at"),
            # GitLab has no pushed_at; last_activity_at is the nearest public
            # equivalent and also moves on issue and merge-request activity.
            "pushed_at": repo.get("last_activity_at"),
            "archived": bool(repo.get("archived")),
            "visibility": repo.get("visibility", "public"),
            "language": self._primary_language(project),
            # GitLab reports its own license keys ("gpl-3.0+"), which resemble
            # SPDX identifiers without being them, so the vocabulary travels
            # with the value rather than being assumed by whoever reads it.
            "license_detected": (repo.get("license") or {}).get("key"),
            "license_detected_vocabulary": "gitlab-license-key",
            "release_count": len(releases),
            "latest_release_at": latest,
            **path_signals(paths, self.kind),
            "tree_truncated": False,
            "source_url": f"https://{self.host}/api/v4/projects/{project}",
        }
        record.update(self._contributors(project))
        record.update(self._commit_activity(project))
        # GitLab reports language shares as percentages, not bytes, so there is
        # nothing here to turn into a size estimate.
        record["language_bytes"] = {}
        return record

    def _commit_activity(self, project: str) -> dict[str, Any]:
        """Commit total from the pagination header, plus the newest commit date."""
        try:
            response = self.get_response(
                f"/projects/{project}/repository/commits", params={"per_page": 1}
            )
            payload = response.json()
        except (SourceError, ValueError) as error:
            return {
                "commits": None,
                "commits_missing_reason": "unavailable",
                "commits_error": str(error),
            }
        if not isinstance(payload, list) or not payload:
            return {"commits": None, "commits_missing_reason": "not_published"}
        total = response.headers.get("x-total")
        return {
            "commits": int(total) if total and total.isdigit() else None,
            "commits_missing_reason": None if total else "unavailable",
            "last_commit_at": payload[0].get("committed_date"),
        }

    def _primary_language(self, project: str) -> str | None:
        """Return the largest language by share, or None when none is reported."""
        try:
            languages = self.get_json(f"/projects/{project}/languages")
        except (SourceError, TypeError):
            return None
        if not isinstance(languages, dict) or not languages:
            return None
        return max(languages, key=lambda name: languages[name])

    def _contributors(self, project: str) -> dict[str, Any]:
        """Count distinct contributors, reporting a reason when the list is closed.

        GitLab returns commit identities rather than accounts, so one person
        committing from two machines can appear twice. Names are deduplicated
        to soften that, and the basis is recorded because this count answers a
        slightly different question from GitHub's account-linked one. Some
        instances restrict the endpoint even for public projects; recording
        that as a reason keeps a locked-down host from looking like a project
        with no contributors.
        """
        basis = "distinct commit author names"
        try:
            people = list(self.paginate(f"/projects/{project}/repository/contributors"))
        except (SourceError, TypeError) as error:
            return {
                "contributors": None,
                "contributors_missing_reason": "unavailable",
                "contributors_error": str(error),
                "contributors_basis": basis,
            }
        names = {str(item.get("name", "")).strip().lower() for item in people}
        return {
            "contributors": len(names - {""}),
            "contributors_missing_reason": None,
            "contributors_basis": basis,
        }
