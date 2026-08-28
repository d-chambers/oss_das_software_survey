"""Measure lines of source code from each mirror's mainline tree.

The forge APIs report a per-language *byte* count, which `a080` divides by a
nominal 32 to estimate lines. That estimate is fine for ranking projects but
wrong in two ways that matter for an ecosystem total: it counts notebooks by
their serialized size, which is dominated by embedded output images, and it
counts whatever the forge decided a repository's languages were rather than
what is in the tree.

This module reads the tree instead. It walks the mainline commit of a bare
mirror, decides a language per path, and counts newlines out of the blobs --
except for notebooks, which are parsed so only their code cells count.

Two exclusions are deliberate and both suppress *generated* files that would
otherwise be counted as authored source:

* HTML is not a counted language at all. In these repositories it is
  essentially always a committed docs build -- mkdocs `site/`, Sphinx
  `docs/_build/`, nbconvert exports. Counting it made "Web" the second-largest
  language of the ecosystem on the strength of three projects' checked-in
  output.
* :data:`GENERATED_DIRS` and minified files are skipped wherever they appear.

The result is a floor on a repository's size, not a SLOC count: blank lines and
comments are included, and a language outside :data:`EXTENSION_LANGUAGES` is
not counted at all.
"""

from __future__ import annotations

import json
import os
import subprocess
import threading
from collections import Counter
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

from oss_das.commits import GIT_ENV, GitError, resolve_mainline, run_git

#: File extension to language name. A language absent here is not counted;
#: adding one changes every published total, so it belongs in a snapshot.
EXTENSION_LANGUAGES = {
    ".py": "Python",
    ".pyx": "Python",
    ".pyi": "Python",
    ".ipynb": "Jupyter",
    ".jl": "Julia",
    ".m": "MATLAB",
    ".mlx": "MATLAB",
    ".c": "C",
    ".h": "C",
    ".cpp": "C++",
    ".cc": "C++",
    ".cxx": "C++",
    ".hpp": "C++",
    ".hh": "C++",
    ".cu": "CUDA",
    ".cuh": "CUDA",
    ".f": "Fortran",
    ".f90": "Fortran",
    ".f95": "Fortran",
    ".for": "Fortran",
    ".r": "R",
    ".rmd": "R",
    ".rs": "Rust",
    ".go": "Go",
    ".java": "Java",
    ".js": "JavaScript",
    ".mjs": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".sh": "Shell",
    ".bash": "Shell",
    ".css": "Web",
    ".vue": "Web",
}

#: Path components whose contents are vendored or generated rather than
#: authored. Matched against any component, at any depth.
GENERATED_DIRS = frozenset(
    {
        "node_modules",
        "vendor",
        ".git",
        "third_party",
        "externals",
        "site",
        "_build",
        "build",
        "dist",
        "_site",
        "public",
        "htmlcov",
        ".venv",
        "venv",
        "eggs",
        ".eggs",
    }
)

#: The language whose sources are parsed rather than counted by newline.
NOTEBOOK = "Jupyter"

LOC_FIELDS = ["project_id", "language", "lines"]


def classify_path(path: str) -> str | None:
    """Return the language to count ``path`` as, or None to skip it.

    Skipping is not the same as counting zero: an uncounted path contributes
    nothing to any language, and a repository of nothing but uncounted paths
    reports no code at all rather than a total of zero lines.
    """
    lowered = path.lower()
    if GENERATED_DIRS & set(lowered.split("/")):
        return None
    base = lowered.rsplit("/", 1)[-1]
    if ".min." in base:
        return None
    if "." not in base:
        return None
    return EXTENSION_LANGUAGES.get("." + base.rsplit(".", 1)[-1])


def notebook_code_lines(raw: str) -> int:
    """Count the source lines of a notebook's code cells.

    Markdown cells and outputs are excluded. A notebook that does not parse
    counts as zero: it is checked-in JSON that no kernel could run, and
    guessing a line count from its bytes is exactly the error this avoids.
    """
    try:
        notebook = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return 0
    if not isinstance(notebook, dict):
        return 0
    total = 0
    for cell in notebook.get("cells") or ():
        if not isinstance(cell, dict) or cell.get("cell_type") != "code":
            continue
        source = cell.get("source", "")
        # nbformat allows either a list of lines or one string. Joining and
        # splitting handles both without trusting the list to hold exactly one
        # line per entry, and without counting a trailing newline as a line.
        if isinstance(source, list):
            source = "".join(part for part in source if isinstance(part, str))
        if isinstance(source, str):
            total += len(source.splitlines())
    return total


