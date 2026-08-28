#!/usr/bin/env python3
"""Discover public DAS repositories across code hosts without changing curation."""

from __future__ import annotations

import contextlib
import os

from oss_das.cli import require_existing, resolve_snapshot_date, snapshot_parser
from oss_das.collection import discover_projects, open_forges
from oss_das.core import PATHS, load_projects, write_csv, write_jsonl

FIELDS = [
    "repository",
    "forge_kind",
    "forge_host",
    "name",
    "description",
    "html_url",
    "language",
    "stars_at_discovery",
    "probes",
    "probe_class",
    "source",
    "fetched_at",
    "catalog_id",
    "catalog_status",
    "decision_reason",
]

COVERAGE_FIELDS = [
    "host",
    "kind",
    "probe",
    "query",
    "status",
    "reported_total",
    "retrieved",
    "truncated",
    "specific",
    "error",
    "fetched_at",
]


def main() -> None:
    args = snapshot_parser(__doc__).parse_args()
    snapshot_date = resolve_snapshot_date(args.snapshot_date)
    output = PATHS.snapshot(snapshot_date) / "candidates.csv"
    coverage_output = PATHS.snapshot(snapshot_date) / "discovery_coverage.csv"
    if require_existing(output, offline=args.offline):
        return
    if output.exists() and not args.force:
        raise FileExistsError(f"output exists; pass --force to replace: {output}")
    with contextlib.ExitStack() as stack:
        forges = [
            stack.enter_context(forge)
            for forge in open_forges(os.getenv("GITHUB_TOKEN"))
        ]
        records, coverage = discover_projects(forges, load_projects())
    write_jsonl(PATHS.raw(snapshot_date) / "discovery.jsonl", records)
    write_jsonl(PATHS.raw(snapshot_date) / "discovery_coverage.jsonl", coverage)
    write_csv(output, records, FIELDS)
    write_csv(coverage_output, coverage, COVERAGE_FIELDS)
    for entry in coverage:
        if entry.get("status") != "ok":
            print(f"discovery {entry['status']}: {entry['host']} {entry['query']}")
        elif entry.get("truncated"):
            print(
                f"discovery truncated: {entry['host']} {entry['query']} "
                f"({entry['retrieved']} of {entry['reported_total']})"
            )


if __name__ == "__main__":
    main()
