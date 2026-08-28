"""The deterministic triage rules in scripts/a020_triage.py."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "a020_triage.py"


@pytest.fixture(scope="module")
def triage():
    spec = importlib.util.spec_from_file_location("a020_triage", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _forge(key="github.com/org/tool", **overrides):
    front = {
        "key": key,
        "source": "forge",
        "name": key.split("/")[-1],
        "description": None,
        "probe_class": "broad-acronym",
    }
    return front | overrides


def _decide(triage, front, *, rejected=None, catalogued=None, forge_keys=None):
    return triage.deterministic(
        front,
        rejected=rejected or {},
        catalogued=catalogued or {},
        forge_keys=forge_keys or {},
    )


def test_rejected_ledger_wins_before_anything_else(triage) -> None:
    front = _forge(
        probe_class="domain-specific", description="distributed acoustic sensing"
    )
    row = _decide(
        triage, front, rejected={front["key"]: {"reason": "paper-code", "note": ""}}
    )
    assert row["verdict"] == "not-das"
    assert row["rule"] == "rejected-ledger"
    assert row["reason"] == "paper-code"


def test_catalogued_key_is_das_with_the_project_id_as_reason(triage) -> None:
    row = _decide(triage, _forge(), catalogued={"github.com/org/tool": "tool"})
    assert row == {"verdict": "das", "rule": "already-catalogued", "reason": "tool"}


def test_bare_acronym_with_no_token_is_not_das(triage) -> None:
    row = _decide(triage, _forge(description="A dashboard for sales."))
    assert row["verdict"] == "not-das"
    assert row["rule"] == "bare-acronym-no-token"


def test_broad_hit_with_domain_vocabulary_survives_to_the_model(triage) -> None:
    assert _decide(triage, _forge(description="Fiber optic strain readers.")) is None
    assert (
        _decide(triage, _forge(name="das-toolkit", description="Tools for DAS data."))
        is None
    )


def test_domain_specific_probe_survives_without_a_token(triage) -> None:
    assert _decide(triage, _forge(probe_class="domain-specific")) is None


def test_registry_candidate_declaring_a_known_forge_key_is_linked(triage) -> None:
    front = {
        "key": "pypi/tool",
        "source": "pypi",
        "name": "tool",
        "description": "DAS processing",
        "repository_url": "https://github.com/Org/Tool",
        "probe_class": "domain-specific",
    }
    row = _decide(
        triage, front, forge_keys={"github.com/org/tool": "github.com/org/tool"}
    )
    assert row["verdict"] == "das"
    assert row["rule"] == "same-project"
    assert row["same_as"] == "github.com/org/tool"


def test_link_is_kept_even_when_the_registry_hit_is_dropped_as_bare(triage) -> None:
    """The same_as column is evidence for grouping whichever way the verdict went."""
    front = {
        "key": "pypi/tool",
        "source": "pypi",
        "name": "tool",
        "description": "nothing relevant",
        "repository_url": "https://github.com/org/tool",
        "probe_class": "broad-acronym",
    }
    row = _decide(
        triage, front, forge_keys={"github.com/org/tool": "github.com/org/tool"}
    )
    assert row["rule"] == "bare-acronym-no-token"
    assert row["same_as"] == "github.com/org/tool"


def test_unknown_declared_repository_is_not_linked(triage) -> None:
    front = {
        "key": "pypi/tool",
        "source": "pypi",
        "name": "tool",
        "description": "fiber sensing",
        "repository_url": "https://github.com/org/elsewhere",
        "probe_class": "domain-specific",
    }
    assert _decide(triage, front, forge_keys={"github.com/org/tool": "x"}) is None


def test_last_row_per_key_wins(triage) -> None:
    rows = [
        {"key": "a", "verdict": "not-das", "model": "deterministic"},
        {"key": "b", "verdict": "das", "model": "haiku"},
        {"key": "a", "verdict": "das", "model": "human"},
    ]
    latest = triage.decided_keys(rows)
    assert latest["a"]["verdict"] == "das"
    assert latest["a"]["model"] == "human"
    assert latest["b"]["verdict"] == "das"


def test_shipped_ledger_has_the_documented_columns(triage) -> None:
    from oss_das.core import PATHS, read_csv

    rows = read_csv(PATHS.triage)
    assert rows, "the repository ships a triage ledger"
    assert set(rows[0]) == set(triage.TRIAGE_FIELDS)
