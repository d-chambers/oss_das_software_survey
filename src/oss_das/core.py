"""Filesystem layout and record I/O shared by every numbered script.

Every per-project record is a Markdown file with YAML frontmatter: facts in
the frontmatter, prose in the body. This module owns reading and writing that
shape, the directory layout from the README, and the two ledgers.
"""

from __future__ import annotations

import csv
import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from oss_das.models import ProjectRecord

#: Sources a measured record can come from; each is one B script's directory.
MEASURED_SOURCES = ("mirror", "git", "forge", "registry", "publications")


@dataclass(frozen=True)
class ProjectPaths:
    root: Path

    @classmethod
    def discover(cls) -> ProjectPaths:
        return cls(Path(__file__).resolve().parents[2])

    @property
    def data(self) -> Path:
        return self.root / "data"

    # --- A: curate -----------------------------------------------------------
    @property
    def candidates(self) -> Path:
        """Write-once discovery findings, ``<source>/<key>.md``."""
        return self.data / "raw" / "candidates"

    @property
    def coverage(self) -> Path:
        """Append-only ledger: every discovery probe and what it returned."""
        return self.data / "raw" / "coverage.csv"

    @property
    def triage(self) -> Path:
        """Append-only ledger of is-it-DAS verdicts; the last row per key wins."""
        return self.data / "triage.csv"

    @property
    def enriched(self) -> Path:
        return self.data / "enriched"

    @property
    def curated(self) -> Path:
        return self.data / "curated"

    @property
    def rejected(self) -> Path:
        return self.data / "rejected.yml"

    # --- B: measure ----------------------------------------------------------
    @property
    def repos(self) -> Path:
        return self.data / "repos"

    @property
    def commits(self) -> Path:
        return self.data / "commits"

    def measured(self, source: str) -> Path:
        assert source in MEASURED_SOURCES, source
        return self.data / "measured" / source

    # --- C: present ----------------------------------------------------------
    @property
    def notebooks(self) -> Path:
        return self.root / "notebooks"

    @property
    def public(self) -> Path:
        """Tables the notebook reads; marimo ships this directory with the export."""
        return self.notebooks / "public"


PATHS = ProjectPaths.discover()


# --- markdown records ---------------------------------------------------------

_FRONT = re.compile(r"\A---\n(.*?)\n---\n?(.*)\Z", re.S)


def read_record(path: Path) -> tuple[dict[str, Any], str]:
    """Split a record into its frontmatter mapping and prose body."""
    match = _FRONT.match(path.read_text())
    if not match:
        raise ValueError(f"{path} has no frontmatter block")
    front = yaml.safe_load(match.group(1)) or {}
    if not isinstance(front, dict):
        raise ValueError(f"{path}: frontmatter must be a mapping")
    return front, match.group(2).strip()


def write_record(path: Path, front: dict[str, Any], body: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = yaml.safe_dump(front, sort_keys=False, allow_unicode=True, width=100)
    path.write_text(f"---\n{text}---\n" + (f"\n{body.strip()}\n" if body else ""))


def read_frontmatter(path: Path) -> dict[str, Any]:
    return read_record(path)[0]


# --- candidate keys -----------------------------------------------------------


def candidate_key(source: str, path: str) -> str:
    """The identity of one finding: ``host/owner/name`` or ``pypi/name``."""
    return f"{source}/{path.strip('/')}".lower()


def candidate_path(key: str, root: Path | None = None) -> Path:
    """Where a candidate is written; nested paths fold into one filename."""
    source, _, rest = key.partition("/")
    return (root or PATHS.candidates) / source / f"{rest.replace('/', '--')}.md"


# --- loaders ------------------------------------------------------------------


def load_projects(path: Path | None = None) -> list[ProjectRecord]:
    """Load the human-approved catalogue from ``data/curated/``."""
    source = path or PATHS.curated
    projects = [
        ProjectRecord.model_validate(read_frontmatter(file))
        for file in sorted(source.glob("*.md"))
    ]
    ids = [project.id for project in projects]
    if len(ids) != len(set(ids)):
        raise ValueError("project ids must be unique")
    keys = [project.key for project in projects]
    if len(keys) != len(set(keys)):
        raise ValueError("project repositories must be unique")
    return sorted(projects, key=lambda project: project.id)


def load_rejections(path: Path | None = None) -> dict[str, dict[str, str]]:
    """Read the ledger of candidates reviewed and rejected, keyed by candidate key."""
    path = path or PATHS.rejected
    if not path.exists():
        return {}
    payload = yaml.safe_load(path.read_text()) or {}
    rejections = payload.get("rejections") or {}
    if not isinstance(rejections, dict):
        raise ValueError(f"{path}: 'rejections' must be a mapping")
    out: dict[str, dict[str, str]] = {}
    for key, value in rejections.items():
        if not isinstance(value, dict) or "reason" not in value:
            raise ValueError(f"{path}: {key!r} needs a 'reason'")
        out[str(key).lower()] = {
            "reason": str(value["reason"]),
            "note": str(value.get("note", "")),
        }
    return out


def append_rejections(
    entries: dict[str, dict[str, str]], path: Path | None = None
) -> None:
    """Add rejections to the ledger, keeping existing entries and comments' intent."""
    path = path or PATHS.rejected
    current = load_rejections(path)
    current.update(entries)
    payload = {"rejections": dict(sorted(current.items()))}
    path.write_text(
        "# Candidates reviewed and rejected, so they are not proposed again.\n"
        "# Keys are candidate keys (host/owner/name or pypi/name), lowercased.\n"
        "# A rejection is not a catalogue entry: it carries no metrics and appears\n"
        "# in no figure. A curated file always wins over an entry here.\n\n"
        + yaml.safe_dump(payload, sort_keys=False, allow_unicode=True, width=100)
    )


# --- csv ----------------------------------------------------------------------


def write_csv(path: Path, rows: Iterable[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: "" if v is None else v for k, v in row.items()})


def append_csv(path: Path, rows: Iterable[dict[str, Any]], fields: list[str]) -> int:
    """Append rows to a ledger, writing the header only when the file is new."""
    path.parent.mkdir(parents=True, exist_ok=True)
    new = not path.exists() or path.stat().st_size == 0
    count = 0
    with path.open("a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields, extrasaction="ignore")
        if new:
            writer.writeheader()
        for row in rows:
            writer.writerow({k: "" if v is None else v for k, v in row.items()})
            count += 1
    return count


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="") as file:
        return list(csv.DictReader(file))


def newest_snapshot() -> str:
    """Kept only so the untouched `v` figure scripts still import; snapshots are gone."""
    raise FileNotFoundError(
        "dated snapshots no longer exist; figures read notebooks/public/"
    )
