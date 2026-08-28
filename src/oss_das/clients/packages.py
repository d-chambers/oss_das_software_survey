"""Package-registry clients and response normalization."""

from __future__ import annotations

from typing import Any

import httpx

from oss_das.clients.base import JsonClient

#: The JSON flavour of the PEP 691 simple index: every project name, one request.
SIMPLE_INDEX_ACCEPT = "application/vnd.pypi.simple.v1+json"


class PyPIClient(JsonClient):
    def __init__(
        self, *, client: httpx.Client | None = None, min_interval: float = 0
    ) -> None:
        super().__init__(
            base_url="https://pypi.org", client=client, min_interval=min_interval
        )

    def index_names(self) -> list[str]:
        """Every project name PyPI serves, from the simple index."""
        payload = self.get_json("/simple/", headers={"Accept": SIMPLE_INDEX_ACCEPT})
        return [str(item["name"]) for item in payload.get("projects", [])]

    def metadata(self, name: str) -> dict[str, Any]:
        """The full JSON API payload: ``info`` plus ``releases``."""
        return self.get_json(f"/pypi/{name}/json")

    def package(self, name: str) -> dict[str, Any]:
        payload = self.get_json(f"/pypi/{name}/json")
        info = payload["info"]
        releases = payload.get("releases", {})
        upload_dates = [
            file.get("upload_time_iso_8601")
            for files in releases.values()
            for file in files
            if file.get("upload_time_iso_8601")
        ]
        return {
            "name": info["name"],
            "version": info["version"],
            "requires_python": info.get("requires_python"),
            "release_count": len(releases),
            "latest_upload_at": max(upload_dates, default=None),
            "project_url": info.get("project_url"),
            # Preserve the distribution metadata rather than flattening it to
            # a prose summary: it is the evidence for dependency edges.
            "requires_dist": info.get("requires_dist") or [],
            "source_url": f"https://pypi.org/pypi/{name}/json",
        }


class PyPIStatsClient(JsonClient):
    """PyPI Stats throttles bursts aggressively, so pace and retry patiently.

    Callers pass ``min_interval=0`` when driving the client from a test
    transport; the defaults describe what the live service tolerates.
    """

    def __init__(
        self,
        *,
        client: httpx.Client | None = None,
        min_interval: float = 6.0,
        max_attempts: int = 5,
        backoff: float = 20.0,
    ) -> None:
        super().__init__(
            base_url="https://pypistats.org",
            client=client,
            min_interval=min_interval,
            max_attempts=max_attempts,
            backoff=backoff,
        )

    def package(self, name: str) -> tuple[dict[str, int], list[dict[str, Any]]]:
        recent = self.get_json(f"/api/packages/{name}/recent")["data"]
        overall = self.get_json(
            f"/api/packages/{name}/overall", params={"mirrors": "false"}
        )["data"]
        daily = [
            item
            for item in overall
            if item.get("category") in {None, "without_mirrors"}
        ]
        return recent, daily


class CondaForgeChannelClient(JsonClient):
    """The conda-forge channel index, which carries a summary per package."""

    def __init__(self, *, client: httpx.Client | None = None) -> None:
        super().__init__(base_url="https://conda.anaconda.org", client=client)

    def channeldata(self) -> dict[str, dict[str, Any]]:
        payload = self.get_json("/conda-forge/channeldata.json")
        packages = payload.get("packages")
        if not isinstance(packages, dict):
            raise TypeError("channeldata.json has no 'packages' mapping")
        return packages


class CondaClient(JsonClient):
    def __init__(self, *, client: httpx.Client | None = None) -> None:
        super().__init__(base_url="https://api.anaconda.org", client=client)

    def package(self, channel: str, name: str) -> dict[str, Any]:
        payload = self.get_json(f"/package/{channel}/{name}")
        artifacts = [
            {
                "version": item.get("version"),
                "basename": item.get("basename"),
                "downloads": item.get("ndownloads"),
            }
            for item in payload.get("files", [])
        ]
        counts = [
            item["downloads"] for item in artifacts if item["downloads"] is not None
        ]
        return {
            "channel": channel,
            "name": payload.get("name", name),
            "latest_version": payload.get("latest_version"),
            "downloads_cumulative": sum(counts) if counts else None,
            "artifacts": artifacts,
            "source_url": f"https://api.anaconda.org/package/{channel}/{name}",
        }
