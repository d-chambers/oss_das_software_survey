#!/usr/bin/env python3
"""Collect OpenAlex metadata and citation counts for curated publication DOIs."""

from __future__ import annotations

import os

from oss_das.cli import require_existing, resolve_snapshot_date, snapshot_parser
from oss_das.clients import OpenAlexClient
from oss_das.collection import collect_publications
from oss_das.core import PATHS, load_projects, write_jsonl


def main() -> None:
    args = snapshot_parser(__doc__).parse_args()
    snapshot_date = resolve_snapshot_date(args.snapshot_date)
    output = PATHS.raw(snapshot_date) / "publications.jsonl"
    if require_existing(output, offline=args.offline):
        return
    if output.exists() and not args.force:
        raise FileExistsError(f"output exists; pass --force to replace: {output}")
    with OpenAlexClient(os.getenv("OPENALEX_API_KEY")) as openalex:
        records = collect_publications(openalex, load_projects())
    write_jsonl(output, records)


if __name__ == "__main__":
    main()
