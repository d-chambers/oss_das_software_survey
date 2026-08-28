#!/usr/bin/env python3
"""Mirror every catalogued repository and export its per-commit history.

Out-of-band, like a070: this stage is not in a000_run_all.py's stage list. It
clones tens of repositories over the network and writes gigabytes to a
destination that is normally an external drive, so it is run deliberately
rather than as part of a snapshot build.

Each project gets a bare mirror under <dest>/repos and a CSV of its commits
under <dest>/commits. Re-running is cheap: an existing mirror is left alone
unless --update is passed.
"""

from __future__ import annotations

import argparse
import shutil
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from oss_das.commits import (
    COMMIT_FIELDS,
    STATUS_FIELDS,
    ProjectResult,
    collect_project,
    iter_rows,
)
from oss_das.core import load_projects, read_csv, write_csv
from oss_das.models import CatalogStatus

DEFAULT_DEST = Path("/media/derrick/Backup Plus/oss_das")

GIB = 1024**3


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dest", type=Path, default=DEFAULT_DEST)
    parser.add_argument(
        "--status",
        nargs="+",
        choices=[status.value for status in CatalogStatus],
        default=[status.value for status in CatalogStatus],
        help="Catalog statuses to include; defaults to all of them.",
    )
    parser.add_argument(
        "--only", nargs="+", default=None, help="Restrict to these ids."
    )
    parser.add_argument("--jobs", type=int, default=8)
    parser.add_argument(
        "--update",
        action="store_true",
        help="Fetch existing mirrors instead of leaving them alone.",
    )
    parser.add_argument("--timeout", type=int, default=1800, help="Per-repo seconds.")
    parser.add_argument(
        "--min-free-gb",
        type=float,
        default=20.0,
        help="Stop starting new clones below this much free space.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Rewrite commit CSVs for mirrors that already exist.",
    )
    return parser


def merge_csv(path, fields, rows, touched: set[str]) -> None:
    """Replace only the projects this run touched, keeping every other row.

    The combined tables accumulate across runs, so a `--only` retry of two
    repositories must not erase the seventy-eight it did not look at.
    """
    kept = [row for row in read_csv(path) if row["project_id"] not in touched]
    combined = [*kept, *rows]
    combined.sort(key=lambda row: row["project_id"])
    write_csv(path, combined, fields)


def main() -> int:
    args = build_parser().parse_args()
    dest: Path = args.dest
    if not dest.exists():
        raise FileNotFoundError(f"destination does not exist: {dest}")
    projects = [
        project
        for project in load_projects()
        if project.status.value in args.status
        and (args.only is None or project.id in args.only)
    ]
    if args.only:
        missing = set(args.only) - {project.id for project in projects}
        if missing:
            raise SystemExit(f"unknown project ids: {', '.join(sorted(missing))}")
    print(f"collecting {len(projects)} repositories into {dest}", file=sys.stderr)

    # Serialized so eight workers cannot each see enough room and then fill the
    # disk between them.
    admission = threading.Lock()

    def run(project) -> ProjectResult:
        with admission:
            free = shutil.disk_usage(dest).free / GIB
            if free < args.min_free_gb:
                return ProjectResult(
                    project=project,
                    clone_result="failed",
                    error=f"insufficient disk space ({free:.1f} GiB free)",
                )
        return collect_project(
            project,
            dest,
            update=args.update,
            timeout=args.timeout,
            force=args.force,
        )

    results: list[ProjectResult] = []
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        for result in pool.map(run, projects):
            results.append(result)
            if result.ok:
                print(
                    f"  OK   {result.project.id}: {result.clone_result}"
                    f" {len(result.commits)} commits on {result.ref}"
                    f" ({result.duration_s:.0f}s)",
                    file=sys.stderr,
                )
            else:
                print(
                    f"  FAIL {result.project.id}: {result.error[:110]}",
                    file=sys.stderr,
                )

    results.sort(key=lambda result: result.project.id)
    touched = {result.project.id for result in results}
    merge_csv(dest / "commits_all.csv", COMMIT_FIELDS, iter_rows(results), touched)
    merge_csv(
        dest / "collection_status.csv",
        STATUS_FIELDS,
        (result.status_row() for result in results),
        touched,
    )
    ok = [result for result in results if result.ok]
    commits = sum(len(result.commits) for result in ok)
    disk = sum(result.repo_bytes or 0 for result in ok) / GIB
    print(
        f"{len(ok)}/{len(results)} repositories, {commits} commits, {disk:.1f} GiB",
        file=sys.stderr,
    )
    # Any failure is a failure: an incomplete export that exits zero would be
    # read downstream as a complete one.
    return 1 if len(ok) != len(results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
