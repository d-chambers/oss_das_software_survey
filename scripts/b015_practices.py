#!/usr/bin/env python3
"""Record which engineering practices each mirrored repository shows.

Reads:  data/curated/*.md, data/repos/<id>.git
Writes: data/measured/practices/<id>.md

No network. The tip tree of each mirror is matched against
``oss_das.measure.PRACTICE_RULES`` -- tests, CI, documentation, packaging and
the rest -- and the file that matched is kept beside the verdict, so a wrong
call can be checked rather than believed. Every curated project gets a record:
one with no repository says ``not_applicable``, one whose mirror b010 could not
make says ``unavailable``.
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter

from oss_das.core import PATHS
from oss_das.measure import (
    PRACTICE_RULES,
    practices_record,
    select_projects,
    write_measured,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--only", nargs="+", default=None, help="Restrict to these ids."
    )
    parser.add_argument("--timeout", type=int, default=900, help="Per-repo seconds.")
    args = parser.parse_args()

    projects = select_projects(args.only)
    print(f"scanning {len(projects)} projects in {PATHS.repos}", file=sys.stderr)
    totals: Counter[str] = Counter()
    scanned = 0
    for project in projects:
        record = practices_record(project, PATHS.repos, timeout=args.timeout)
        write_measured("practices", record, PATHS.measured("practices"))
        reason = record["missing"].get("practices")
        if reason:
            print(f"  {reason:<14} {project.id} {record['error']}", file=sys.stderr)
            continue
        scanned += 1
        totals.update(name for name, has in record["practices"].items() if has)
        kept = ", ".join(sorted(record["evidence"]))
        print(
            f"  {project.id:<26} {len(record['evidence']):>2}  {kept}", file=sys.stderr
        )

    print(f"\n{scanned} repositories scanned", file=sys.stderr)
    for name, _ in PRACTICE_RULES:
        count = totals[name]
        share = count / scanned * 100 if scanned else 0.0
        print(f"  {name:<14} {count:>3}  {share:5.1f}%", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
