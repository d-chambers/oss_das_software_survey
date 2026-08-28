#!/usr/bin/env python3
"""Run collection, dataset, validation, and site stages in order."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot-date", required=True)
    parser.add_argument(
        "--collect", action="store_true", help="Refresh remote source snapshots."
    )
    parser.add_argument(
        "--offline", action="store_true", help="Require existing remote snapshots."
    )
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    if args.collect and args.offline:
        parser.error("--collect and --offline are mutually exclusive")

    scripts = Path(__file__).resolve().parent
    stages = []
    if args.collect or args.offline:
        # Offline runs still visit the collection stages so that a missing raw
        # source file fails loudly instead of silently rebuilding from nothing.
        stages.extend([10, 20, 30, 35, 40])
    stages.extend([50, 60, 80, 100, 110, 115, 120, 125, 130, 140, 150])
    for number in stages:
        path = next(scripts.glob(f"a{number:03d}_*.py"))
        command = [sys.executable, str(path), "--snapshot-date", args.snapshot_date]
        if args.offline and number < 50:
            command.append("--offline")
        if args.force:
            command.append("--force")
        subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
