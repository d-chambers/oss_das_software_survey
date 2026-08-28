#!/usr/bin/env python3
"""Decide, cheaply, which candidates are worth an agent's time.

Reads:  data/raw/candidates/**/*.md, data/rejected.yml, data/curated/*.md,
        data/triage.csv (last row per key wins)
Writes: data/triage.csv (append-only)

Two layers, cheapest first. The deterministic layer needs no network: a key
in the rejection ledger, a key already catalogued, or a bare-acronym hit with
no fiber/DAS vocabulary in its name or description. Validated on the
2026-08-28 discovery it kept 582 of 3,245 candidates and would have dropped
none of the 94 the reviewer had accepted. Stars are deliberately not a rule:
a quarter of the included projects had none at discovery.

The model layer (``--model``) shows each survivor's frontmatter and body to a
cheap model and records its verdict, with the model id from the response.
Without ``--model`` survivors are left undecided and reported, so a later run
can pick them up. A human overrides any row by appending one with
``model: human``.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from typing import Any

from oss_das.core import (
    PATHS,
    append_csv,
    candidate_key,
    load_projects,
    load_rejections,
    read_csv,
    read_record,
)

TRIAGE_FIELDS = ["key", "verdict", "rule", "reason", "same_as", "model", "date"]

#: Vocabulary that marks a name or description as plausibly about fiber sensing.
TOKEN = re.compile(
    r"fib(er|re)|distributed acoustic|\bdas\b|dfos|dts\b|dss\b|interrogator"
    r"|strain|seismic|optic|acoustic|geophys",
    re.I,
)

PROMPT = """You are triaging one software repository for a census of distributed \
acoustic sensing (DAS) software. DAS means fiber-optic distributed acoustic / \
vibration sensing (also phi-OTDR, DFOS, DTS, DSS). "DAS" also abbreviates many \
unrelated things (data acquisition system, deep audio segmenter, German "das").

Candidate metadata and README excerpt:

{record}

Answer with one JSON object and nothing else:
{{"verdict": "das" or "not-das", "confidence": "high"|"medium"|"low", \
"reason": "<one sentence>"}}

