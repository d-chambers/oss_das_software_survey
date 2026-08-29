#!/usr/bin/env python3
"""Record what each mirrored project is built on, from manifests and imports.

Reads:  data/curated/*.md, data/repos/<id>.git
Writes: data/measured/dependencies/<id>.md

No network. Every manifest the repository carries is parsed, and every Python
file it ships is read for its imports, because a manifest is a promise and an
import is a fact: twenty catalogued projects declare no manifest at all, and
reading manifests alone recorded working code as depending on nothing. Names
are classified required, optional, or development, and the strongest evidence
for a name wins.
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter

from oss_das.core import PATHS
from oss_das.measure import (
    DEPENDENCY_KINDS,
    dependency_record,
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
    print(f"reading {len(projects)} projects from {PATHS.repos}", file=sys.stderr)
    popular: Counter[str] = Counter()
    scanned = python = 0
    for project in projects:
        record = dependency_record(project, PATHS.repos, timeout=args.timeout)
        write_measured("dependencies", record, PATHS.measured("dependencies"))
        reason = record["missing"].get("dependencies")
        if reason:
            print(f"  {reason:<14} {project.id} {record['error']}", file=sys.stderr)
            continue
        scanned += 1
        python += bool(record["has_python"])
        counts = {kind: len(record[kind]) for kind in DEPENDENCY_KINDS}
        popular.update(record["required"] + record["optional"])
        print(
            f"  {project.id:<26} "
            + "  ".join(f"{kind[:3]} {n:>3}" for kind, n in counts.items())
            + ("" if record["has_python"] else "   (no python)"),
            file=sys.stderr,
        )

    print(f"\n{scanned} projects read, {python} of them with Python", file=sys.stderr)
    for name, count in popular.most_common(15):
        print(f"  {name:<18} {count:>3}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
