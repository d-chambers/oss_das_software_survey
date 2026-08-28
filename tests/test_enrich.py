from __future__ import annotations

from datetime import UTC, datetime

import pytest

from oss_das.core import read_record, write_record
from oss_das.enrich import (
    EnrichedIndex,
    build_prompt,
    candidate_groups,
    catalogued_keys,
    latest_rows,
    parse_result,
    pending_groups,
    propose,
    provenance,
    render_enriched,
    to_record,
    unique_id,
    write_enriched,
)
from oss_das.models import ProjectRecord

ROWS = [
    {"key": "github.com/org/tool", "verdict": "das", "rule": "model", "same_as": ""},
    {
        "key": "pypi/tool",
        "verdict": "das",
        "rule": "same-project",
        "same_as": "github.com/org/tool",
    },
    {
        "key": "conda/tool",
        "verdict": "not-das",
        "rule": "bare-acronym-no-token",
        "same_as": "github.com/org/tool",
    },
    {"key": "github.com/org/other", "verdict": "das", "rule": "model", "same_as": ""},
    {
        "key": "github.com/dasdae/dascore",
        "verdict": "das",
        "rule": "already-catalogued",
        "same_as": "",
    },
    {
        "key": "github.com/org/noise",
        "verdict": "not-das",
        "rule": "model",
        "same_as": "",
    },
    {
        "key": "github.com/org/other",
        "verdict": "not-das",
        "rule": "human",
        "same_as": "",
    },
]

PAYLOAD = {
    "result": (
        "Some narration first.\n```json\n"
        '{"id": "tool", "name": "Tool", "repository_url": "https://github.com/Org/Tool", '
        '"homepage": null, "description": "Reads DAS files.", "status": "included", '
        '"decision_reason": "Reusable reader with a license.", "primary_category": "processing", '
        '"capabilities": ["io", "io", "processing"], "das_focus": "das-native", '
        '"license_spdx": "MIT", "license_class": "osi-approved", '
        '"registries": {"pypi": ["tool"]}, '
        '"publications": [{"doi": "https://doi.org/10.1234/ABC", "role": "canonical"}, {"doi": null}]}'
        "\n```\n\n## Summary\n\nA reader.\n\n## Details\n\n- **Interface:** library\n"
    ),
    "modelUsage": {
        "claude-sonnet-5": {
            "inputTokens": 10,
            "outputTokens": 5,
            "cacheReadInputTokens": 2,
            "cacheCreationInputTokens": 1,
        },
        "claude-haiku-4-5": {"inputTokens": 1, "outputTokens": 1},
    },
    "duration_ms": 12345,
    "num_turns": 4,
    "total_cost_usd": 0.12345,
}


def test_groups_follow_same_as_and_drop_catalogued_and_negative_rows() -> None:
    groups = candidate_groups(latest_rows(ROWS))
    assert groups == {"github.com/org/tool": ["github.com/org/tool", "pypi/tool"]}


def test_a_linked_candidate_alone_still_forms_a_group_with_its_canonical() -> None:
    rows = [
        {
            "key": "pypi/x",
            "verdict": "das",
            "rule": "same-project",
            "same_as": "github.com/a/x",
        }
    ]
    assert candidate_groups(latest_rows(rows)) == {
        "github.com/a/x": ["github.com/a/x", "pypi/x"]
    }


def test_pending_skips_groups_touching_curated_or_enriched_keys(tmp_path) -> None:
    groups = {
        "github.com/a/x": ["github.com/a/x", "pypi/x"],
        "github.com/b/y": ["github.com/b/y"],
        "github.com/c/z": ["github.com/c/z", "pypi/z"],
    }
    project = ProjectRecord.model_validate(
        {
            "id": "x",
            "name": "X",
            "repository": "a/x",
            "description": "d",
            "status": "included",
            "decision_reason": "r",
            "primary_category": "processing",
            "sources": ["pypi/x-old"],
        }
    )
    write_record(tmp_path / "z.md", {"proposed": {"id": "z"}, "sources": ["pypi/z"]})
    enriched = EnrichedIndex.load(tmp_path)
    assert enriched.ids == {"z"}
    assert enriched.keys == {"pypi/z"}
    assert catalogued_keys([project]) == {"github.com/a/x", "pypi/x-old"}
    pending = pending_groups(
        groups, catalogued=catalogued_keys([project]), enriched=enriched
    )
    assert list(pending) == ["github.com/b/y"]
    forced = pending_groups(
        groups,
        catalogued=catalogued_keys([project]),
        enriched=enriched,
        force_ids=["z"],
    )
    assert list(forced) == ["github.com/b/y", "github.com/c/z"]


