"""Tests for the figure measurements and their rendering."""

from __future__ import annotations

import shutil
from xml.etree import ElementTree

import pytest

from oss_das.figures import draw
from oss_das.figures.data import BOT, unique_authors
from oss_das.figures.records import frontmatter
from oss_das.figures.render import RenderError, load_asset, write_figure


def commit(name: str, email: str) -> dict[str, str]:
    return {"author_name": name, "author_email": email}


class TestUniqueAuthors:
    def test_no_commits_is_nobody(self):
        assert unique_authors([]) == 0

    def test_one_person_two_addresses_is_one(self):
        rows = [commit("Ada", "ada@work.com"), commit("Ada", "ada@home.com")]
        assert unique_authors(rows) == 1

    def test_one_address_two_names_is_one(self):
        # A rename, or a laptop configured differently, is still one person.
        rows = [commit("Ada L", "ada@x.com"), commit("Ada Lovelace", "ada@x.com")]
        assert unique_authors(rows) == 1

    def test_transitive_identities_collapse(self):
        # Ada@work links to "Ada"; "Ada Lovelace" links through the shared address.
        rows = [
            commit("Ada", "ada@work.com"),
            commit("Ada", "ada@home.com"),
            commit("Ada Lovelace", "ada@home.com"),
        ]
        assert unique_authors(rows) == 1

    def test_distinct_people_stay_distinct(self):
        rows = [commit("Ada", "ada@x.com"), commit("Grace", "grace@y.com")]
        assert unique_authors(rows) == 2

    def test_case_and_whitespace_do_not_split_a_person(self):
        rows = [commit(" Ada ", "Ada@X.com"), commit("ada", "ada@x.com")]
        assert unique_authors(rows) == 1

    @pytest.mark.parametrize(
        "name,email",
        [
            ("dependabot[bot]", "bot@github.com"),
            ("github-actions", "actions@github.com"),
            ("Someone", "pre-commit-ci[bot]@users.noreply.github.com"),
        ],
    )
    def test_automation_is_not_a_contributor(self, name, email):
        assert unique_authors([commit("Ada", "ada@x.com"), commit(name, email)]) == 1

    def test_a_bot_never_merges_two_people(self):
        # Bots are dropped before the union, so they cannot bridge identities.
        rows = [
            commit("Ada", "ada@x.com"),
            commit("dependabot[bot]", "ada@x.com"),
            commit("dependabot[bot]", "grace@y.com"),
            commit("Grace", "grace@y.com"),
        ]
        assert unique_authors(rows) == 2

    def test_bot_pattern_does_not_match_ordinary_names(self):
        assert not BOT.search("Roberta Bottomley")


class TestCanvas:
    def test_output_is_well_formed_svg(self):
        c = draw.Canvas(width=100, height=50, title="T", desc="D")
        c.text(50, 25, "hello")
        root = ElementTree.fromstring(c.to_svg())
        assert root.tag.endswith("svg")
        assert root.get("viewBox") == "0 0 100 50"

    def test_text_is_escaped_not_injected(self):
        c = draw.Canvas(width=10, height=10, title="T", desc="D")
        c.text(0, 0, "5 < 6 & rising")
        svg = c.to_svg()
        assert "<text" in svg and "5 &lt; 6 &amp; rising" in svg
        ElementTree.fromstring(svg)  # still parses

    def test_title_and_desc_are_escaped(self):
        c = draw.Canvas(width=10, height=10, title="a & b", desc="x < y")
        ElementTree.fromstring(c.to_svg())

    def test_letter_spacing_shifts_centred_text_back(self):
        # Spacing is added after the last glyph too, so centred text drifts left.
        c = draw.Canvas(width=100, height=10, title="T", desc="D")
        c.text(50, 5, "AB", spacing=4, anchor="middle")
        assert 'x="52"' in c.parts[0]

    def test_letter_spacing_does_not_shift_left_anchored_text(self):
        c = draw.Canvas(width=100, height=10, title="T", desc="D")
        c.text(50, 5, "AB", spacing=4, anchor="start")
        assert 'x="50"' in c.parts[0]

    def test_stat_returns_the_last_baseline_it_drew(self):
        c = draw.Canvas(width=100, height=100, title="T", desc="D")
        end = c.stat(50, 10, "7", "things", "a gloss", gap=30, sub_gap=20)
        assert end == 60

    def test_stat_without_a_gloss_stops_at_the_label(self):
        c = draw.Canvas(width=100, height=100, title="T", desc="D")
        assert c.stat(50, 10, "7", "things", gap=30) == 40


