from __future__ import annotations

from pathlib import Path

import pytest

from oss_das.core import load_rejections, read_csv, read_record, write_record
from oss_das.models import ProjectRecord
from oss_das.review import (
    Proposal,
    accept,
    append_human_verdict,
    curated_body,
    curated_record,
    human_verdict_row,
    load_proposals,
    not_das_sample,
    pending,
    reject,
    rejection_entries,
    vocabulary,
)

PROPOSED = {
    "id": "tool",
    "name": "Tool",
    "repository": "Org/Tool",
    "repository_url": "https://github.com/Org/Tool",
    "homepage": None,
    "description": "Reads DAS files.",
    "status": "included",
    "decision_reason": "Reusable reader.",
    "primary_category": "processing",
    "capabilities": ["io"],
    "das_focus": "das-native",
    "license_spdx": "MIT",
    "license_class": "osi-approved",
    "forge": {"kind": "github", "host": "github.com"},
    "registries": {"pypi": ["tool"], "conda": [], "julia": []},
    "publications": [],
}


def _proposal(id, status, sources=(), **overrides):
    proposed = PROPOSED | {"id": id, "status": status} | overrides
    return Proposal(
        id=id,
        path=Path(f"{id}.md"),
        proposed=proposed,
        sources=list(sources),
        provenance={"agent": "x"},
        body="## Summary\n\nText.\n\n## Details\n\n- x",
    )


def _project(id, repository, sources=()):
    return ProjectRecord.model_validate(
        {
            "id": id,
            "name": id,
            "repository": repository,
            "description": "d",
            "status": "included",
            "decision_reason": "r",
            "primary_category": "processing",
            "capabilities": ["io", "viz"],
            "sources": list(sources),
        }
    )


def test_pending_orders_included_then_watchlist_then_excluded_and_hides_reviewed() -> (
    None
):
    proposals = [
        _proposal("z-excluded", "excluded", ["github.com/z/z"]),
        _proposal("b-watch", "watchlist", ["github.com/b/b"]),
        _proposal("a-included", "included", ["github.com/a/a"]),
        _proposal("by-id", "included", ["github.com/q/q"]),
        _proposal("by-key", "included", ["pypi/k", "github.com/k/k"]),
        _proposal("by-forge", "included", ["github.com/f/f"]),
    ]
    curated = [
        _project("by-id", "x/y"),
        _project("other", "o/o", sources=["pypi/k"]),
        _project("forge", "F/F"),
    ]
    assert [item.id for item in pending(proposals, curated)] == [
        "a-included",
        "b-watch",
        "z-excluded",
    ]
    settled = pending(proposals, curated, rejected={"github.com/b/b"})
    assert [item.id for item in settled] == ["a-included", "z-excluded"]


def test_vocabulary_collects_list_and_scalar_fields() -> None:
    projects = [_project("a", "a/a"), _project("b", "b/b")]
    assert vocabulary(projects, "capabilities") == ["io", "viz"]
    assert vocabulary(projects, "primary_category") == ["processing"]


def test_load_proposals_reads_enriched_files(tmp_path) -> None:
    write_record(
        tmp_path / "tool.md",
        {"proposed": PROPOSED, "sources": ["pypi/tool"], "provenance": {"agent": "x"}},
        "## Summary\n\nHi.\n\n## Details\n\n- a",
    )
    [item] = load_proposals(tmp_path)
    assert item.id == "tool"
    assert item.sources == ["pypi/tool"]
    assert item.summary == "Hi."


def _form_values(**overrides):
    """What the notebook form hands over: no repository path, URL editable."""
    values = {k: v for k, v in PROPOSED.items() if k != "repository"}
    return values | overrides


