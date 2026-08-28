#!/usr/bin/env python3
"""Collect direct PyPI requirement metadata for the dependency graph."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from oss_das.cli import require_existing, resolve_snapshot_date, snapshot_parser
from oss_das.clients.packages import PyPIClient
from oss_das.collection import SOURCE_FAILURES, missingness
from oss_das.core import PATHS, load_projects, write_jsonl
from oss_das.models import CatalogStatus
from oss_das.utils import utc_now


def main() -> None:
    parser = snapshot_parser(__doc__)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    snapshot_date = resolve_snapshot_date(args.snapshot_date)
    output = PATHS.raw(snapshot_date) / "dependencies.jsonl"
    if require_existing(output, offline=args.offline):
        return
    if output.exists() and not args.force:
        raise FileExistsError("dependency metadata exists; pass --force to replace it")
    work = [
        (project.id, package)
        for project in load_projects()
        if project.status != CatalogStatus.EXCLUDED
        for package in project.registries.pypi
    ]

    def collect(item: tuple[str, str]) -> dict:
        project_id, package = item
        record = {
            "project_id": project_id,
            "registry": "pypi",
            "name": package,
            "source_url": f"https://pypi.org/pypi/{package}/json",
            "fetched_at": utc_now(),
        }
        try:
            record.update(client.package(package), missing_reason=None)
        except SOURCE_FAILURES as error:
            record.update(missingness(error, absent_reason="not_published"))
        return record

    with PyPIClient() as client:
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            records = list(pool.map(collect, work))
    write_jsonl(output, records)
    print(f"collected dependency metadata for {len(records)} PyPI distributions")


if __name__ == "__main__":
    main()
