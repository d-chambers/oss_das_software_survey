"""Propose a catalogue entry for each triaged candidate group, one agent per group.

Triage says "this is about fiber sensing"; it does not say what the project
is, whether it is reusable, or which candidates are the same project. This
stage groups candidates by the same-project links triage recorded, hands each
group to a headless agent that reads what the project publishes about itself,
and stores the agent's proposal as ``data/enriched/<id>.md`` for a reviewer to
accept or reject. The proposal is validated as a ``ProjectRecord`` before it
is written, so review only ever sees records the schema accepts.

Provenance is measured, not asked for: the model identity, token counts, cost
and timing come from the API response, because a model cannot observe its own
usage and would have to invent it.
"""

from __future__ import annotations

import json
import re
import subprocess
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from pydantic import ValidationError

from oss_das.core import PATHS, read_record, write_record
from oss_das.models import (
    DasFocus,
    ForgeKind,
    LicenseClass,
    ProjectRecord,
)

#: The name recorded in each enriched file's provenance block.
AGENT_NAME = "das-enricher"

#: Read-only tooling. The agent fetches published pages and nothing else.
ALLOWED_TOOLS = "WebFetch"

#: Fields the agent proposes; the review step adds the rest.
PROPOSAL_EXCLUDES = {"sources", "reviewed_at", "provenance", "forge", "repository"}

#: How much of each candidate's body the prompt carries.
EVIDENCE_LIMIT = 3000

PROMPT = """You are proposing one entry for a research catalogue of open-source \
distributed acoustic sensing (DAS) software. DAS means fiber-optic distributed \
acoustic / vibration sensing; the catalogue also records other distributed fiber \
sensing (DTS, DSS, phi-OTDR) and general tools that support DAS data.

The candidates below were found by discovery and judged to be the same project. \
Read what the project publishes about itself with WebFetch: the repository \
landing page or README, and the documentation site or package page if there is \
one. Do not describe the project from prior knowledge.

## Candidates

{evidence}

## What to return

First, one fenced ```json block with exactly these keys:

- id: a short lowercase slug, letters, digits and hyphens (e.g. "dascore")
- name: the project's own name
- repository_url: the canonical source repository URL (https://host/owner/name), \
or null when no source repository is published
- homepage: documentation or project site URL, or null
- description: one sentence, under 160 characters, saying what the software does
- status: "included" when it is reusable DAS or fiber-sensing software with \
published source; "watchlist" when it is DAS software that is too early, thin, \
or unclear to include yet; "excluded" when it is not reusable software \
(a paper's analysis scripts, a course, a dataset, an acronym collision)
- decision_reason: one sentence justifying the status
- primary_category: one of {categories}
- capabilities: a list drawn from {capabilities}; add a new tag only when none fits
- das_focus: one of {focus}
- license_spdx: the SPDX identifier of the license actually published, or null
- license_class: one of {license_classes}; "unlicensed" when source is public \
with no license file
- registries: {{"pypi": [...], "conda": ["conda-forge/<name>", ...], "julia": [...]}} \
listing only packages you verified exist
- publications: a list of {{"doi": "...", "role": "canonical" or "related", \
"note": "..."}} for papers the project itself cites; "canonical" for the one \
paper that describes the software, at most one

Then, in GitHub-flavoured markdown, exactly this shape:

## Summary

One paragraph of 100-150 words, in plain prose, describing what this software \
does, who would use it, and what makes it different from a generic toolkit. Be \
concrete and factual. Do not market it.

## Details

- **Interface:** library, CLI, GUI application, notebook collection, or service
- **Data formats:** the DAS or fiber formats it reads or writes, if stated
- **Key dependencies:** the handful of libraries it is built on
- **Scope signals:** anything indicating maturity, scale, or intended audience
- **Source visible:** whether the repository actually publishes source code
- **Sources read:** the URLs you actually fetched

Rules that matter more than completeness:
- If you could not reach any source, write `UNAVAILABLE` under Summary, set \
status to "watchlist", and say what failed in decision_reason.
- If a detail is not stated in what you read, write `not stated`. Never infer a \
license, format, or dependency you did not see.
"""


# --- grouping -----------------------------------------------------------------


def latest_rows(rows: Iterable[dict[str, str]]) -> dict[str, dict[str, str]]:
    """Last row per key wins; that is the whole override mechanism."""
    latest: dict[str, dict[str, str]] = {}
    for row in rows:
        latest[row["key"]] = row
    return latest


