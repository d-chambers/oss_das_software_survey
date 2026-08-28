#!/usr/bin/env python3
"""Collect PyPI, PyPI Stats, conda-channel, and Julia registry metadata."""

from __future__ import annotations

import os

from oss_das.cli import require_existing, resolve_snapshot_date, snapshot_parser
from oss_das.clients import (
    CondaClient,
    JuliaRegistryClient,
    PyPIClient,
    PyPIStatsClient,
)
from oss_das.collection import collect_julia, collect_packages, probe_conda_forge
from oss_das.core import PATHS, load_projects, write_jsonl


def main() -> None:
    args = snapshot_parser(__doc__).parse_args()
    snapshot_date = resolve_snapshot_date(args.snapshot_date)
    output = PATHS.raw(snapshot_date) / "packages.jsonl"
    daily_output = PATHS.raw(snapshot_date) / "pypi_daily.jsonl"
    if require_existing(output, offline=args.offline):
        require_existing(daily_output, offline=True)
        return
    if (output.exists() or daily_output.exists()) and not args.force:
        raise FileExistsError("registry output exists; pass --force to replace it")
    projects = load_projects()
    with (
        PyPIClient() as pypi,
        PyPIStatsClient() as stats,
        CondaClient() as conda,
        JuliaRegistryClient(os.getenv("GITHUB_TOKEN")) as julia,
    ):
        records, daily = collect_packages(pypi, stats, conda, projects)
        records.extend(collect_julia(julia, projects))
        undeclared = probe_conda_forge(conda, projects)
    write_jsonl(output, records)
    write_jsonl(daily_output, daily)
    for finding in undeclared:
        print(
            f"conda-forge {finding['status']}: {finding['project_id']} -> "
            f"{finding['identifier']}"
        )
    for record in records:
        if record["registry"] == "julia" and not record.get("registered"):
            print(
                f"julia unregistered: {record['project_id']} -> {record['name']} "
                f"({record.get('missing_reason')})"
            )


if __name__ == "__main__":
    main()
