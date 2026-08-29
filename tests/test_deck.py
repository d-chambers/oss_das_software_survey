"""The deck must not be able to print a number the measurements do not hold."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DECK = ROOT / "deck"
SCRIPT = ROOT / "scripts" / "v900_deck.py"

pytestmark = pytest.mark.skipif(
    not (DECK / "slides.qmd").exists(), reason="no deck in this checkout"
)


def build(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--no-render", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


class TestNumbersResolve:
    def test_every_citation_resolves_against_the_sidecar(self):
        assert build().returncode == 0

    def test_the_slides_hold_no_bare_totals(self):
        """A literal is a number that can go stale; the deck must cite instead."""
        import re

        text = (DECK / "slides.qmd").read_text()
        sidecar = json.loads((ROOT / "figures" / "figures.json").read_text())
        headline = {
            str(sidecar["ecosystem_totals"][key])
            for key in ("projects", "contributors", "commits", "lines", "citations")
        }
        # Only look outside shortcodes, where a literal would be the stale kind.
        prose = re.sub(r"\{\{<[^>]*>\}\}", "", text)
        found = sorted(n for n in headline if re.search(rf"\b{n}\b", prose))
        assert not found, (
            f"the deck writes headline totals as literals: {found} -- cite them "
            "with {{< meta n.ecosystem_totals.* >}} so they cannot go stale"
        )


class TestFiguresExist:
    def test_every_referenced_figure_is_on_disk(self):
        import re

        text = (DECK / "slides.qmd").read_text()
        missing = [
            ref
            for ref in re.findall(r"!\[[^\]]*\]\((\.\./figures/[^)]+)\)", text)
            if not (DECK / ref).resolve().exists()
        ]
        assert not missing, missing


class TestItFailsLoudly:
    def test_an_unknown_measurement_stops_the_build(self, tmp_path):
        """A renamed measurement must break the build, not render a blank."""
        deck = tmp_path / "deck"
        deck.mkdir()
        (deck / "slides.qmd").write_text(
            "---\ntitle: t\n---\n\n## s\n\n{{< meta n.nope.not_a_key >}}\n"
        )
        figures = tmp_path / "figures"
        figures.mkdir()
        (figures / "figures.json").write_text(json.dumps({"a": {"b": 1}}))
        result = build("--root", str(tmp_path))
        assert result.returncode != 0
        assert "nope.not_a_key" in result.stderr
