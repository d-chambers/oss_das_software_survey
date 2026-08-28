#!/usr/bin/env python3
"""Read each curated repository's record from its code host's API.

Reads:  data/curated/*.md, GITHUB_TOKEN (optional)
Writes: data/measured/forge/<id>.md

Without a token, GitHub-hosted projects are recorded as unavailable rather
than fetched: the unauthenticated limit would be exhausted within the first
few repositories. GitLab and Gitea hosts need no token.
"""

from __future__ import annotations

import argparse
import os
import sys

from oss_das.core import PATHS
from oss_das.measure import ForgeClients, forge_record, select_projects, write_measured


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--only", nargs="+", default=None, help="Restrict to these ids."
    )
    args = parser.parse_args()

    projects = select_projects(args.only)
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("no GITHUB_TOKEN: GitHub projects will be unavailable", file=sys.stderr)
    measured = 0
    with ForgeClients(token) as clients:
        for project in projects:
            record = forge_record(project, clients)
            write_measured("forge", record, PATHS.measured("forge"))
            missing = record["missing"].get("repository")
            if missing:
                print(
                    f"  {missing:<14} {project.id} {record['error']}", file=sys.stderr
                )
            else:
                measured += 1
                print(
                    f"  ok             {project.id} {record['stars']} stars",
                    file=sys.stderr,
                )
    print(f"{measured}/{len(projects)} repositories read", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
