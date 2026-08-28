#!/usr/bin/env python3
"""Look up each curated DOI on OpenAlex and record its citations.

Reads:  data/curated/*.md, OPENALEX_API_KEY (optional)
Writes: data/measured/publications/<id>.md
"""

from __future__ import annotations

import argparse
import os
import sys

from oss_das.clients import OpenAlexClient
from oss_das.core import PATHS
from oss_das.measure import publication_record, select_projects, write_measured


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--only", nargs="+", default=None, help="Restrict to these ids."
    )
    args = parser.parse_args()

    projects = select_projects(args.only)
    works = resolved = 0
    with OpenAlexClient(os.getenv("OPENALEX_API_KEY")) as openalex:
        for project in projects:
            record = publication_record(project, openalex)
            write_measured("publications", record, PATHS.measured("publications"))
            items = record["publications"]
            works += len(items)
            resolved += sum(1 for item in items if not item["missing"])
            if items:
                print(
                    f"  {project.id:<26} {len(items)} DOIs"
                    f" total={record['citations_total']}"
                    f" canonical={record['canonical_citations']}",
                    file=sys.stderr,
                )
    print(
        f"{len(projects)} projects, {resolved}/{works} works resolved", file=sys.stderr
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