class TestWriteFigure:
    def test_svg_only_writes_one_file(self, tmp_path):
        c = draw.Canvas(width=10, height=10, title="T", desc="D")
        written = write_figure("demo", c.to_svg(), tmp_path, pdf=False)
        assert [p.name for p in written] == ["demo.svg"]
        assert (tmp_path / "demo.svg").exists()

    @pytest.mark.skipif(shutil.which("inkscape") is None, reason="inkscape required")
    def test_pdf_is_written_beside_the_svg(self, tmp_path):
        c = draw.Canvas(width=200, height=100, title="T", desc="D")
        c.text(100, 50, "figure")
        written = write_figure("demo", c.to_svg(), tmp_path)
        assert [p.name for p in written] == ["demo.svg", "demo.pdf"]
        assert (tmp_path / "demo.pdf").read_bytes().startswith(b"%PDF")

    def test_a_missing_asset_is_an_error_not_an_empty_figure(self, tmp_path):
        with pytest.raises(RenderError, match="no such figure asset"):
            load_asset("absent", tmp_path)

    def test_an_asset_without_a_group_is_rejected(self, tmp_path):
        (tmp_path / "flat.svg").write_text("<svg><rect/></svg>")
        with pytest.raises(RenderError, match="expected a top-level"):
            load_asset("flat", tmp_path)

    def test_an_asset_is_embedded_as_its_group(self, tmp_path):
        (tmp_path / "icon.svg").write_text('<svg><g id="i"><rect x="1"/></g></svg>')
        assert load_asset("icon", tmp_path) == '<g id="i"><rect x="1"/></g>'


@pytest.mark.skipif(shutil.which("inkscape") is None, reason="inkscape required")
class TestPdfTextMode:
    """keep_text has to actually change the PDF, or it is a lying flag."""

    def _pdf(self, tmp_path, name, **kw):
        c = draw.Canvas(width=300, height=120, title="T", desc="D")
        c.text(150, 70, "Distributed", size=40)
        write_figure(name, c.to_svg(), tmp_path, **kw)
        return (tmp_path / f"{name}.pdf").read_bytes()

    def test_outlined_pdf_embeds_no_font(self, tmp_path):
        assert self._pdf(tmp_path, "outlined").count(b"/Font") == 0

    def test_kept_text_pdf_embeds_a_font(self, tmp_path):
        assert self._pdf(tmp_path, "kept", keep_text=True).count(b"/Font") > 0

    def test_the_two_modes_differ(self, tmp_path):
        outlined = self._pdf(tmp_path, "a")
        kept = self._pdf(tmp_path, "b", keep_text=True)
        assert outlined != kept


class TestFrontmatter:
    """Records are scraped text; the reader must survive what is in them."""

    def write(self, tmp_path, name, text):
        path = tmp_path / name
        path.write_text(text, encoding="utf-8")
        return path

    def test_reads_a_plain_block(self, tmp_path):
        p = self.write(tmp_path, "a.md", "---\nid: x\nn: 2\n---\nbody\n")
        assert frontmatter(p) == {"id": "x", "n": 2}

    def test_a_dashed_line_inside_a_quoted_value_does_not_truncate(self, tmp_path):
        # Scraped descriptions contain "---"; splitting on the string anywhere
        # cuts the block mid-value and the remainder is not valid YAML.
        p = self.write(
            tmp_path, "b.md", '---\nid: x\ndescription: "a --- b"\nn: 3\n---\nbody\n'
        )
        assert frontmatter(p) == {"id": "x", "description": "a --- b", "n": 3}

    def test_body_delimiters_are_not_mistaken_for_the_block(self, tmp_path):
        p = self.write(tmp_path, "c.md", "---\nid: x\n---\nprose\n---\nmore\n")
        assert frontmatter(p) == {"id": "x"}

    def test_a_file_with_no_frontmatter_is_empty_not_an_error(self, tmp_path):
        assert frontmatter(self.write(tmp_path, "d.md", "just prose\n")) == {}

    def test_an_unterminated_block_is_empty_not_a_crash(self, tmp_path):
        assert frontmatter(self.write(tmp_path, "e.md", "---\nid: x\nno end\n")) == {}

    def test_a_non_mapping_block_is_empty(self, tmp_path):
        assert (
            frontmatter(self.write(tmp_path, "f.md", "---\n- one\n- two\n---\n")) == {}
        )

    def test_malformed_yaml_names_the_file(self, tmp_path):
        p = self.write(tmp_path, "g.md", '---\nid: "unclosed\n---\n')
        with pytest.raises(ValueError, match=r"g\.md: frontmatter is not valid YAML"):
            frontmatter(p)

    def test_every_shipped_record_parses(self):
        # A record the reader cannot open would silently drop out of a figure.
        import pathlib

        for directory in ("data/curated", "data/measured/git"):
            root = pathlib.Path(directory)
            if not root.is_dir():
                continue
            for path in root.glob("*.md"):
                assert frontmatter(path), path
