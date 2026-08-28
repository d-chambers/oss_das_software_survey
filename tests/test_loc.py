"""Tests for measuring lines of source out of a bare mirror."""

from __future__ import annotations

import json
import shutil
import subprocess

import pytest

from oss_das.loc import (
    classify_path,
    measure_mirror,
    measure_repo,
    notebook_code_lines,
)

pytestmark = pytest.mark.skipif(shutil.which("git") is None, reason="git required")


class TestClassifyPath:
    def test_known_extensions_map_to_languages(self):
        assert classify_path("src/pkg/core.py") == "Python"
        assert classify_path("analysis.ipynb") == "Jupyter"
        assert classify_path("src/filter.jl") == "Julia"

    def test_extension_match_is_case_insensitive(self):
        assert classify_path("SRC/Core.PY") == "Python"

    def test_unknown_extension_is_not_counted(self):
        assert classify_path("README.md") is None
        assert classify_path("data/trace.h5") is None

    def test_extensionless_file_is_not_counted(self):
        assert classify_path("LICENSE") is None
        assert classify_path("scripts/run") is None

    def test_html_is_not_a_counted_language(self):
        # Committed docs builds, not authored source; counting them once made
        # "Web" the second language of the ecosystem.
        assert classify_path("docs/index.html") is None

    @pytest.mark.parametrize(
        "path",
        [
            "site/search/worker.js",
            "docs/_build/html/static.css",
            "node_modules/left-pad/index.js",
            "deep/nested/build/generated.py",
            "vendor/lib.c",
        ],
    )
    def test_generated_directories_are_skipped_at_any_depth(self, path):
        assert classify_path(path) is None

    def test_minified_files_are_skipped(self):
        assert classify_path("assets/plotly.min.js") is None
        # ...but a normal file whose name merely contains "min" is not.
        assert classify_path("src/minimize.js") == "JavaScript"

    def test_a_directory_named_like_source_is_still_counted(self):
        # "build" is skipped as a directory; a module *called* build is source.
        assert classify_path("src/pkg/build.py") == "Python"


class TestNotebookCodeLines:
    def test_counts_code_cells_only(self):
        raw = json.dumps(
            {
                "cells": [
                    {"cell_type": "code", "source": ["import numpy\n", "x = 1\n"]},
                    {"cell_type": "markdown", "source": ["# A heading\n"] * 50},
                ]
            }
        )
        assert notebook_code_lines(raw) == 2

    def test_outputs_do_not_count(self):
        raw = json.dumps(
            {
                "cells": [
                    {
                        "cell_type": "code",
                        "source": ["plot()\n"],
                        "outputs": [{"data": {"image/png": "A" * 100_000}}],
                    }
                ]
            }
        )
        assert notebook_code_lines(raw) == 1

    def test_source_as_a_single_string(self):
        raw = json.dumps({"cells": [{"cell_type": "code", "source": "a = 1\nb = 2\n"}]})
        assert notebook_code_lines(raw) == 2

    def test_empty_source_counts_nothing(self):
        raw = json.dumps({"cells": [{"cell_type": "code", "source": ""}]})
        assert notebook_code_lines(raw) == 0

    def test_unparseable_notebook_counts_zero_not_its_bytes(self):
        assert notebook_code_lines("not json at all") == 0
        assert notebook_code_lines(json.dumps([1, 2, 3])) == 0


def git(repo, *args):
    subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        env={
            "PATH": "/usr/bin:/bin",
            "HOME": str(repo),
            "GIT_AUTHOR_NAME": "Ada",
            "GIT_AUTHOR_EMAIL": "ada@example.com",
            "GIT_COMMITTER_NAME": "Ada",
            "GIT_COMMITTER_EMAIL": "ada@example.com",
            "GIT_AUTHOR_DATE": "2024-01-02T03:04:05+00:00",
            "GIT_COMMITTER_DATE": "2024-01-02T03:04:05+00:00",
        },
    )


