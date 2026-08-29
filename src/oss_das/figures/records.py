"""Read the repository's markdown records.

Every fact the pipeline knows now lives in a markdown file with a YAML
frontmatter block: one per curated project, per measurement, per candidate.
The figures read those files directly rather than the derived CSVs, so a
figure stays correct while the surrounding pipeline is being rebuilt.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Any

import yaml

from oss_das.core import PATHS


def frontmatter(path: Path) -> dict[str, Any]:
    """Return a record's YAML block, or an empty mapping if it has none.

    The block is delimited by lines that are exactly ``---``. Splitting on the
    string anywhere would cut a record whose own text contains it -- scraped
    descriptions do, and the truncated block then fails to parse as YAML.
    """
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            block = "\n".join(lines[1:index])
            break
    else:
        return {}
    try:
        loaded = yaml.safe_load(block)
    except yaml.YAMLError as error:
        raise ValueError(f"{path}: frontmatter is not valid YAML: {error}") from error
    return loaded if isinstance(loaded, dict) else {}


def _records(directory: Path) -> Iterator[dict[str, Any]]:
    for path in sorted(directory.glob("*.md")):
        record = frontmatter(path)
        if record:
            yield record


def data_dir() -> Path:
    return PATHS.root / "data"


def curated() -> dict[str, dict[str, Any]]:
    """Every catalogued project, keyed by id."""
    return {r["id"]: r for r in _records(data_dir() / "curated") if "id" in r}


def measured(kind: str) -> dict[str, dict[str, Any]]:
    """One family of measurements -- git, mirror, forge, registry -- by id."""
    directory = data_dir() / "measured" / kind
    if not directory.is_dir():
        return {}
    return {r["id"]: r for r in _records(directory) if "id" in r}


def candidate_sources() -> dict[str, int]:
    """How many candidates each discovery source produced.

    Counted from the files rather than a summary row, so the number cannot
    disagree with what is actually on disk.
    """
    root = data_dir() / "raw" / "candidates"
    if not root.is_dir():
        return {}
    return {
        source.name: sum(1 for _ in source.glob("*.md"))
        for source in sorted(root.iterdir())
        if source.is_dir()
    }


def comparison(ecosystem: str) -> dict[str, dict[str, Any]]:
    """Every record for a reference ecosystem, keyed by ``owner--name``."""
    directory = data_dir() / "comparison" / ecosystem
    if not directory.exists():
        return {}
    return {path.stem: frontmatter(path) for path in sorted(directory.glob("*.md"))}


def rejections() -> dict[str, dict[str, str]]:
    """The reviewed-and-rejected ledger, keyed by candidate key."""
    path = data_dir() / "rejected.yml"
    if not path.exists():
        return {}
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return payload.get("rejections") or {}