"das" means the software is about fiber-optic distributed sensing in any way; \
reusability is judged later, not here. When the evidence is thin, prefer "das" \
with low confidence over "not-das"."""


def load_candidates() -> dict[str, tuple[dict[str, Any], str]]:
    out = {}
    for path in sorted(PATHS.candidates.glob("*/*.md")):
        front, body = read_record(path)
        out[front["key"]] = (front, body)
    return out


def decided_keys(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    """Last row per key wins; that is the whole override mechanism."""
    latest: dict[str, dict[str, str]] = {}
    for row in rows:
        latest[row["key"]] = row
    return latest


def has_token(front: dict[str, Any]) -> bool:
    text = f"{front.get('name') or ''} {front.get('description') or ''}"
    return bool(TOKEN.search(text))


def deterministic(
    front: dict[str, Any],
    *,
    rejected: dict[str, dict[str, str]],
    catalogued: dict[str, str],
    forge_keys: dict[str, str],
) -> dict[str, str] | None:
    """Return a triage row, or None when the candidate survives to the model."""
    key = front["key"]
    if key in rejected:
        return {
            "verdict": "not-das",
            "rule": "rejected-ledger",
            "reason": rejected[key]["reason"],
        }
    if key in catalogued:
        return {
            "verdict": "das",
            "rule": "already-catalogued",
            "reason": catalogued[key],
        }
    same_as = ""
    url = front.get("repository_url") or ""
    if front.get("source") != "forge" and url:
        host_path = re.sub(r"^https?://", "", url).strip("/").split("/")
        if len(host_path) >= 3:
            linked = candidate_key(host_path[0], "/".join(host_path[1:]))
            if linked in forge_keys:
                same_as = linked
    if front.get("probe_class") != "domain-specific" and not has_token(front):
        return {
            "verdict": "not-das",
            "rule": "bare-acronym-no-token",
            "reason": "no fiber-sensing vocabulary in name or description, and not from a domain-specific probe",
            "same_as": same_as,
        }
    if same_as:
        return {
            "verdict": "das",
            "rule": "same-project",
            "reason": f"declares {same_as}",
            "same_as": same_as,
        }
    return None


def render_for_model(front: dict[str, Any], body: str) -> str:
    keep = {
        k: v
        for k, v in front.items()
        if k not in {"probes", "found_by"} and v not in (None, "", [])
    }
    text = json.dumps(keep, indent=1, ensure_ascii=False)
    return text + (
        "\n\nREADME:\n" + body[:4000] if body else "\n\n(no README captured)"
    )


def ask_model(key: str, record: str, *, model: str, timeout: int) -> dict[str, str]:
    """One headless call; the model id and cost come from the response, not the model."""
    command = [
        "claude",
        "-p",
        PROMPT.format(record=record),
        "--output-format",
        "json",
        "--model",
        model,
    ]
    try:
        done = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
        payload = json.loads(done.stdout)
        answer = json.loads(
            re.search(r"\{.*\}", str(payload.get("result", "")), re.S).group(0)
        )
        verdict = "das" if answer.get("verdict") == "das" else "not-das"
        used = ",".join(sorted(payload.get("modelUsage") or {})) or model
        reason = f"[{answer.get('confidence', '?')}] {answer.get('reason', '')}".strip()
        return {
            "key": key,
            "verdict": verdict,
            "rule": "model",
            "reason": reason,
            "model": used,
        }
    except Exception as error:
        print(f"  FAIL {key}: {str(error)[:100]}", file=sys.stderr)
        return {}


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--model", default=None, help="Run the model layer with this model, e.g. haiku."
    )
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument(
        "--limit", type=int, default=None, help="Model at most N survivors."
    )
    parser.add_argument(
        "--only", nargs="*", default=None, help="Restrict to these candidate keys."
    )
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()

    candidates = load_candidates()
    decided = decided_keys(read_csv(PATHS.triage))
    rejected = load_rejections()
    catalogued: dict[str, str] = {}
    forge_keys: dict[str, str] = {}
    for project in load_projects():
        for source in project.sources:
            catalogued[source] = project.id
        if project.forge_key:
            catalogued[project.forge_key] = project.id
    for key, (front, _) in candidates.items():
        if front.get("source") == "forge":
            forge_keys[key] = key

    pending = {
        k: v
        for k, v in candidates.items()
        if k not in decided and (not args.only or k in args.only)
    }
    today = datetime.now(UTC).date().isoformat()
    rows: list[dict[str, str]] = []
    survivors: list[str] = []
    for key, (front, _) in pending.items():
        row = deterministic(
            front, rejected=rejected, catalogued=catalogued, forge_keys=forge_keys
        )
        if row is None:
            survivors.append(key)
        else:
            rows.append(
                {
                    "key": key,
                    "same_as": "",
                    "model": "deterministic",
                    "date": today,
                    **row,
                }
            )

    modelled: list[dict[str, str]] = []
    if args.model and survivors:
        todo = survivors[: args.limit] if args.limit else survivors
        print(f"asking {args.model} about {len(todo)} candidates", file=sys.stderr)
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            for row in pool.map(
                lambda k: ask_model(
                    k,
                    render_for_model(*candidates[k]),
                    model=args.model,
                    timeout=args.timeout,
                ),
                todo,
            ):
                if row:
                    modelled.append({**row, "same_as": "", "date": today})
        survivors = [k for k in survivors if k not in {r["key"] for r in modelled}]

    written = append_csv(PATHS.triage, rows + modelled, TRIAGE_FIELDS)

    by_rule: dict[str, int] = {}
    for row in rows + modelled:
        label = f"{row['rule']}:{row['verdict']}"
        by_rule[label] = by_rule.get(label, 0) + 1
    print(
        f"candidates {len(candidates)}, already decided {len(decided)}, new rows {written}"
    )
    for label, count in sorted(by_rule.items(), key=lambda item: -item[1]):
        print(f"  {label:34s} {count}")
    print(f"undecided (need --model): {len(survivors)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