def commit_tree(repo, files: dict[str, str]) -> None:
    """Create a repository on branch `trunk` holding exactly ``files``."""
    repo.mkdir()
    git(repo, "init", "--quiet", "--initial-branch", "trunk")
    for name, text in files.items():
        path = repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    git(repo, "add", "-A")
    git(repo, "commit", "--quiet", "-m", "tree")


@pytest.fixture
def mixed_repo(tmp_path):
    """A repository with counted source, a notebook, and generated output."""
    notebook = json.dumps(
        {
            "cells": [
                {"cell_type": "code", "source": ["import x\n", "x.go()\n"]},
                {"cell_type": "markdown", "source": ["# not code\n"]},
            ]
        }
    )
    repo = tmp_path / "demo"
    commit_tree(
        repo,
        {
            "src/core.py": "one\ntwo\nthree\n",
            "src/util.py": "alpha\nbeta\n",
            "notebooks/run.ipynb": notebook,
            "kernel/fast.c": "int main(){}\n",
            "README.md": "docs\n" * 99,
            "site/index.html": "<html>\n" * 99,
            "docs/_build/leftover.py": "generated\n" * 99,
            "assets/lib.min.js": "minified\n" * 99,
        },
    )
    return repo


class TestAgainstRealRepositories:
    def test_counts_source_and_ignores_generated_output(self, tmp_path, mixed_repo):
        mirror = tmp_path / "demo.git"
        subprocess.run(
            ["git", "clone", "--mirror", "--quiet", str(mixed_repo), str(mirror)],
            check=True,
            capture_output=True,
        )
        result = measure_mirror(mirror)
        assert result.project_id == "demo"
        assert result.ref == "trunk"
        # Python from src only; the _build copy and the minified asset are gone,
        # and the notebook contributes its two code lines, not its bytes.
        assert result.languages == {"Python": 5, "Jupyter": 2, "C": 1}
        assert result.total == 8
        assert result.primary_language == "Python"

    def test_repository_with_no_counted_source_reports_none(self, tmp_path):
        repo = tmp_path / "readme-only"
        commit_tree(repo, {"README.md": "nothing but prose\n"})
        mirror = tmp_path / "readme-only.git"
        subprocess.run(
            ["git", "clone", "--mirror", "--quiet", str(repo), str(mirror)],
            check=True,
            capture_output=True,
        )
        result = measure_mirror(mirror)
        # Empty, not zero: nothing here was measured as code at all.
        assert result.languages == {}
        assert result.total == 0
        assert result.primary_language is None
        assert result.rows() == []

    def test_empty_repository_has_no_mainline(self, tmp_path):
        repo = tmp_path / "empty.git"
        subprocess.run(
            ["git", "init", "--bare", "--quiet", str(repo)],
            check=True,
            capture_output=True,
        )
        result = measure_mirror(repo)
        assert result.ref is None
        assert result.languages == {}

    def test_measures_the_named_ref_not_the_working_tree(self, tmp_path, mixed_repo):
        # Later commits must not leak into a measurement of an earlier ref.
        (mixed_repo / "src/extra.py").write_text("added\n" * 10)
        git(mixed_repo, "add", "-A")
        git(mixed_repo, "commit", "--quiet", "-m", "grow")
        first = subprocess.run(
            ["git", "-C", str(mixed_repo), "rev-parse", "trunk~1"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        assert measure_repo(mixed_repo, first)["Python"] == 5
        assert measure_repo(mixed_repo, "trunk")["Python"] == 15

    def test_many_files_do_not_deadlock_the_batch_reader(self, tmp_path):
        # The sha list for this tree exceeds a pipe buffer, which is what the
        # writer thread in _read_blobs exists to survive.
        repo = tmp_path / "wide"
        commit_tree(repo, {f"src/m{n:04d}.py": "line\n" for n in range(2000)})
        assert measure_repo(repo, "trunk") == {"Python": 2000}

    def test_rows_are_one_per_language_sorted(self, tmp_path, mixed_repo):
        result = measure_mirror(mixed_repo)
        assert result.rows() == [
            {"project_id": "demo", "language": "C", "lines": 1},
            {"project_id": "demo", "language": "Jupyter", "lines": 2},
            {"project_id": "demo", "language": "Python", "lines": 5},
        ]
