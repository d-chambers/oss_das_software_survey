"""The published notebook runs headlessly and its slides layout matches its cells."""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

import pytest

NOTEBOOKS = Path(__file__).resolve().parent.parent / "notebooks"
NOTEBOOK = NOTEBOOKS / "ecosystem.py"
LAYOUT = NOTEBOOKS / "layouts" / "ecosystem.slides.json"


@pytest.fixture(scope="module")
def notebook():
    spec = importlib.util.spec_from_file_location("ecosystem_notebook", NOTEBOOK)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def run(notebook):
    outputs, defs = notebook.app.run()
    return outputs, defs


class TestLayout:
    def test_declares_the_slides_layout(self):
        assert 'layout_file="layouts/ecosystem.slides.json"' in NOTEBOOK.read_text()

    def test_one_layout_entry_per_cell(self):
        layout = json.loads(LAYOUT.read_text())
        cells = len(re.findall(r"^@app\.cell", NOTEBOOK.read_text(), re.MULTILINE))
        assert layout["type"] == "slides"
        assert len(layout["data"]["cells"]) == cells
        assert {c["type"] for c in layout["data"]["cells"]} <= {
            "slide",
            "sub-slide",
            "fragment",
            "skip",
        }

    def test_declares_browser_dependencies(self):
        # marimo's WASM runtime installs only what the inline script metadata names.
        header = NOTEBOOK.read_text().split("# ///", 2)[1]
        assert '"pandas"' in header and '"plotly"' in header


class TestRun:
    def test_runs_without_error(self, run):
        _, defs = run
        assert defs["N"] == len(defs["included"])
        assert set(defs["included"]["status"]) == {"included"}
        assert set(defs["watchlist"]["status"]) <= {"watchlist"}

    def test_reads_tables_through_notebook_location(self):
        source = NOTEBOOK.read_text()
        assert "mo.notebook_location()" in source
        assert "read_csv(" in source and "keep_default_na=False" in source

    def test_snapshot_is_a_date(self, run):
        _, defs = run
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", defs["SNAPSHOT"])
