from __future__ import annotations

from pathlib import Path

import plotly.graph_objects as go
import pytest

from oss_das import core, site
from oss_das.core import ProjectPaths


def test_render_page_embeds_plotly_for_offline_use(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(site, "PATHS", ProjectPaths(tmp_path))
    output = site.render_page(
        "index.html",
        title="Test",
        heading="Test page",
        lede="An offline chart.",
        snapshot_date="2026-08-03",
        figures=[go.Figure(go.Bar(x=[1], y=[2]))],
    )
    rendered = output.read_text()
    assert "plotly.js" in rendered
    assert '<script src="https://cdn.plot.ly' not in rendered
    assert "Test page" in rendered


def test_render_page_is_byte_identical_across_rebuilds(
    tmp_path: Path, monkeypatch
) -> None:
    """Plotly's default random div id would otherwise break reproducibility."""
    monkeypatch.setattr(site, "PATHS", ProjectPaths(tmp_path))

    def build() -> str:
        return site.render_page(
            "index.html",
            title="Test",
            heading="Test page",
            lede="An offline chart.",
            snapshot_date="2026-08-03",
            figures=[go.Figure(go.Bar(x=[1], y=[2])), go.Figure(go.Bar(x=[3], y=[4]))],
        ).read_text()

    assert build() == build()


def test_health_heatmap_leaves_unobserved_signals_empty() -> None:
    """A failed GitHub fetch must not look identical to a confirmed absence."""
    figures = site.health_figures(
        {
            "projects": [
                {
                    "id": "seen",
                    "name": "Seen",
                    "status": "included",
                    "days_since_push": "3",
                    "lines_of_code_estimate": "100",
                    "has_docs": "True",
                    "has_tests": "False",
                    "has_ci": "True",
                },
                {
                    "id": "unseen",
                    "name": "Unseen",
                    "status": "included",
                    "days_since_push": "",
                    "lines_of_code_estimate": "",
                    "has_docs": "",
                    "has_tests": "",
                    "has_ci": "",
                },
            ]
        }
    )
    assert list(figures[1].data[0].x) == [100.0]
    assert list(figures[2].data[0].z) == [[1, 0, 1], [None, None, None]]


def test_load_plot_data_reads_project_records(tmp_path: Path, monkeypatch) -> None:
    """Charts use the project records rather than a duplicate CSV view."""
    paths = ProjectPaths(tmp_path)
    paths.curated.mkdir(parents=True)
    (paths.curated / "example.md").write_text(
        """---
curated:
  id: example
  name: Example
  repository: owner/example
  description: A test project.
  status: included
  decision_reason: Reviewed.
  primary_category: processing
  capabilities: [io]
  license_spdx: MIT
  license_class: osi-approved
  publications:
    - doi: 10.1234/example
      role: canonical
collected:
  snapshot: '2026-08-03'
  language: Python
  stars: 12
  pypi_downloads_30d: 34
  lines_of_code_estimate: 56
  canonical_citations: 0
  last_commit_at: '2026-08-01T00:00:00Z'
  has_docs: true
  has_tests: false
  has_ci: true
---

# Example
"""
    )
    monkeypatch.setattr(core, "PATHS", paths)
    monkeypatch.setattr(site, "PATHS", paths)

    data = site.load_plot_data("2026-08-03")

    assert data["projects"][0]["days_since_push"] == "2"
    assert data["projects"][0]["lines_of_code_estimate"] == "56"
    assert data["projects"][0]["has_tests"] == "False"
    assert data["metrics"] == [
        {
            "project_id": "example",
            "metric": "repo_stars",
            "value": "12",
            "unit": "stars",
        },
        {
            "project_id": "example",
            "metric": "pypi_downloads_30d",
            "value": "34",
            "unit": "downloads",
        },
        {
            "project_id": "example",
            "metric": "canonical_citations",
            "value": "0",
            "unit": "citations",
        },
    ]
    assert data["capabilities"] == [
        {
            "project_id": "example",
            "capability": "io",
            "present": "True",
            "source": "curated",
        }
    ]
    assert data["publications"][0]["missing_reason"] == ""


def test_load_plot_data_rejects_mixed_snapshot_dates(
    tmp_path: Path, monkeypatch
) -> None:
    paths = ProjectPaths(tmp_path)
    paths.curated.mkdir(parents=True)
    (paths.curated / "example.md").write_text(
        """---
curated:
  id: example
  name: Example
  repository: owner/example
  description: A test project.
  status: included
  decision_reason: Reviewed.
  primary_category: processing
  license_spdx: MIT
  license_class: osi-approved
collected:
  snapshot: '2026-08-02'
---
"""
    )
    monkeypatch.setattr(core, "PATHS", paths)
    monkeypatch.setattr(site, "PATHS", paths)

    with pytest.raises(ValueError, match="2026-08-02, not 2026-08-03"):
        site.load_plot_data("2026-08-03")


def _catalog_data(**overrides) -> dict:
    data = {
        "projects": [
            {
                "id": "example",
                "name": "<Example>",
                "status": "included",
                "primary_category": "processing",
                "license_spdx": "MIT",
                "license_class": "osi-approved",
                "capabilities": "io",
                "repository": "owner/example",
                "repository_url": "https://github.com/owner/example",
                "decision_reason": "Safe & reviewed",
            }
        ],
        "metrics": [],
        "publications": [],
    }
    return data | overrides


def test_catalog_escapes_project_content() -> None:
    rendered = site.catalog_html(_catalog_data())
    assert "&lt;Example&gt;" in rendered
    assert "Safe &amp; reviewed" in rendered


def test_catalog_states_reason_instead_of_zero_for_missing_metrics() -> None:
    rendered = site.catalog_html(
        _catalog_data(
            metrics=[
                {
                    "project_id": "example",
                    "metric": "repo_stars",
                    "value": "1234",
                    "missing_reason": "",
                },
                {
                    "project_id": "example",
                    "metric": "pypi_downloads_30d",
                    "value": "",
                    "missing_reason": "fetch_error",
                },
            ]
        )
    )
    assert "1,234" in rendered
    assert "not retrieved" in rendered
    assert ">0<" not in rendered


def test_catalog_links_resolved_canonical_publication() -> None:
    rendered = site.catalog_html(
        _catalog_data(
            publications=[
                {
                    "project_id": "example",
                    "doi": "10.1234/example",
                    "role": "canonical",
                    "title": "Example paper",
                    "publication_year": "2025",
                    "missing_reason": "",
                }
            ]
        )
    )
    assert "https://doi.org/10.1234/example" in rendered
    assert "Example paper" in rendered
    assert "(2025)" in rendered
