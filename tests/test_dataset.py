from __future__ import annotations

import json
from pathlib import Path

import pytest

from oss_das.core import ProjectPaths, load_projects, read_csv, write_jsonl
from oss_das.dataset import (
    _julia_status,
    _registry_total,
    build_snapshot,
    validate_snapshot,
)


def _write_project(path: Path) -> None:
    """Write one project file in the merged layout the loader now expects."""
    path.mkdir(parents=True)
    (path / "example.md").write_text(
        """---
curated:
  id: example
  name: Example
  repository: owner/example
  description: Example DAS package.
  status: included
  decision_reason: Meets the policy.
  primary_category: processing
  capabilities: [io, processing]
  license_spdx: MIT
  license_class: osi-approved
  registries:
    pypi: [example]
    conda: [conda-forge/example]
  publications:
    - doi: 10.1234/example
      role: canonical
collected:
  stars: 5
---

# Example

Prose written by an agent.
"""
    )


def test_build_and_validate_snapshot(tmp_path: Path) -> None:
    paths = ProjectPaths(tmp_path)
    _write_project(paths.curated)
    raw = paths.raw("2026-08-03")
    write_jsonl(
        raw / "github.jsonl",
        [
            {
                "project_id": "example",
                "source_url": "https://api.github.com/repos/owner/example",
                "fetched_at": "2026-08-03T00:00:00+00:00",
                "stars": 5,
                "forks": 2,
                "contributors": 3,
                "release_count": 4,
                "created_at": "2020-01-01T00:00:00Z",
                "pushed_at": "2026-08-01T00:00:00Z",
                "latest_release_at": "2026-07-01T00:00:00Z",
                "archived": False,
                "language": "Python",
                "has_docs": True,
                "has_tests": True,
                "has_ci": True,
            }
        ],
    )
    write_jsonl(
        raw / "packages.jsonl",
        [
            {
                "project_id": "example",
                "registry": "pypi",
                "name": "example",
                "source_url": "https://pypi.org/pypi/example/json",
                "stats_source_url": "https://pypistats.org/api/packages/example/recent",
                "fetched_at": "2026-08-03T00:00:00+00:00",
                "downloads_last_month": 30,
                "requires_dist": ["numpy>=1.26", "docs-only; extra == 'docs'"],
            },
            {
                "project_id": "example",
                "registry": "conda",
                "source_url": "https://api.anaconda.org/package/conda-forge/example",
                "fetched_at": "2026-08-03T00:00:00+00:00",
                "downloads_cumulative": 20,
            },
        ],
    )
    write_jsonl(
        raw / "pypi_daily.jsonl",
        [
            {
                "project_id": "example",
                "package": "example",
                "date": "2026-08-01",
                "downloads": 3,
                "category": "without_mirrors",
                "source_url": "https://pypistats.org/api/packages/example/overall",
                "fetched_at": "2026-08-03T00:00:00+00:00",
            }
        ],
    )
    write_jsonl(
        raw / "publications.jsonl",
        [
            {
                "project_id": "example",
                "doi": "10.1234/example",
                "role": "canonical",
                "title": "Example paper",
                "publication_year": 2025,
                "work_type": "article",
                "cited_by_count": 7,
                "openalex_id": "https://openalex.org/W1",
                "source_url": "https://api.openalex.org/works/1",
                "fetched_at": "2026-08-03T00:00:00+00:00",
                "missing_reason": None,
            }
        ],
    )

    snapshot = build_snapshot("2026-08-03", paths=paths)
    validate_snapshot("2026-08-03", paths=paths)
    metrics = {
        item["metric"]: item["value"] for item in read_csv(snapshot / "metrics.csv")
    }
    assert metrics["repo_stars"] == "5"
    assert metrics["pypi_downloads_180d"] == "3"
    assert metrics["canonical_citations"] == "7"
    dependencies = read_csv(snapshot / "dependencies.csv")
    assert dependencies[0]["dependency"] == "numpy"
    assert dependencies[0]["requirement"] == ">=1.26"
    manifest = json.loads((snapshot / "manifest.json").read_text())
    assert manifest["included_count"] == 1


def test_partial_registry_totals_are_withheld_not_summed() -> None:
    """One unreachable package makes any project total a guess, so report none."""
    records = [
        {"registry": "pypi", "downloads_last_month": 100, "stats_missing_reason": None},
        {"registry": "pypi", "stats_missing_reason": "fetch_error"},
    ]
    value, reason = _registry_total(
        records, "downloads_last_month", "stats_missing_reason", "missing_reason"
    )
    assert value is None
    assert reason == "fetch_error"


def test_unpublished_package_contributes_a_genuine_zero_to_a_total() -> None:
    records = [
        {"registry": "pypi", "downloads_last_month": 100, "stats_missing_reason": None},
        {"registry": "pypi", "missing_reason": "not_published"},
    ]
    assert _registry_total(
        records, "downloads_last_month", "stats_missing_reason", "missing_reason"
    ) == (100, None)


