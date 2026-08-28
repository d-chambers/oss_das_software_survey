#!/usr/bin/env python3
"""Mirror every curated repository into a bare clone.

Reads:  data/curated/*.md
Writes: data/repos/<id>.git (gitignored), data/measured/mirror/<id>.md

An existing mirror is left alone unless ``--update`` is passed, in which case
it is fetched. Every curated project gets a mirror record whatever its
status; a project with no repository gets one saying so. Exits non-zero when
any clone or fetch failed, because a partial set of mirrors that exited zero
would be measured downstream as a complete one.
"""

from __future__ import annotations

import argparse
import sys
from concurrent.futures import ThreadPoolExecutor

from oss_das.core import PATHS
from oss_das.measure import GIB, mirror_record, select_projects, write_measured


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--only", nargs="+", default=None, help="Restrict to these ids."
    )
    parser.add_argument("--jobs", type=int, default=4, help="Concurrent clones.")
    parser.add_argument("--timeout", type=int, default=1800, help="Per-repo seconds.")
    parser.add_argument(
        "--min-free-gb",
        type=float,
        default=20.0,
        help="Do not start a fresh clone below this much free space.",
    )
    parser.add_argument(
        "--update", action="store_true", help="Fetch mirrors that already exist."
    )
    args = parser.parse_args()

    projects = select_projects(args.only)
    print(f"mirroring {len(projects)} projects into {PATHS.repos}", file=sys.stderr)

    def run(project):
        return mirror_record(
            project,
            PATHS.repos,
            update=args.update,
            timeout=args.timeout,
            min_free_gb=args.min_free_gb,
        )

    records = []
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        for record in pool.map(run, projects):
            write_measured("mirror", record, PATHS.measured("mirror"))
            records.append(record)
            detail = record["error"] if record["result"] == "failed" else ""
            print(f"  {record['result']:<14} {record['id']} {detail}", file=sys.stderr)

    counts = {}
    for record in records:
        counts[record["result"]] = counts.get(record["result"], 0) + 1
    disk = sum(record["repo_bytes"] or 0 for record in records) / GIB
    summary = ", ".join(f"{count} {result}" for result, count in sorted(counts.items()))
    print(f"{summary}; {disk:.1f} GiB of mirrors", file=sys.stderr)
    return 1 if counts.get("failed") else 0


if __name__ == "__main__":
    raise SystemExit(main())
