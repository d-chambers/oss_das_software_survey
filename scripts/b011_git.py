#!/usr/bin/env python3
"""Measure commit history and lines of source from each bare mirror.

Reads:  data/curated/*.md, data/repos/<id>.git
Writes: data/commits/<id>.csv (overwritten), data/measured/git/<id>.md

No network. Every curated project gets a git record: one with no repository
says ``not_applicable``, one whose mirror b010 could not make says
``unavailable``. A project's commit CSV is written before its record and
removed when nothing was measured, so an old export can never sit beside a
fresh record. Exits non-zero when git failed on a mirror that exists.
"""

from __future__ import annotations

import argparse
import sys

from oss_das.core import PATHS
from oss_das.measure import (
    commit_rows,
    git_record,
    language_totals,
    mirror_path,
    select_projects,
    write_commits,
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
    print(f"measuring {len(projects)} projects from {PATHS.repos}", file=sys.stderr)
    records = []
    exported = 0
    failed = 0
    for project in projects:
        record, commits = git_record(project, PATHS.repos, timeout=args.timeout)
        csv_path = PATHS.commits / f"{project.id}.csv"
        if record["ref"] is None:
            csv_path.unlink(missing_ok=True)
        else:
            write_commits(csv_path, commit_rows(project, commits))
        write_measured("git", record, PATHS.measured("git"))
        records.append(record)
        if record["ref"] is None:
            reason = record["missing"].get("git")
            failed += reason == "fetch_error" or (
                reason == "unavailable"
                and mirror_path(PATHS.repos, project.id).exists()
            )
            print(f"  {reason:<14} {project.id} {record['error']}", file=sys.stderr)
            continue
        exported += len(commits)
        primary = record["primary_language"] or "--"
        print(
            f"  {project.id:<26} {record['commits']:>6} commits"
            f" {record['lines_total'] or 0:>9,} lines   {primary}",
            file=sys.stderr,
        )

    totals = language_totals(records)
    lines = sum(totals.values())
    measured = sum(1 for record in records if record["ref"] is not None)
    print(
        f"\n{measured} mirrors, {exported:,} commits, {lines:,} lines", file=sys.stderr
    )
    for language, count in totals.most_common():
        print(
            f"  {language:<12} {count:>9,}  {count / lines * 100:5.1f}%",
            file=sys.stderr,
        )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