def test_a_wholly_unpublished_registry_reports_no_total() -> None:
    assert _registry_total([], "downloads_last_month", "missing_reason") == (
        None,
        "not_published",
    )
    assert _registry_total(
        [{"missing_reason": "not_published"}], "downloads_last_month", "missing_reason"
    ) == (None, "not_published")


def test_complete_registry_records_are_summed() -> None:
    records = [
        {"downloads_cumulative": 20},
        {"downloads_cumulative": 5},
    ]
    assert _registry_total(records, "downloads_cumulative", "missing_reason") == (
        25,
        None,
    )


def test_julia_status_distinguishes_unregistered_from_unchecked() -> None:
    """A package absent from General is a finding; an unread one is a gap."""
    assert _julia_status([], []) == "not_applicable"
    assert _julia_status(["Tool"], [{"registered": True}]) == "registered"
    assert (
        _julia_status(
            ["Tool"], [{"registered": False, "missing_reason": "not_published"}]
        )
        == "unregistered"
    )
    assert (
        _julia_status(
            ["Tool"], [{"registered": False, "missing_reason": "fetch_error"}]
        )
        == "unknown"
    )
    assert _julia_status(["Tool", "Other"], [{"registered": True}]) == "unknown"


def test_a_per_field_reason_beats_the_whole_record_reason(tmp_path: Path) -> None:
    """A host that closes one endpoint must not blank every repository metric."""
    paths = ProjectPaths(tmp_path)
    _write_project(paths.curated)
    raw = paths.raw("2026-08-03")
    write_jsonl(
        raw / "github.jsonl",
        [
            {
                "project_id": "example",
                "source_url": "https://git.example.org/api/v4/projects/1",
                "fetched_at": "2026-08-03T00:00:00+00:00",
                "stars": 5,
                "forks": 2,
                "contributors": None,
                "contributors_missing_reason": "unavailable",
                "release_count": 4,
                "missing_reason": None,
            }
        ],
    )
    for name in ("packages", "publications", "pypi_daily"):
        write_jsonl(raw / f"{name}.jsonl", [])
    build_snapshot("2026-08-03", paths=paths)

    metrics = {
        item["metric"]: item
        for item in read_csv(paths.snapshot("2026-08-03") / "metrics.csv")
    }
    assert metrics["repo_stars"]["value"] == "5"
    assert metrics["repo_contributors"]["value"] == ""
    assert metrics["repo_contributors"]["missing_reason"] == "unavailable"


def test_a_curated_doi_with_no_collected_record_is_unavailable(
    tmp_path: Path,
) -> None:
    """A curated canonical DOI that collection has not seen is uncollected.

    ``not_applicable`` asserts the project has no publication at all, which is
    false once a DOI is curated. Reporting it that way would turn a value
    nobody fetched into a confirmed absence.
    """
    paths = ProjectPaths(tmp_path)
    _write_project(paths.curated)
    raw = paths.raw("2026-08-03")
    for name in ("github", "packages", "publications", "pypi_daily"):
        write_jsonl(raw / f"{name}.jsonl", [])
    build_snapshot("2026-08-03", paths=paths)

    row = next(
        item
        for item in read_csv(paths.snapshot("2026-08-03") / "metrics.csv")
        if item["metric"] == "canonical_citations"
    )
    assert row["value"] == ""
    assert row["missing_reason"] == "unavailable"


def test_validation_rejects_a_license_class_that_contradicts_the_spdx_id(
    tmp_path: Path,
) -> None:
    paths = ProjectPaths(tmp_path)
    _write_project(paths.curated)
    raw = paths.raw("2026-08-03")
    write_jsonl(raw / "github.jsonl", [])
    for name in ("packages", "publications", "pypi_daily"):
        write_jsonl(raw / f"{name}.jsonl", [])
    snapshot = build_snapshot("2026-08-03", paths=paths)

    rows = read_csv(snapshot / "projects.csv")
    assert rows[0]["license_class"] == "osi-approved"
    text = (snapshot / "projects.csv").read_text()
    (snapshot / "projects.csv").write_text(text.replace("MIT", ""))
    with pytest.raises(ValueError, match="contradicts the SPDX id"):
        validate_snapshot("2026-08-03", paths=paths)


def test_loader_reads_curation_and_ignores_generated_blocks(tmp_path: Path) -> None:
    """collected/summary are rebuilt, so they must not widen the curated schema."""
    paths = ProjectPaths(tmp_path)
    _write_project(paths.curated)

    projects = load_projects(paths.curated)

    assert [project.id for project in projects] == ["example"]
    assert projects[0].capabilities == ["io", "processing"]


def test_loader_rejects_a_file_with_no_curated_block(tmp_path: Path) -> None:
    paths = ProjectPaths(tmp_path)
    paths.curated.mkdir(parents=True)
    (paths.curated / "broken.md").write_text("---\ncollected:\n  stars: 1\n---\n\nx\n")

    with pytest.raises(ValueError, match="no curated block"):
        load_projects(paths.curated)
