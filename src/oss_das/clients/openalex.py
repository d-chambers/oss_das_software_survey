"""OpenAlex DOI and citation-count client."""

from __future__ import annotations

from urllib.parse import quote

import httpx

from oss_das.clients.base import JsonClient


class OpenAlexClient(JsonClient):
    def __init__(
        self, api_key: str | None = None, *, client: httpx.Client | None = None
    ) -> None:
        params = {"api_key": api_key} if api_key else None
        super().__init__(
            base_url="https://api.openalex.org", params=params, client=client
        )

    def work_by_doi(self, doi: str) -> dict[str, object]:
        normalized = doi.lower().removeprefix("https://doi.org/")
        source_url = f"https://api.openalex.org/works/https://doi.org/{normalized}"
        payload = self.get_json(
            f"/works/{quote(f'https://doi.org/{normalized}', safe='')}"
        )
        return {
            "doi": normalized,
            "title": payload.get("display_name"),
            "publication_year": payload.get("publication_year"),
            "work_type": payload.get("type"),
            "cited_by_count": payload.get("cited_by_count"),
            "openalex_id": payload.get("id"),
            "source_url": source_url,
        }
