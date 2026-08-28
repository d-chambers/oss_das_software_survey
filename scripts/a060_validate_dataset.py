#!/usr/bin/env python3
"""Validate schema, identity, missingness, and checksums for a snapshot."""

from __future__ import annotations

from oss_das.cli import resolve_snapshot_date, snapshot_parser
from oss_das.dataset import validate_snapshot


def main() -> None:
    args = snapshot_parser(__doc__).parse_args()
    snapshot_date = resolve_snapshot_date(args.snapshot_date, prefer_latest=True)
    validate_snapshot(snapshot_date)
    print(f"validated snapshot {snapshot_date}")


if __name__ == "__main__":
    main()