def test_prompt_carries_evidence_and_the_curated_vocabulary() -> None:
    records = {
        "github.com/org/tool": (
            {
                "key": "github.com/org/tool",
                "name": "tool",
                "probes": ["x"],
                "description": None,
            },
            "# README body",
        ),
    }
    prompt = build_prompt(
        records, capabilities={"io", "processing"}, categories={"processing"}
    )
    assert "### github.com/org/tool" in prompt
    assert "# README body" in prompt
    assert '"probes"' not in prompt
    assert '["io", "processing"]' in prompt
    assert '"das-native"' in prompt


def test_parse_result_takes_the_json_block_and_the_summary_after_it() -> None:
    proposal, body = parse_result(PAYLOAD["result"])
    assert proposal["id"] == "tool"
    assert body.startswith("## Summary")
    with pytest.raises(ValueError, match="json block"):
        parse_result("no json here")


def test_to_record_derives_repository_and_forge_from_the_url() -> None:
    proposal, _ = parse_result(PAYLOAD["result"])
    record = to_record(proposal, hints={})
    assert record.repository == "Org/Tool"
    assert record.forge.host == "github.com"
    assert record.repository_url == "https://github.com/Org/Tool"
    assert record.capabilities == ["io", "processing"]
    assert [item.doi for item in record.publications] == ["10.1234/abc"]

    gitlab = to_record(
        proposal | {"repository_url": "https://git.gfz-potsdam.de/geofon/dastools"},
        hints={"git.gfz-potsdam.de": "gitlab"},
    )
    assert gitlab.forge.kind.value == "gitlab"
    assert gitlab.forge.host == "git.gfz-potsdam.de"

    with pytest.raises(ValueError, match="which API"):
        to_record(proposal | {"repository_url": "https://example.org/a/b"}, hints={})


def test_to_record_accepts_a_registry_only_proposal() -> None:
    proposal, _ = parse_result(PAYLOAD["result"])
    record = to_record(
        proposal | {"repository_url": None, "registries": {"pypi": ["tool"]}}, hints={}
    )
    assert record.repository is None
    assert record.key == "pypi/tool"


def test_invalid_proposal_is_rejected_by_the_schema() -> None:
    proposal, _ = parse_result(PAYLOAD["result"])
    with pytest.raises(Exception, match="status"):
        to_record(proposal | {"status": "maybe"}, hints={})


def test_id_collision_gets_a_numeric_suffix() -> None:
    assert unique_id("tool", set()) == "tool"
    assert unique_id("tool", {"tool"}) == "tool-2"
    assert unique_id("tool", {"tool", "tool-2"}) == "tool-3"


def test_provenance_comes_from_the_response() -> None:
    started = datetime(2026, 8, 28, 12, 0, tzinfo=UTC)
    block = provenance(PAYLOAD, started)
    assert block["agent"] == "das-enricher"
    assert block["models"] == ["claude-haiku-4-5", "claude-sonnet-5"]
    assert block["input_tokens"] == 11
    assert block["output_tokens"] == 6
    assert block["total_tokens"] == 20
    assert block["duration_seconds"] == 12.3
    assert block["turns"] == 4
    assert block["api_list_cost_usd"] == 0.1235
    assert block["ran_at"] == "2026-08-28T12:00:00+00:00"


def test_propose_renders_a_validated_enriched_file(tmp_path) -> None:
    result = {"payload": PAYLOAD, "started": datetime(2026, 8, 28, tzinfo=UTC)}
    front, body = propose(
        result,
        sources=["pypi/tool", "github.com/org/tool"],
        hints={},
        taken_ids={"tool"},
    )
    assert front["proposed"]["id"] == "tool-2"
    assert front["sources"] == ["github.com/org/tool", "pypi/tool"]
    assert set(front) == {"proposed", "sources", "provenance"}
    assert "sources" not in front["proposed"]
    ProjectRecord.model_validate(front["proposed"])
    target = write_enriched(front, body, path=tmp_path)
    assert target.name == "tool-2.md"
    stored, stored_body = read_record(target)
    assert stored["proposed"]["repository"] == "Org/Tool"
    assert stored_body.startswith("## Summary")


def test_propose_raises_and_writes_nothing_on_error_or_bad_json() -> None:
    with pytest.raises(ValueError, match="timed out"):
        propose({"error": "timed out after 1s"}, sources=[], hints={}, taken_ids=set())
    broken = {
        "payload": {**PAYLOAD, "result": '```json\n{"id": "BAD ID"}\n```'},
        "started": datetime.now(UTC),
    }
    with pytest.raises(ValueError):
        propose(broken, sources=[], hints={}, taken_ids=set())


def test_render_enriched_excludes_review_only_fields() -> None:
    record = to_record(parse_result(PAYLOAD["result"])[0], hints={})
    front = render_enriched(record, sources=["b", "a"], provenance={"agent": "x"})
    assert front["sources"] == ["a", "b"]
    assert "reviewed_at" not in front["proposed"]
    assert "provenance" not in front["proposed"]