def candidate_groups(latest: dict[str, dict[str, str]]) -> dict[str, list[str]]:
    """Group DAS verdicts by their same-project link.

    A group is one canonical key plus every candidate whose ``same_as`` points
    at it. Rows already catalogued are not proposals, so they are left out
    here; a group that touches one is dropped later by key.
    """
    members = {
        key
        for key, row in latest.items()
        if row.get("verdict") == "das" and row.get("rule") != "already-catalogued"
    }
    parent: dict[str, str] = {}

    def find(key: str) -> str:
        parent.setdefault(key, key)
        while parent[key] != key:
            parent[key] = parent[parent[key]]
            key = parent[key]
        return key

    for key in members:
        target = latest[key].get("same_as")
        if target:
            # A link is followed even through a candidate that is not itself a
            # DAS verdict, so chains a -> b -> c end up in one group.
            parent[find(key)] = find(target)
    # A link's target belongs to the group even without a DAS row of its own:
    # it is the same project, and the proposal should cite every alias.
    linked = {latest[k]["same_as"] for k in members if latest[k].get("same_as")}
    components: dict[str, set[str]] = {}
    for key in members | linked:
        components.setdefault(find(key), set()).add(key)
    groups: dict[str, list[str]] = {}
    for keys in components.values():
        # The canonical key is the member nothing points away from, else the
        # smallest key, so the choice is stable across reruns.
        roots = [k for k in keys if not latest.get(k, {}).get("same_as")]
        groups[min(roots or keys)] = sorted(keys)
    return dict(sorted(groups.items()))


def catalogued_keys(projects: Iterable[ProjectRecord]) -> set[str]:
    keys: set[str] = set()
    for project in projects:
        keys.update(project.sources)
        if project.forge_key:
            keys.add(project.forge_key)
    return keys


@dataclass(frozen=True)
class EnrichedIndex:
    """What ``data/enriched/`` already holds, by id and by candidate key."""

    ids: frozenset[str]
    keys: frozenset[str]

    @classmethod
    def load(cls, path: Path | None = None) -> EnrichedIndex:
        ids, keys = set(), set()
        for file in (path or PATHS.enriched).glob("*.md"):
            front, _ = read_record(file)
            ids.add(file.stem)
            keys.update(front.get("sources") or [])
        return cls(frozenset(ids), frozenset(keys))


def pending_groups(
    groups: dict[str, list[str]],
    *,
    catalogued: set[str],
    enriched: EnrichedIndex,
    force_ids: Iterable[str] = (),
) -> dict[str, list[str]]:
    """Groups still owed a proposal: none of their keys catalogued or enriched."""
    force = set(force_ids)
    out = {}
    for canonical, keys in groups.items():
        if any(key in catalogued for key in keys):
            continue
        if any(key in enriched.keys for key in keys) and not force:
            continue
        out[canonical] = keys
    return out


# --- prompt -------------------------------------------------------------------


def render_evidence(records: dict[str, tuple[dict[str, Any], str]]) -> str:
    parts = []
    for key, (front, body) in records.items():
        keep = {
            k: v
            for k, v in front.items()
            if k not in {"probes", "found_by", "first_seen"} and v not in (None, "", [])
        }
        text = f"### {key}\n\n```json\n{json.dumps(keep, indent=1, ensure_ascii=False)}\n```"
        if body:
            text += f"\n\nREADME or long description:\n\n{body[:EVIDENCE_LIMIT]}"
        parts.append(text)
    return "\n\n".join(parts)


def build_prompt(
    records: dict[str, tuple[dict[str, Any], str]],
    *,
    capabilities: Iterable[str],
    categories: Iterable[str],
) -> str:
    return PROMPT.format(
        evidence=render_evidence(records),
        categories=json.dumps(sorted(categories)),
        capabilities=json.dumps(sorted(capabilities)),
        focus=json.dumps([item.value for item in DasFocus]),
        license_classes=json.dumps([item.value for item in LicenseClass]),
    )


# --- agent --------------------------------------------------------------------


def run_agent(prompt: str, *, model: str, timeout: int) -> dict[str, Any]:
    """Run one headless agent; return ``{"payload", "started"}`` or ``{"error"}``."""
    started = datetime.now(UTC).replace(microsecond=0)
    command = [
        "claude",
        "-p",
        prompt,
        "--output-format",
        "json",
        "--model",
        model,
        "--allowedTools",
        ALLOWED_TOOLS,
    ]
    try:
        completed = subprocess.run(
            command, capture_output=True, text=True, timeout=timeout
        )
    except subprocess.TimeoutExpired:
        return {"error": f"timed out after {timeout}s"}
    if completed.returncode != 0:
        return {
            "error": completed.stderr.strip()[:400] or f"exit {completed.returncode}"
        }
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return {"error": "agent did not return JSON"}
    if payload.get("is_error"):
        return {"error": str(payload.get("result"))[:400]}
    return {"payload": payload, "started": started}


def usage_totals(payload: dict[str, Any]) -> dict[str, int]:
    """Sum token counts across every model the run actually used."""
    totals = {"input": 0, "output": 0, "cache_read": 0, "cache_write": 0}
    for usage in (payload.get("modelUsage") or {}).values():
        totals["input"] += usage.get("inputTokens", 0)
        totals["output"] += usage.get("outputTokens", 0)
        totals["cache_read"] += usage.get("cacheReadInputTokens", 0)
        totals["cache_write"] += usage.get("cacheCreationInputTokens", 0)
    return totals


