"""The deck must not be able to print a number the measurements do not hold."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DECK = ROOT / "deck"
SCRIPT = ROOT / "deck" / "prepare.py"

pytestmark = pytest.mark.skipif(
    not (DECK / "slides.qmd").exists(), reason="no deck in this checkout"
)


def build(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
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
    """A build that cannot prove a number must refuse, and say why."""

    def scratch(self, tmp_path, slides: str, sidecar: dict) -> Path:
        deck = tmp_path / "deck"
        deck.mkdir()
        (deck / "slides.qmd").write_text(slides)
        figures = tmp_path / "figures"
        figures.mkdir()
        (figures / "figures.json").write_text(json.dumps(sidecar))
        return tmp_path

    def test_an_unknown_measurement_is_refused_not_raised(self, tmp_path):
        root = self.scratch(
            tmp_path,
            "---\ntitle: t\n---\n\n## s\n\n{{< meta n.nope.not_a_key >}}\n",
            {"a": {"b": 1}, "figures": {}},
        )
        result = build("--root", str(root))
        assert result.returncode == 2
        assert "nope.not_a_key" in result.stderr
        # A traceback would mean it crashed rather than reported. Under -O the
        # assert this replaced vanished and the crash alone kept the test green.
        assert "Traceback" not in result.stderr

    def test_a_figure_that_is_not_the_measured_one_is_refused(self, tmp_path):
        root = self.scratch(
            tmp_path,
            "---\ntitle: t\n---\n\n## s\n\n![](../figures/v010_x.png)\n",
            {"figures": {"v010_x.png": "0" * 64}},
        )
        (root / "figures" / "v010_x.png").write_bytes(b"not the measured bytes")
        result = build("--root", str(root))
        assert result.returncode == 2
        assert "v010_x.png" in result.stderr
        assert "Traceback" not in result.stderr

    def test_a_figure_referenced_uncheckably_is_refused(self, tmp_path):
        """An <img> or an absolute path would slip past both other checks."""
        root = self.scratch(
            tmp_path,
            '---\ntitle: t\n---\n\n## s\n\n<img src="../figures/v010_x.png">\n',
            {"figures": {}},
        )
        result = build("--root", str(root))
        assert result.returncode == 2
        assert "cannot check" in result.stderr

    def test_a_sidecar_without_checksums_is_refused(self, tmp_path):
        root = self.scratch(
            tmp_path,
            "---\ntitle: t\n---\n\n## s\n\n![](../figures/v010_x.png)\n",
            {"a": 1},
        )
        (root / "figures" / "v010_x.png").write_bytes(b"x")
        result = build("--root", str(root))
        assert result.returncode == 2
        assert "checksums" in result.stderr


class TestListsAreCitable:
    def test_a_number_inside_a_list_can_be_cited(self):
        """The most quotable numbers live in lists; dropping them forced
        literals back onto the slides."""
        import importlib.util

        spec = importlib.util.spec_from_file_location("deck", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        flat = module.flatten({"network": {"providers": [["a", "A", 13]]}})
        assert flat["network.providers.0.2"] == 13


class TestBothFormats:
    """The HTML is what gets presented; the PDF is the backup for when it isn't."""

    def config(self) -> str:
        return (DECK / "_quarto.yml").read_text()

    def test_both_outputs_are_declared(self):
        config = self.config()
        assert "revealjs:" in config and "beamer:" in config

    def test_the_html_is_self_contained(self):
        """One file, or something goes missing between laptop and lectern."""
        assert "embed-resources: true" in self.config()

    def test_every_positioned_logo_exists(self):
        """An .absolute image that is missing leaves a hole, not an error."""
        import re

        text = (DECK / "slides.qmd").read_text()
        refs = re.findall(r"!\[\]\((assets/[^)]+)\)\{\.absolute", text)
        assert refs, "no positioned logos found; the axis slides are the point"
        missing = [r for r in refs if not (DECK / r).exists()]
        assert not missing, missing

    def test_reveal_only_content_declares_a_beamer_fallback(self):
        """Absolute positioning has no beamer equivalent, so each such slide
        must offer the PDF something readable instead of nothing."""
        text = (DECK / "slides.qmd").read_text()
        assert text.count('when-format="revealjs"') == text.count(
            'when-format="beamer"'
        ), "a format-conditional block has no counterpart in the other format"
