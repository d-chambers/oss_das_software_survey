"""What the review notebook decides with; the notebook itself only wires widgets.

Review is the one step where a person writes to ``data/curated/``. Everything
that can be tested without a browser lives here: which proposals are still
pending and in what order, how an edited form becomes a validated record, and
what a rejection appends to the ledger.
"""

from __future__ import annotations

import random
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from oss_das.core import (
    PATHS,
    append_csv,
    append_rejections,
    candidate_path,
    read_csv,
    read_record,
    write_record,
)
from oss_das.enrich import forge_for
from oss_das.models import CatalogStatus, ProjectRecord

#: Why a candidate group is not a catalogue entry; the ledger's vocabulary.
REJECT_REASONS = (
    "not-reusable",
    "paper-code",
    "duplicate",
    "acronym-collision",
    "teaching",
    "no-source",
    "not-das",
)

#: Proposed-included first: those are the ones a reviewer most wants to see.
STATUS_ORDER = {
    CatalogStatus.INCLUDED.value: 0,
    CatalogStatus.WATCHLIST.value: 1,
    CatalogStatus.EXCLUDED.value: 2,
}

TRIAGE_FIELDS = ["key", "verdict", "rule", "reason", "same_as", "model", "date"]


@dataclass(frozen=True)
class Proposal:
    """One ``data/enriched/<id>.md`` as the notebook sees it."""

    id: str
    path: Path
    proposed: dict[str, Any]
    sources: list[str]
    provenance: dict[str, Any] | None
    body: str

    @property
    def status(self) -> str:
        return str(self.proposed.get("status", CatalogStatus.EXCLUDED.value))

    @property
    def summary(self) -> str:
        """The agent's ``## Summary`` paragraph, without the details list."""
        text = self.body
        start = text.find("## Summary")
        end = text.find("## Details")
        if start == -1:
            return text.strip()
        return text[start + len("## Summary") : end if end != -1 else None].strip()


def load_proposals(path: Path | None = None) -> list[Proposal]:
    out = []
    for file in sorted((path or PATHS.enriched).glob("*.md")):
        front, body = read_record(file)
        proposed = front.get("proposed") or {}
        out.append(
            Proposal(
                id=str(proposed.get("id", file.stem)),
                path=file,
                proposed=proposed,
                sources=list(front.get("sources") or []),
                provenance=front.get("provenance"),
                body=body,
            )
        )
    return out


def pending(
    proposals: Iterable[Proposal],
    curated: Iterable[ProjectRecord],
    rejected: Iterable[str] = (),
) -> list[Proposal]:
    """Proposals still owed a decision, in review order.

    A proposal is settled once a curated file carries its id or any of its
    source keys, or once any of its keys sits in the rejection ledger.
    """
    projects = list(curated)
    ids = {project.id for project in projects}
    keys = {key for project in projects for key in project.sources}
    keys |= {project.forge_key for project in projects if project.forge_key}
    keys |= set(rejected)
    open_ = [
        item
        for item in proposals
        if item.id not in ids and not (set(item.sources) & keys)
    ]
    return sorted(open_, key=lambda item: (STATUS_ORDER.get(item.status, 9), item.id))


def vocabulary(projects: Iterable[ProjectRecord], field: str) -> list[str]:
    """Every value the curated set already uses for a list or scalar field."""
    values: set[str] = set()
    for project in projects:
        value = getattr(project, field)
        values.update(value if isinstance(value, list) else [str(value)])
    return sorted(values)


def load_candidate(
    key: str, root: Path | None = None
) -> tuple[dict[str, Any], str] | None:
    path = candidate_path(key, root)
    return read_record(path) if path.exists() else None


# --- accept -------------------------------------------------------------------


def curated_record(
    fields: dict[str, Any],
    *,
    sources: Iterable[str],
    provenance: dict[str, Any] | None,
    today: str | None = None,
) -> ProjectRecord:
    """A validated curated record from the edited form fields.

    The form edits ``repository_url``; the repository path and forge are
    derived from it here so an edited URL cannot disagree with them.
    """
    payload = {
        k: v
        for k, v in fields.items()
        if k not in {"sources", "reviewed_at", "provenance", "repository"}
    }
    url = payload.pop("repository_url", None)
    if url:
        hints = {}
        forge = payload.get("forge") or {}
        if forge.get("host") and forge.get("kind"):
            hints[str(forge["host"]).lower()] = str(forge["kind"])
        kind, host, path = forge_for(url, hints=hints)
        payload["repository"] = path
        payload["repository_url"] = f"https://{host}/{path}"
        payload["forge"] = {"kind": kind, "host": host}
    else:
        payload.pop("forge", None)
    payload["sources"] = sorted(set(sources))
    payload["reviewed_at"] = today or datetime.now(UTC).date().isoformat()
    payload["provenance"] = provenance
    return ProjectRecord.model_validate(payload)


def curated_body(summary: str, notes: str = "") -> str:
    parts = [f"## Summary\n\n{summary.strip()}"] if summary.strip() else []
    if notes.strip():
        parts.append(f"## Reviewer notes\n\n{notes.strip()}")
    return "\n\n".join(parts)


def accept(record: ProjectRecord, body: str, *, path: Path | None = None) -> Path:
    """Write a new curated file; an existing id is a collision, never an overwrite."""
    target = (path or PATHS.curated) / f"{record.id}.md"
    if target.exists():
        raise FileExistsError(f"{target} exists; pick another id or edit that file")
    write_record(target, record.model_dump(mode="json"), body)
    return target


# --- reject -------------------------------------------------------------------


def rejection_entries(
    sources: Iterable[str], reason: str, note: str = ""
) -> dict[str, dict[str, str]]:
    if reason not in REJECT_REASONS:
        raise ValueError(f"reason must be one of {REJECT_REASONS}")
    return {
        key: {"reason": reason, "note": note.strip()} for key in sorted(set(sources))
    }


def reject(
    sources: Iterable[str], reason: str, note: str = "", *, path: Path | None = None
) -> dict[str, dict[str, str]]:
    entries = rejection_entries(sources, reason, note)
    append_rejections(entries, path)
    return entries


# --- spot-check ---------------------------------------------------------------


def latest_rows(rows: Iterable[dict[str, str]]) -> dict[str, dict[str, str]]:
    latest: dict[str, dict[str, str]] = {}
    for row in rows:
        latest[row["key"]] = row
    return latest


def not_das_sample(
    rows: Iterable[dict[str, str]], *, size: int = 20, seed: int | None = None
) -> list[dict[str, str]]:
    """A random sample of current ``not-das`` verdicts, for spot-checking."""
    negatives = [
        row for row in latest_rows(rows).values() if row.get("verdict") == "not-das"
    ]
    return random.Random(seed).sample(negatives, min(size, len(negatives)))


def human_verdict_row(
    key: str, reason: str = "", *, same_as: str = "", today: str | None = None
) -> dict[str, str]:
    """The override row a person appends to triage: verdict das, model human."""
    return {
        "key": key,
        "verdict": "das",
        "rule": "human",
        "reason": reason.strip(),
        "same_as": same_as,
        "model": "human",
        "date": today or datetime.now(UTC).date().isoformat(),
    }


def append_human_verdict(
    key: str, reason: str = "", *, path: Path | None = None
) -> dict[str, str]:
    """Append the override, keeping whatever same-project link the key already has."""
    ledger = path or PATHS.triage
    previous = latest_rows(read_csv(ledger)).get(key, {})
    row = human_verdict_row(key, reason, same_as=previous.get("same_as", ""))
    append_csv(ledger, [row], TRIAGE_FIELDS)
    return row
