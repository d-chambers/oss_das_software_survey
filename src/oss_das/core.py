"""Filesystem paths and serialization shared by all numbered scripts."""

from __future__ import annotations

import csv
import json
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, TypeVar

import yaml
from pydantic import BaseModel

from oss_das.models import ProjectRecord

RecordT = TypeVar("RecordT", bound=BaseModel)


@dataclass(frozen=True)
class ProjectPaths:
    root: Path

    @classmethod
    def discover(cls) -> ProjectPaths:
        return cls(Path(__file__).resolve().parents[2])

    @property
    def curated(self) -> Path:
        """One markdown file per project; the frontmatter is the registry."""
        return self.root / "data" / "projects"

    @property
    def snapshots(self) -> Path:
        return self.root / "data" / "snapshots"

    @property
    def docs(self) -> Path:
        return self.root / "docs"

    def snapshot(self, snapshot_date: str) -> Path:
        date.fromisoformat(snapshot_date)
        return self.snapshots / snapshot_date

    def raw(self, snapshot_date: str) -> Path:
        return self.snapshot(snapshot_date) / "raw"


PATHS = ProjectPaths.discover()


#: Frontmatter blocks a rebuild owns. They sit beside the curated record but
#: are not part of it, so they are stripped before validation rather than being
#: allowed to widen the schema a reviewer is responsible for.
GENERATED_BLOCKS = ("collected", "summary")


def read_frontmatter(path: Path) -> dict[str, Any]:
    text = path.read_text()
    if not text.startswith("---\n"):
        raise ValueError(f"{path} has no frontmatter block")
    _, _, rest = text.partition("---\n")
    front, marker, _ = rest.partition("\n---")
    if not marker:
        raise ValueError(f"{path} has an unterminated frontmatter block")
    return yaml.safe_load(front) or {}


def load_projects(path: Path | None = None) -> list[ProjectRecord]:
    """Load the curated registry from the per-project files.

    Each file also carries collected metrics and agent provenance, which are
    regenerated rather than reviewed; only the ``curated`` block is the
    authority for identity, scope, and licensing.
    """
    source = path or PATHS.curated
    documents = []
    for file in sorted(source.glob("*.md")):
        document = read_frontmatter(file)
        if "curated" not in document:
            raise ValueError(f"{file} has no curated block")
        documents.append(document["curated"])
    projects = [ProjectRecord.model_validate(item) for item in documents]
    ids = [project.id for project in projects]
    repositories = [project.forge_key for project in projects]
    if len(ids) != len(set(ids)):
        raise ValueError("project ids must be unique")
    if len(repositories) != len(set(repositories)):
        raise ValueError("project repositories must be unique")
    return sorted(projects, key=lambda project: project.id)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, default=str) + "\n")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def write_jsonl(path: Path, values: Iterable[dict[str, Any] | BaseModel]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    for value in values:
        payload = (
            value.model_dump(mode="json") if isinstance(value, BaseModel) else value
        )
        lines.append(json.dumps(payload, sort_keys=True, default=str))
    path.write_text("\n".join(lines) + ("\n" if lines else ""))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def write_csv(path: Path, rows: Iterable[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {key: "" if value is None else value for key, value in row.items()}
            )


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="") as file:
        return list(csv.DictReader(file))


def load_rejections(path: Path | None = None) -> dict[str, dict[str, str]]:
    """Read the ledger of candidates reviewed and rejected, keyed by forge key.

    A rejection is deliberately not a catalog entry. Writing one curated file
    per junk repository would bury `data/projects/` under several hundred
    records that carry no metrics and appear in no figure. The ledger records
    only that a repository was looked at and is not a project, so discovery
    stops proposing it at every snapshot.
    """
    path = path or PATHS.root / "data" / "rejected.yml"
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


def newest_snapshot() -> str:
    candidates = sorted(
        path.name for path in PATHS.snapshots.glob("????-??-??") if path.is_dir()
    )
    if not candidates:
        raise FileNotFoundError("no dated snapshots are available")
    return candidates[-1]
