#!/usr/bin/env python3
"""Measure a reference ecosystem's dependency graph, for comparison with DAS.

Reads:  GITHUB_TOKEN
Writes: data/comparison/<ecosystem>/<owner>--<name>.md
        data/comparison/<ecosystem>-coverage.csv
No clones.

The `s` stage sits outside a/b/c on purpose. These repositories are not
candidates for the catalogue and must never reach the funnel, which counts
every file under data/raw/candidates. Keeping them in their own tree is what
stops a second ecosystem changing this one's arithmetic.
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import UTC, datetime

from oss_das.clients.github import SEARCH_RESULT_LIMIT, GitHubClient
from oss_das.comparison import RepositoryReader, dependency_record
from oss_das.core import PATHS, append_csv, write_record
from oss_das.discover import COVERAGE_FIELDS

#: Search allows thirty requests a minute; the tree listings share the core
#: budget. Two seconds between requests keeps a full run under both.
MIN_INTERVAL = 2.0


def record_path(ecosystem: str, repository: str):
    owner, _, name = repository.partition("/")
    return PATHS.comparison(ecosystem) / f"{owner}--{name}.md".lower()


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--ecosystem", default="seismology", help="Topic to sweep.")
    parser.add_argument(
        "--limit", type=int, default=None, help="Stop after this many repositories."
    )
    parser.add_argument(
        "--refresh", action="store_true", help="Re-read repositories already recorded."
    )
    args = parser.parse_args()

    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("no GITHUB_TOKEN: refusing to sweep anonymously", file=sys.stderr)
        return 2

    out = PATHS.comparison(args.ecosystem)
    out.mkdir(parents=True, exist_ok=True)
    fetched_at = datetime.now(UTC).isoformat(timespec="seconds")
    query = f"topic:{args.ecosystem}"

    with GitHubClient(token, min_interval=MIN_INTERVAL) as github:
        items, total = github.search_items(query)
        truncated = total > len(items)
        append_csv(
            PATHS.comparison_coverage(args.ecosystem),
            [
                {
                    "fetched_at": fetched_at,
                    "host": "github.com",
                    "kind": "github",
                    "probe": f"github.com:{query}",
                    "query": query,
                    "status": "ok",
                    "reported_total": total,
                    "retrieved": len(items),
                    "truncated": truncated,
                    "error": "",
                }
            ],
            COVERAGE_FIELDS,
        )
        # A truncated sweep is not a smaller sweep, it is an unknown one: the
        # thousand it returns are the thousand GitHub chose to rank first.
        assert not truncated, (
            f"{query} reported {total} repositories, past the "
            f"{SEARCH_RESULT_LIMIT} search cap; partition the query by stars "
            "or creation date and sweep each slice"
        )
        print(f"{len(items)} repositories carry {query}", file=sys.stderr)

        hits = items[: args.limit] if args.limit else items
        written = skipped = failed = 0
        with RepositoryReader(github) as reader:
            for index, hit in enumerate(hits, 1):
                repository = hit["full_name"]
                path = record_path(args.ecosystem, repository)
                if path.exists() and not args.refresh:
                    skipped += 1
                    continue
                record = dependency_record(repository, hit["default_branch"], reader)
                record.update(
                    ecosystem=args.ecosystem,
                    name=hit["name"],
                    stars=hit.get("stargazers_count"),
                    language=hit.get("language"),
                    fork=bool(hit.get("fork")),
                    archived=bool(hit.get("archived")),
                    pushed_at=hit.get("pushed_at"),
                    fetched_at=fetched_at,
                )
                write_record(path, record)
                written += 1
                if record["error"]:
                    failed += 1
                print(
                    f"  {index:>4}/{len(hits)}  {repository:<52} "
                    f"{len(record['manifests'])} manifests, "
                    f"{len(record['declared'])} declared",
                    file=sys.stderr,
                )

    print(
        f"{written} written, {skipped} already present, {failed} with errors",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
