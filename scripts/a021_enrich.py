#!/usr/bin/env python3
"""Ask one agent per triaged candidate group to propose a catalogue entry.

Reads:  data/triage.csv (last row per key wins), data/raw/candidates/**/*.md,
        data/curated/*.md (catalogued keys, capability vocabulary),
        data/enriched/*.md (groups already proposed)
Writes: data/enriched/<id>.md (proposal frontmatter, agent prose as body)

A group is a candidate with verdict ``das`` plus every candidate whose
``same_as`` points at it. Groups touching a curated or already-enriched key
are skipped, so re-running proposes only what is new. Each proposal is
validated as a ProjectRecord before anything is written; a proposal the
schema rejects is reported and leaves no file.
"""

from __future__ import annotations

import argparse
import sys
from concurrent.futures import ThreadPoolExecutor

from oss_das.core import PATHS, load_projects, read_csv, read_record
from oss_das.enrich import (
    EnrichedIndex,
    build_prompt,
    candidate_groups,
    catalogued_keys,
    latest_rows,
    pending_groups,
    propose,
    run_agent,
    write_enriched,
)


def load_candidates(keys: set[str]) -> dict[str, tuple[dict, str]]:
    out = {}
    for path in sorted(PATHS.candidates.glob("*/*.md")):
        front, body = read_record(path)
        if front["key"] in keys:
            out[front["key"]] = (front, body)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--model", default="sonnet")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument(
        "--limit", type=int, default=None, help="Propose at most N groups."
    )
    parser.add_argument(
        "--only",
        nargs="*",
        default=None,
        help="Restrict to groups containing these keys.",
    )
    parser.add_argument(
        "--force",
        nargs="*",
        default=None,
        metavar="ID",
        help="Redo these enriched ids.",
    )
    parser.add_argument("--timeout", type=int, default=600)
    args = parser.parse_args()

    projects = load_projects()
    catalogued = catalogued_keys(projects)
    enriched = EnrichedIndex.load()
    groups = candidate_groups(latest_rows(read_csv(PATHS.triage)))

    force_ids = set(args.force or [])
    forced_id_of: dict[str, str] = {}
    if force_ids:
        forced_keys: set[str] = set()
        for identifier in force_ids:
            front, _ = read_record(PATHS.enriched / f"{identifier}.md")
            forced_keys.update(front.get("sources") or [])
            for key in front.get("sources") or []:
                forced_id_of[key] = identifier
        groups = {c: keys for c, keys in groups.items() if forced_keys & set(keys)}
    pending = pending_groups(
        groups, catalogued=catalogued, enriched=enriched, force_ids=force_ids
    )
    if args.only:
        wanted = set(args.only)
        pending = {c: keys for c, keys in pending.items() if wanted & set(keys)}
    if args.limit:
        pending = dict(list(pending.items())[: args.limit])
    if not pending:
        print("nothing to propose")
        return 0

    candidates = load_candidates({key for keys in pending.values() for key in keys})
    capabilities = {tag for project in projects for tag in project.capabilities}
    categories = {project.primary_category for project in projects}
    taken = set(enriched.ids - force_ids) | {project.id for project in projects}

    def work(item: tuple[str, list[str]]) -> tuple[str, list[str], dict]:
        canonical, keys = item
        records = {key: candidates[key] for key in keys if key in candidates}
        prompt = build_prompt(records, capabilities=capabilities, categories=categories)
        return (
            canonical,
            keys,
            run_agent(prompt, model=args.model, timeout=args.timeout),
        )

    print(f"proposing {len(pending)} groups with {args.model}", file=sys.stderr)
    spend = 0.0
    written = 0
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for canonical, keys, result in pool.map(work, pending.items()):
            hints = {
                candidates[k][0]["forge_host"]: candidates[k][0]["forge_kind"]
                for k in keys
                if k in candidates and candidates[k][0].get("source") == "forge"
            }
            try:
                front, body = propose(
                    result, sources=keys, hints=hints, taken_ids=taken
                )
            except ValueError as error:
                print(f"  FAIL {canonical}: {str(error)[:300]}", file=sys.stderr)
                continue
            forced = {forced_id_of[k] for k in keys if k in forced_id_of}
            if forced:
                # A forced redo replaces its file; a drifted id would leave two.
                front["proposed"]["id"] = min(forced)
            taken.add(front["proposed"]["id"])
            target = write_enriched(front, body)
            spend += front["provenance"]["api_list_cost_usd"]
            written += 1
            print(
                f"  ok   {canonical} -> {target.name} [{front['proposed']['status']}]",
                file=sys.stderr,
            )
    print(f"wrote {written} of {len(pending)} proposals, ${spend:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
