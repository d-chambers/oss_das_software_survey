#!/usr/bin/env python3
"""Build normalized public CSV files from curated and collected records."""

from __future__ import annotations

from oss_das.cli import resolve_snapshot_date, snapshot_parser
from oss_das.dataset import build_snapshot


def main() -> None:
    args = snapshot_parser(__doc__).parse_args()
    snapshot_date = resolve_snapshot_date(args.snapshot_date, prefer_latest=True)
    build_snapshot(snapshot_date)


if __name__ == "__main__":
    main()
