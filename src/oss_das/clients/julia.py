"""Julia General registry membership lookups.

Julia has no download API comparable to PyPI Stats, so the only public,
verifiable claim about a Julia package is whether the General registry
actually carries it. The catalog previously asserted registry names that
nobody checked; this client turns that assertion into a recorded observation.
"""

from __future__ import annotations

from typing import Any

import httpx

from oss_das.clients.base import JsonClient, NotFoundError

#: The General registry's package directories are one level under a
#: single-letter shard, so ``Dascore`` lives at ``D/Dascore``.
REGISTRY_REPOSITORY = "JuliaRegistries/General"


class JuliaRegistryClient(JsonClient):
    """Read the General registry tree through GitHub's contents API."""

    def __init__(
        self, token: str | None = None, *, client: httpx.Client | None = None
    ) -> None:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "oss-das-research",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        super().__init__(
            base_url="https://api.github.com", headers=headers, client=client
        )

    def package(self, name: str) -> dict[str, Any]:
        """Confirm one package is registered, or raise NotFoundError.

        A registered package always has a ``Package.toml``; a directory that
        merely shares a name prefix does not, so the file is what is probed.
        """
        path = f"{name[0].upper()}/{name}/Package.toml"
        source_url = (
            f"https://api.github.com/repos/{REGISTRY_REPOSITORY}/contents/{path}"
        )
        entry = self.get_json(f"/repos/{REGISTRY_REPOSITORY}/contents/{path}")
        if not isinstance(entry, dict) or entry.get("type") != "file":
            raise NotFoundError(source_url)
        return {
            "name": name,
            "registered": True,
            "registry": REGISTRY_REPOSITORY,
            "registry_url": f"https://github.com/{REGISTRY_REPOSITORY}/tree/master/{name[0].upper()}/{name}",
            "source_url": source_url,
        }
