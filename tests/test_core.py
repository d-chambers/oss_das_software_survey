from __future__ import annotations

from pathlib import Path

import pytest

from oss_das.core import (
    append_csv,
    append_rejections,
    candidate_key,
    candidate_path,
    load_projects,
    load_rejections,
    read_csv,
    read_record,
    write_record,
)

CURATED = {
    "id": "example",
    "name": "Example",
    "repository": "Owner/Repo",
    "description": "A reusable DAS tool.",
    "status": "included",
    "decision_reason": "Meets the policy.",
    "primary_category": "processing",
}


def test_record_round_trips_frontmatter_and_body(tmp_path: Path) -> None:
    path = tmp_path / "x.md"
    write_record(
        path, {"key": "pypi/x", "n": 3, "flags": {"a": True}}, "## Summary\n\nProse."
    )
    front, body = read_record(path)
    assert front == {"key": "pypi/x", "n": 3, "flags": {"a": True}}
    assert body == "## Summary\n\nProse."


def test_record_without_body_has_no_trailing_prose(tmp_path: Path) -> None:
    path = tmp_path / "x.md"
    write_record(path, {"key": "pypi/x"})
    assert path.read_text().endswith("---\n")
    assert read_record(path) == ({"key": "pypi/x"}, "")


def test_record_without_frontmatter_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "x.md"
    path.write_text("# just prose\n")
    with pytest.raises(ValueError, match="frontmatter"):
        read_record(path)


def test_candidate_keys_are_lowercase_and_nested_paths_fold_into_one_file() -> None:
    key = candidate_key("gitlab.com", "Group/Sub/Repo")
    assert key == "gitlab.com/group/sub/repo"
    assert candidate_path(key).name == "group--sub--repo.md"
    assert candidate_path(key).parent.name == "gitlab.com"
    assert candidate_path("pypi/daspal").parent.name == "pypi"


def test_append_csv_writes_the_header_once(tmp_path: Path) -> None:
    path = tmp_path / "ledger.csv"
    fields = ["key", "verdict"]
    assert append_csv(path, [{"key": "a", "verdict": "das"}], fields) == 1
    assert (
        append_csv(path, [{"key": "b", "verdict": "not-das", "extra": 1}], fields) == 1
    )
    rows = read_csv(path)
    assert rows == [{"key": "a", "verdict": "das"}, {"key": "b", "verdict": "not-das"}]
    assert path.read_text().count("key,verdict") == 1


def test_load_projects_reads_curated_frontmatter_and_rejects_duplicates(
    tmp_path: Path,
) -> None:
    write_record(tmp_path / "example.md", CURATED, "## Summary\n\nProse.")
    (projects,) = load_projects(tmp_path)
    assert projects.id == "example"
    assert projects.forge_key == "github.com/owner/repo"
    write_record(tmp_path / "other.md", {**CURATED, "id": "other"})
    with pytest.raises(ValueError, match="unique"):
        load_projects(tmp_path)


def test_rejections_merge_and_lowercase_their_keys(tmp_path: Path) -> None:
    path = tmp_path / "rejected.yml"
    append_rejections({"GitHub.com/A/B": {"reason": "duplicate", "note": ""}}, path)
    append_rejections(
        {"pypi/x": {"reason": "acronym-collision", "note": "German"}}, path
    )
    ledger = load_rejections(path)
    assert set(ledger) == {"github.com/a/b", "pypi/x"}
    assert ledger["pypi/x"] == {"reason": "acronym-collision", "note": "German"}