def provenance(payload: dict[str, Any], started: datetime) -> dict[str, Any]:
    totals = usage_totals(payload)
    return {
        "agent": AGENT_NAME,
        "models": sorted(payload.get("modelUsage") or {}),
        "ran_at": started.isoformat(),
        "duration_seconds": round(payload.get("duration_ms", 0) / 1000, 1),
        "turns": payload.get("num_turns"),
        "input_tokens": totals["input"],
        "output_tokens": totals["output"],
        "cache_read_tokens": totals["cache_read"],
        "cache_write_tokens": totals["cache_write"],
        "total_tokens": sum(totals.values()),
        "api_list_cost_usd": round(payload.get("total_cost_usd", 0.0), 4),
        "provenance": "token counts and model identity come from the API"
        " response, not from the agent's self-report",
    }


# --- proposal -----------------------------------------------------------------

_FENCE = re.compile(r"```json\s*(\{.*?\})\s*```", re.S)


def parse_result(text: str) -> tuple[dict[str, Any], str]:
    """Split an agent result into its JSON proposal and the markdown after it."""
    match = _FENCE.search(text)
    if not match:
        raise ValueError("no ```json block in the agent result")
    proposal = json.loads(match.group(1))
    if not isinstance(proposal, dict):
        raise ValueError("the json block is not an object")
    body = text[match.end() :]
    index = body.find("## Summary")
    body = body[index:] if index != -1 else body
    return proposal, body.strip()


def forge_for(url: str, *, hints: dict[str, str]) -> tuple[str, str, str]:
    """``(kind, host, owner/name)`` for a repository URL.

    The kind comes from a forge candidate on the same host when the group has
    one, and from the host name otherwise; a host that gives no clue is
    reported as GitLab-like only if it says so.
    """
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    path = parsed.path.strip("/").removesuffix(".git")
    if not host or path.count("/") < 1:
        raise ValueError(f"repository_url {url!r} is not https://host/owner/name")
    kind = hints.get(host)
    if kind is None:
        if host == "github.com":
            kind = ForgeKind.GITHUB.value
        elif "gitlab" in host:
            kind = ForgeKind.GITLAB.value
        elif host == "codeberg.org" or "gitea" in host or "forgejo" in host:
            kind = ForgeKind.GITEA.value
        else:
            raise ValueError(f"cannot tell which API {host} speaks")
    return kind, host, path


def to_record(proposal: dict[str, Any], *, hints: dict[str, str]) -> ProjectRecord:
    """Validate a proposal, deriving repository and forge from its URL."""
    fields = {k: v for k, v in proposal.items() if k not in PROPOSAL_EXCLUDES}
    url = fields.pop("repository_url", None)
    if url:
        kind, host, path = forge_for(url, hints=hints)
        fields["repository"] = path
        fields["repository_url"] = f"https://{host}/{path}"
        fields["forge"] = {"kind": kind, "host": host}
    fields["publications"] = [
        item
        for item in fields.get("publications") or []
        if isinstance(item, dict) and item.get("doi")
    ]
    return ProjectRecord.model_validate(fields)


def unique_id(proposed: str, taken: Iterable[str]) -> str:
    """The proposed id, or the first numeric suffix that is free."""
    taken = set(taken)
    if proposed not in taken:
        return proposed
    index = 2
    while f"{proposed}-{index}" in taken:
        index += 1
    return f"{proposed}-{index}"


def render_enriched(
    record: ProjectRecord, *, sources: list[str], provenance: dict[str, Any]
) -> dict[str, Any]:
    """The frontmatter of ``data/enriched/<id>.md``."""
    proposed = record.model_dump(
        mode="json", exclude={"sources", "reviewed_at", "provenance"}
    )
    return {"proposed": proposed, "sources": sorted(sources), "provenance": provenance}


def write_enriched(
    front: dict[str, Any], body: str, *, path: Path | None = None
) -> Path:
    target = (path or PATHS.enriched) / f"{front['proposed']['id']}.md"
    write_record(target, front, body)
    return target


def propose(
    result: dict[str, Any],
    *,
    sources: list[str],
    hints: dict[str, str],
    taken_ids: Iterable[str],
) -> tuple[dict[str, Any], str]:
    """Turn one agent run into an enriched frontmatter and body, or raise."""
    if "error" in result:
        raise ValueError(result["error"])
    payload = result["payload"]
    proposal, body = parse_result(str(payload.get("result", "")))
    try:
        record = to_record(proposal, hints=hints)
    except ValidationError as error:
        raise ValueError(str(error)) from error
    record = record.model_copy(update={"id": unique_id(record.id, taken_ids)})
    front = render_enriched(
        record, sources=sources, provenance=provenance(payload, result["started"])
    )
    return front, body
