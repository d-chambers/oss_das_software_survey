#!/usr/bin/env python3
"""Collect point-in-time repository and maintenance signals from every host."""

from __future__ import annotations

import contextlib
import os

from oss_das.cli import require_existing, resolve_snapshot_date, snapshot_parser
from oss_das.collection import collect_repositories, open_forges
from oss_das.core import PATHS, load_projects, write_jsonl


def main() -> None:
    args = snapshot_parser(__doc__).parse_args()
    snapshot_date = resolve_snapshot_date(args.snapshot_date)
    output = PATHS.raw(snapshot_date) / "github.jsonl"
    if require_existing(output, offline=args.offline):
        return
    if output.exists() and not args.force:
        raise FileExistsError(f"output exists; pass --force to replace: {output}")
    with contextlib.ExitStack() as stack:
        forges = [
            stack.enter_context(forge)
            for forge in open_forges(os.getenv("GITHUB_TOKEN"))
        ]
        records = collect_repositories(forges, load_projects())
    write_jsonl(output, records)


if __name__ == "__main__":
    main()