def list_tree(repo: Path, ref: str, *, timeout: int = 900) -> list[tuple[str, str]]:
    """Return (blob sha, language) for every counted path reachable from ``ref``."""
    text = run_git(
        [
            "-c",
            "core.quotePath=false",
            "-C",
            str(repo),
            "ls-tree",
            "-r",
            "--full-tree",
            ref,
        ],
        timeout=timeout,
    )
    wanted: list[tuple[str, str]] = []
    for line in text.splitlines():
        head, _, path = line.partition("\t")
        fields = head.split()
        if len(fields) < 3 or fields[1] != "blob" or not path:
            continue
        language = classify_path(path)
        if language is not None:
            wanted.append((fields[2], language))
    return wanted


def measure_repo(repo: Path, ref: str, *, timeout: int = 900) -> dict[str, int]:
    """Return lines per language in ``ref``'s tree, omitting empty languages.

    Blobs are read through a single `git cat-file --batch` rather than one
    process per file: the largest mirrors hold thousands of counted paths, and
    the process spawns dominate everything else.
    """
    wanted = list_tree(repo, ref, timeout=timeout)
    if not wanted:
        return {}
    totals: Counter[str] = Counter()
    # cat-file answers in the order asked, so zip re-pairs each blob with the
    # language its path was classified as.
    blobs = _read_blobs(repo, [sha for sha, _ in wanted], timeout)
    for (_, language), raw in zip(wanted, blobs, strict=True):
        if language == NOTEBOOK:
            totals[language] += notebook_code_lines(raw.decode("utf-8", "replace"))
        else:
            totals[language] += raw.count(b"\n")
    return {language: count for language, count in totals.items() if count}


def _read_blobs(repo: Path, shas: list[str], timeout: int) -> Iterator[bytes]:
    """Yield each blob's contents, in the order requested.

    The request list is written from a separate thread. A repository with a few
    thousand counted files sends more than a pipe buffer holds, and writing it
    all before reading any answer deadlocks: git stops draining our stdin once
    its own stdout backs up, and both processes wait on the other.
    """
    process = subprocess.Popen(
        ["git", "-C", str(repo), "cat-file", "--batch"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        env={**os.environ, **GIT_ENV},
    )
    assert process.stdin is not None and process.stdout is not None

    def feed() -> None:
        try:
            process.stdin.write(("\n".join(shas) + "\n").encode())
        except BrokenPipeError:
            pass  # the reader gave up first; it raises the real error
        finally:
            process.stdin.close()

    writer = threading.Thread(target=feed, daemon=True)
    writer.start()
    try:
        for sha in shas:
            header = process.stdout.readline()
            if not header:
                raise GitError(f"cat-file ended before {sha}")
            parts = header.split()
            if len(parts) < 3 or parts[1] != b"blob":
                raise GitError(f"cat-file did not return a blob for {sha}")
            size = int(parts[2])
            payload = process.stdout.read(size)
            process.stdout.read(1)  # the newline git appends after each blob
            yield payload
    finally:
        process.stdout.close()
        writer.join(timeout=timeout)
        process.wait(timeout=timeout)


@dataclass(frozen=True)
class RepoLines:
    """One mirror's measurement.

    ``languages`` is empty for a repository that publishes no counted source at
    its mainline tip -- a README-only repository, or one whose code was
    deleted. That is a real finding, so it is kept as a row rather than
    dropped.
    """

    project_id: str
    ref: str | None
    languages: dict[str, int]

    @property
    def total(self) -> int:
        return sum(self.languages.values())

    @property
    def primary_language(self) -> str | None:
        if not self.languages:
            return None
        return max(self.languages, key=lambda name: (self.languages[name], name))

    def rows(self) -> list[dict[str, object]]:
        return [
            {"project_id": self.project_id, "language": language, "lines": lines}
            for language, lines in sorted(self.languages.items())
        ]


def measure_mirror(repo: Path, *, timeout: int = 900) -> RepoLines:
    """Measure one bare mirror at its mainline ref."""
    ref = resolve_mainline(repo, timeout=timeout)
    if ref is None:
        return RepoLines(
            project_id=repo.name.removesuffix(".git"), ref=None, languages={}
        )
    return RepoLines(
        project_id=repo.name.removesuffix(".git"),
        ref=ref,
        languages=measure_repo(repo, ref, timeout=timeout),
    )


def iter_mirrors(repos: Path) -> Iterator[Path]:
    """Yield every bare mirror under ``repos``, in id order."""
    yield from sorted(repos.glob("*.git"))
