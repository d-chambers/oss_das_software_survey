#!/usr/bin/env python3
"""Search the code hosts for fiber-sensing repositories and record each finding once.

Reads:  data/curated/*.md (namespaces to walk), data/rejected.yml,
        data/raw/candidates/**/*.md (existing keys are never rewritten)
Writes: data/raw/candidates/<host>/<owner--name>.md (write-once, README as body),
        data/raw/coverage.csv (append-only: one row per probe, run or not)

GitHub is searched with the full-text phrase queries and topic probes; the
GitLab and Gitea instances, whose search covers names and descriptions only,
get the short phrases. Every owner of a curated repository is then listed,
because a group's newest repository is usually found before it describes
itself. Without ``GITHUB_TOKEN`` the GitHub probes are recorded as skipped
rather than run against the anonymous limit.
"""

from __future__ import annotations

import argparse
import contextlib
import os
import sys
from datetime import UTC, datetime

from oss_das.collection import open_forges
from oss_das.core import load_projects, load_rejections
from oss_das.discover import (
    CandidateStore,
    append_coverage,
    refresh_candidate,
    search_forges,
    write_forge_candidates,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--refresh", metavar="KEY", help="Rewrite one candidate file from its host."
    )
    args = parser.parse_args()

    token = os.getenv("GITHUB_TOKEN")
    store = CandidateStore(rejected=frozenset(load_rejections()))
    now = datetime.now(UTC).replace(microsecond=0)
    with contextlib.ExitStack() as stack:
        forges = [stack.enter_context(forge) for forge in open_forges(token)]
        if args.refresh:
            refresh_candidate(args.refresh, store=store, forges=forges)
            print(f"refreshed {args.refresh}")
            return 0
        unavailable = {} if token else {"github.com": "no GITHUB_TOKEN"}
        if unavailable:
            print(
                "GITHUB_TOKEN is not set; GitHub probes recorded as skipped",
                file=sys.stderr,
            )
        hits = search_forges(
            forges,
            load_projects(),
            fetched_at=now.isoformat(),
            coverage=append_coverage,
            unavailable=unavailable,
        )
        written = write_forge_candidates(
            hits, store=store, forges=forges, first_seen=now.date().isoformat()
        )
    print(f"hits {len(hits)}, new candidates {len(written)}")
    for key in written:
        print(f"  {key}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
