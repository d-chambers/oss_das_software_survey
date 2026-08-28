#!/usr/bin/env python3
"""Merge curation, collected metrics, and the agent summary into one file each.

Each project gets a single markdown file whose frontmatter carries everything
known about it. The file is split into three blocks that are owned by different
processes, and the split is the point: `curated` is written by a person and
never touched here, `collected` and `summary` are regenerated and any hand-edit
to them is lost. Without that boundary a rebuild would silently overwrite a
reviewer's judgement with whatever an API happened to return.

The dated snapshots under data/snapshots remain the historical record. These
files always describe the newest scan.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import yaml

from oss_das.core import PATHS, load_projects, newest_snapshot, read_csv
from oss_das.site import metric_lookup

#: Bytes of source per line, used only to turn language byte counts into a
#: rough size. Notebooks are left out: an .ipynb is mostly serialized output,
#: so its byte count says more about saved figures than about code written.
BYTES_PER_LINE = 32
LOC_EXCLUDED = {"Jupyter Notebook"}

#: Metrics nobody publishes for free, recorded as absent with the reason rather
#: than quietly omitted, so the gap is legible in the file itself.
UNAVAILABLE = {
    "pypi_downloads_total": "no free source publishes all-time PyPI totals",
    "conda_downloads_180d": "anaconda.org publishes a cumulative count only,"
    " with no time series",
}


def estimate_loc(language_bytes: dict[str, int]) -> int | None:
    counted = {
        name: size
        for name, size in (language_bytes or {}).items()
        if name not in LOC_EXCLUDED
    }
    if not counted:
        return None
    return round(sum(counted.values()) / BYTES_PER_LINE)


def collected_block(
    project_id: str,
    row: dict[str, str],
    raw: dict[str, Any],
    metrics: dict,
    dependencies: list[dict[str, str]],
) -> dict[str, Any]:
    def metric(name: str) -> int | None:
        """Metrics arrive as floats via CSV; every one of these is a count."""
        value = metrics.get((project_id, name))
        return None if value is None else int(value)

    def flag(name: str) -> bool | None:
        raw_value = row.get(name, "")
        return None if raw_value == "" else raw_value == "True"

    block = {
        "scanned_at": raw.get("fetched_at"),
        "snapshot": row.get("snapshot_date"),
        "visibility": row.get("visibility") or None,
        "language": row.get("language") or None,
        "stars": metric("repo_stars"),
        "forks": metric("repo_forks"),
        "contributors": metric("repo_contributors"),
        "releases": metric("repo_releases"),
        "commits": raw.get("commits"),
        "last_commit_at": raw.get("last_commit_at"),
        "created_at": row.get("created_at") or None,
        "latest_release_at": row.get("latest_release_at") or None,
        "archived": flag("archived"),
        "lines_of_code_estimate": estimate_loc(raw.get("language_bytes", {})),
        "loc_basis": (
            f"language bytes / {BYTES_PER_LINE}, notebooks excluded"
            if raw.get("language_bytes")
            else None
        ),
        "pypi_downloads_180d": metric("pypi_downloads_180d"),
        "pypi_downloads_30d": metric("pypi_downloads_30d"),
        "pypi_downloads_total": None,
        "conda_downloads_total": metric("conda_downloads_cumulative"),
        "conda_downloads_180d": None,
        "canonical_citations": metric("canonical_citations"),
        "dependencies": [
            {
                "package": item["package"],
                "dependency": item["dependency"],
                "requirement": item["requirement"],
                "marker": item["marker"],
                "dependency_project": item["dependency_project_id"] or None,
            }
            for item in dependencies
        ],
        "has_docs": flag("has_docs"),
        "has_tests": flag("has_tests"),
        "has_ci": flag("has_ci"),
        "unavailable": UNAVAILABLE,
    }
    return {
        key: value for key, value in block.items() if value is not None and value != ""
    }


def existing_parts(path: Path) -> tuple[dict[str, Any], str]:
    """Return a project file's summary provenance and its prose body.

    The agent stage owns both, so this stage reads them back and returns them
    unchanged rather than regenerating anything it did not collect.
    """
    if not path.exists():
        return {}, ""
    text = path.read_text()
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not match:
        return {}, text.strip()
    document = yaml.safe_load(match.group(1)) or {}
    body = match.group(2).strip()
    # The heading and source link are rebuilt below, so drop the old ones
    # rather than letting a rename leave a stale title behind.
    body = re.sub(r"\A#\s+.*?\n+(Source: \[.*?\)\n+)?", "", body, count=1, flags=re.S)
    return document.get("summary", {}), body.strip()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot-date", default=None)
    # Accepted for symmetry with the other stages: this one always rewrites the
    # generated blocks, so there is nothing extra to force.
    parser.add_argument("--force", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--offline", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    snapshot_date = args.snapshot_date or newest_snapshot()
    snapshot = PATHS.snapshot(snapshot_date)

    rows = {item["id"]: item for item in read_csv(snapshot / "projects.csv")}
    metrics = metric_lookup(read_csv(snapshot / "metrics.csv"))
    dependency_groups: dict[str, list[dict[str, str]]] = {}
    for dependency in read_csv(snapshot / "dependencies.csv"):
        dependency_groups.setdefault(dependency["project_id"], []).append(dependency)
    raw_records = {}
    for line in (snapshot / "raw" / "github.jsonl").read_text().splitlines():
        if line.strip():
            record = json.loads(line)
            raw_records[record["project_id"]] = record

    target = PATHS.curated
    target.mkdir(parents=True, exist_ok=True)

    for project in load_projects():
        curated = project.model_dump(mode="json", exclude_defaults=False)
        row = rows.get(project.id, {}) | {"snapshot_date": snapshot_date}
        raw = raw_records.get(project.id, {})
        provenance, prose = existing_parts(target / f"{project.id}.md")
        document: dict[str, Any] = {"curated": curated}
        collected = collected_block(
            project.id, row, raw, metrics, dependency_groups.get(project.id, [])
        )
        if collected:
            document["collected"] = collected
        if provenance:
            document["summary"] = provenance
        front = yaml.safe_dump(document, sort_keys=False, allow_unicode=True, width=100)
        body = prose or "_No agent summary has been generated for this project._"
        # The link is repeated in the body because a person reading the file
        # should not have to assemble a URL out of two frontmatter fields.
        link = f"[{project.repository}]({project.repository_url})"
        (target / f"{project.id}.md").write_text(
            f"---\n{front}---\n\n# {project.name}\n\nSource: {link}\n\n{body}\n"
        )
    print(f"wrote {len(list(target.glob('*.md')))} project files to {target}")


if __name__ == "__main__":
    main()
