#!/usr/bin/env python3
"""Measure lines of source per language from the mirrors a025 left behind.

Out-of-band, like a025 and a070: it reads gigabytes of bare mirrors rather than
the snapshot, so it is run deliberately and not from a000_run_all.py.

Writes one row per project and language to <dest>/loc.csv. A project whose
mainline tip publishes no counted source gets no rows there and is listed in
the run summary instead -- the absence is the finding, and a zero row would
read as "measured, and it was zero".
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

from oss_das.commits import GitError
from oss_das.core import PATHS, write_csv
from oss_das.loc import LOC_FIELDS, RepoLines, iter_mirrors, measure_mirror

DEFAULT_DEST = PATHS.root / "data"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dest",
        type=Path,
        default=DEFAULT_DEST,
        help="Directory holding repos/; loc.csv is written here.",
    )
    parser.add_argument(
        "--only", nargs="+", default=None, help="Restrict to these project ids."
    )
    parser.add_argument("--timeout", type=int, default=900, help="Per-repo seconds.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    repos: Path = args.dest / "repos"
    if not repos.is_dir():
        raise SystemExit(f"no mirrors to measure: {repos} does not exist")

    mirrors = list(iter_mirrors(repos))
    if args.only:
        wanted = set(args.only)
        mirrors = [m for m in mirrors if m.name.removesuffix(".git") in wanted]
        missing = wanted - {m.name.removesuffix(".git") for m in mirrors}
        if missing:
            raise SystemExit(f"no mirror for: {', '.join(sorted(missing))}")
    print(f"measuring {len(mirrors)} mirrors under {repos}", file=sys.stderr)

    measured: list[RepoLines] = []
    failed: list[tuple[str, str]] = []
    for mirror in mirrors:
        project_id = mirror.name.removesuffix(".git")
        try:
            result = measure_mirror(mirror, timeout=args.timeout)
        except GitError as error:
            failed.append((project_id, str(error)))
            print(f"  FAIL {project_id}: {error}", file=sys.stderr)
            continue
        measured.append(result)
        primary = result.primary_language or "--"
        print(
            f"  {project_id:<26} {result.total:>9,} lines   {primary}",
            file=sys.stderr,
        )

    rows = [row for result in measured for row in result.rows()]
    write_csv(args.dest / "loc.csv", rows, LOC_FIELDS)

    totals: Counter[str] = Counter()
    for result in measured:
        totals.update(result.languages)
    lines = sum(totals.values())
    sourceless = sorted(r.project_id for r in measured if not r.languages)
    print(f"\n{len(measured)} mirrors, {lines:,} lines", file=sys.stderr)
    for language, count in totals.most_common():
        share = count / lines * 100 if lines else 0.0
        print(f"  {language:<12} {count:>9,}  {share:5.1f}%", file=sys.stderr)
    if sourceless:
        print(
            f"no counted source at tip ({len(sourceless)}): {', '.join(sourceless)}",
            file=sys.stderr,
        )
    # A partial measurement that exited zero would be read downstream as a
    # complete one, the same contract a025 keeps.
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
