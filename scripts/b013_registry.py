#!/usr/bin/env python3
"""Measure each project's packages on PyPI, PyPI Stats, conda, and Julia.

Reads:  data/curated/*.md, GITHUB_TOKEN (optional, for the Julia registry)
Writes: data/measured/registry/<id>.md

PyPI Stats is paced at six seconds a request, so a run takes a few minutes.
"""

from __future__ import annotations

import argparse
import os
import sys

from oss_das.clients import (
    CondaClient,
    JuliaRegistryClient,
    PyPIClient,
    PyPIStatsClient,
)
from oss_das.core import PATHS
from oss_das.measure import registry_record, select_projects, write_measured


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--only", nargs="+", default=None, help="Restrict to these ids."
    )
    args = parser.parse_args()

    projects = select_projects(args.only)
    packages = 0
    with (
        PyPIClient() as pypi,
        PyPIStatsClient() as stats,
        CondaClient() as conda,
        JuliaRegistryClient(os.getenv("GITHUB_TOKEN")) as julia,
    ):
        for project in projects:
            record = registry_record(project, pypi, stats, conda, julia)
            write_measured("registry", record, PATHS.measured("registry"))
            items = [*record["pypi"], *record["conda"], *record["julia"]]
            packages += len(items)
            gaps = [f"{i.get('name')}:{i['missing']}" for i in items if i["missing"]]
            if items:
                print(
                    f"  {project.id:<26} {len(items)} packages"
                    f" {record['pypi_downloads_30d'] or ''} {' '.join(gaps)}",
                    file=sys.stderr,
                )
    print(f"{len(projects)} projects, {packages} packages", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
