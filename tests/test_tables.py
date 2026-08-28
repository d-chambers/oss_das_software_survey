from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from oss_das.models import ProjectRecord

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "c010_build_tables.py"
spec = importlib.util.spec_from_file_location("c010", SCRIPT)
c010 = importlib.util.module_from_spec(spec)
sys.modules["c010"] = c010
spec.loader.exec_module(c010)


def test_cells_flatten_lists_and_mappings_and_keep_blanks_blank() -> None:
    assert c010.cell(None) == ""
    assert c010.cell(0) == "0"
    assert c010.cell(True) == "True"
    assert c010.cell(["a", "b"]) == "a;b"
    assert c010.cell({"Python": 12, "Shell": 3}) == "Python=12;Shell=3"


def test_curated_row_carries_identity_scope_and_canonical_doi() -> None:
    project = ProjectRecord.model_validate(
        {
            "id": "dascore",
            "name": "DASCore",
            "repository": "DASDAE/dascore",
            "description": "d",
            "status": "included",
            "decision_reason": "r",
            "primary_category": "core-framework",
            "capabilities": ["io", "processing"],
            "registries": {"pypi": ["dascore"], "conda": ["conda-forge/dascore"]},
            "publications": [
                {"doi": "10.1/related", "role": "related"},
                {"doi": "10.1/canon", "role": "canonical"},
            ],
            "reviewed_at": "2026-08-28",
        }
    )
    row = c010.curated_row(project)
    assert row["owner"] == "DASDAE"
    assert row["forge_host"] == "github.com"
    assert row["capabilities"] == "io;processing"
    assert row["pypi"] == "dascore"
    assert row["canonical_doi"] == "10.1/canon"
    assert row["das_focus"] == "das-native"


def test_registry_only_project_has_blank_forge_columns() -> None:
    project = ProjectRecord.model_validate(
        {
            "id": "daspal",
            "name": "DASPAL",
            "description": "d",
            "status": "included",
            "decision_reason": "r",
            "primary_category": "processing",
            "registries": {"pypi": ["daspal"]},
        }
    )
    row = c010.curated_row(project)
    assert row["repository"] == "" and row["forge_host"] == "" and row["owner"] == ""


def test_every_measured_column_maps_to_a_known_source() -> None:
    sources = {source for _, source, _ in c010.MEASURED_COLUMNS}
    assert sources <= set(c010.MEASURED_SOURCES)
    assert len(c010.FIELDS) == len(set(c010.FIELDS))