def test_curated_record_adds_review_fields_and_validates(tmp_path) -> None:
    edited = _form_values(capabilities=["processing", "io"])
    record = curated_record(
        edited,
        sources=["pypi/tool", "github.com/org/tool"],
        provenance={"agent": "x"},
        today="2026-08-28",
    )
    assert record.sources == ["github.com/org/tool", "pypi/tool"]
    assert record.reviewed_at == "2026-08-28"
    assert record.provenance == {"agent": "x"}
    assert record.capabilities == ["io", "processing"]
    assert record.repository == "Org/Tool"
    assert record.forge.host == "github.com"

    target = accept(record, curated_body("A summary.", "Looks right."), path=tmp_path)
    front, body = read_record(target)
    assert ProjectRecord.model_validate(front).id == "tool"
    assert body == "## Summary\n\nA summary.\n\n## Reviewer notes\n\nLooks right."

    with pytest.raises(FileExistsError, match="exists"):
        accept(record, "", path=tmp_path)


def test_an_edited_url_redefines_repository_and_forge() -> None:
    moved = _form_values(
        repository_url="https://git.gfz-potsdam.de/geofon/dastools/",
        forge={"kind": "gitlab", "host": "git.gfz-potsdam.de"},
    )
    record = curated_record(moved, sources=[], provenance=None)
    assert record.repository == "geofon/dastools"
    assert record.forge.kind.value == "gitlab"
    assert record.repository_url == "https://git.gfz-potsdam.de/geofon/dastools"

    registry_only = _form_values(
        repository_url=None, forge={"kind": "github", "host": "github.com"}
    )
    record = curated_record(registry_only, sources=["pypi/tool"], provenance=None)
    assert record.repository is None
    assert record.repository_url is None


def test_curated_record_rejects_an_unknown_host() -> None:
    with pytest.raises(ValueError, match="which API"):
        curated_record(
            _form_values(repository_url="https://example.org/a/b", forge=None),
            sources=[],
            provenance=None,
        )


def test_curated_body_without_notes_is_just_the_summary() -> None:
    assert curated_body("S") == "## Summary\n\nS"
    assert curated_body("", "") == ""


def test_rejection_entries_cover_every_source_with_a_vocabulary_reason(
    tmp_path,
) -> None:
    entries = rejection_entries(
        ["pypi/tool", "github.com/org/tool"], "paper-code", " scripts for one paper "
    )
    assert entries == {
        "github.com/org/tool": {
            "reason": "paper-code",
            "note": "scripts for one paper",
        },
        "pypi/tool": {"reason": "paper-code", "note": "scripts for one paper"},
    }
    with pytest.raises(ValueError, match="reason"):
        rejection_entries(["x"], "meh")

    ledger = tmp_path / "rejected.yml"
    reject(["pypi/tool"], "not-das", path=ledger)
    reject(["github.com/org/tool"], "duplicate", "same as tool", path=ledger)
    assert set(load_rejections(ledger)) == {"pypi/tool", "github.com/org/tool"}


def test_not_das_sample_uses_the_latest_row_per_key() -> None:
    rows = [
        {"key": "a", "verdict": "not-das"},
        {"key": "b", "verdict": "not-das"},
        {"key": "a", "verdict": "das", "model": "human"},
        {"key": "c", "verdict": "das"},
    ]
    assert [row["key"] for row in not_das_sample(rows, size=20, seed=1)] == ["b"]
    assert not_das_sample([], size=5) == []


def test_human_verdict_row_overrides_triage(tmp_path) -> None:
    row = human_verdict_row(
        "github.com/org/tool", "reader for iDAS files", today="2026-08-28"
    )
    assert row == {
        "key": "github.com/org/tool",
        "verdict": "das",
        "rule": "human",
        "reason": "reader for iDAS files",
        "same_as": "",
        "model": "human",
        "date": "2026-08-28",
    }
    ledger = tmp_path / "triage.csv"
    append_human_verdict("pypi/x", path=ledger)
    assert read_csv(ledger)[0]["model"] == "human"


def test_human_override_keeps_an_existing_same_project_link(tmp_path) -> None:
    ledger = tmp_path / "triage.csv"
    ledger.write_text(
        "key,verdict,rule,reason,same_as,model,date\n"
        "pypi/x,not-das,bare-acronym-no-token,,github.com/o/x,deterministic,d\n"
    )
    row = append_human_verdict("pypi/x", "reader", path=ledger)
    assert row["same_as"] == "github.com/o/x"
    assert read_csv(ledger)[-1]["same_as"] == "github.com/o/x"
