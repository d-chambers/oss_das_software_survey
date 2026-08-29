#!/usr/bin/env python3
"""Join the catalogue with every measurement into the two tables the notebook reads.

Reads:  data/curated/*.md, data/measured/<source>/<id>.md, data/commits/<id>.csv
Writes: notebooks/public/ecosystem.csv  (one row per curated project, wide)
        notebooks/public/commits.csv    (one row per commit, every project)

Refuses to build when any curated project lacks a measured file from any
source, or when any measured file is older than ``--max-age`` days, so a
crashed B run cannot be joined silently with a stale one. ``--allow-stale``
turns the refusal into a warning. Measured files whose id matches no curated
project are ignored.

Measured file contract (frontmatter only; every B script writes one source):

    common        id, source, scanned_at, missing: {metric: reason}
    mirror        repository_url, result, error, path, repo_bytes
    git           ref, tip, commits, merges, first_commit_at, last_commit_at,
                  authors, insertions, deletions, lines_total,
                  lines_by_language: {language: lines}, primary_language
    forge         source_url, stars, forks, contributors, contributors_basis,
                  releases, created_at, pushed_at, last_commit_at,
                  latest_release_at, archived, visibility, language,
                  language_bytes: {}, has_docs, has_tests, has_ci,
                  license_detected, license_detected_vocabulary
    registry      pypi: [{name, version, latest_upload_at, release_count,
                  downloads_30d, downloads_180d, requires_dist: [], missing}],
                  conda: [{channel, name, downloads_total, missing}],
                  julia: [{name, registered, missing}],
                  pypi_downloads_30d, pypi_downloads_180d, conda_downloads_total,
                  dependencies: [names]
    publications  publications: [{doi, role, title, year, work_type,
                  cited_by_count, openalex_id, missing}],
                  citations_total, canonical_citations

Downloads and citations are summed across a project's packages and DOIs by
the B scripts; this stage only flattens.
"""

from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime, timedelta
from typing import Any

from oss_das.core import (
    MEASURED_SOURCES,
    PATHS,
    load_projects,
    read_csv,
    read_frontmatter,
    write_csv,
)
from oss_das.models import ProjectRecord

CURATED_FIELDS = [
    "id",
    "name",
    "repository",
    "repository_url",
    "forge_kind",
    "forge_host",
    "owner",
    "homepage",
    "description",
    "status",
    "decision_reason",
    "primary_category",
    "capabilities",
    "das_focus",
    "license_spdx",
    "license_class",
    "pypi",
    "conda",
    "julia",
    "canonical_doi",
    "reviewed_at",
]

#: (column, source, key) — the measured value each column is read from.
MEASURED_COLUMNS: list[tuple[str, str, str]] = [
    ("mirror_result", "mirror", "result"),
    ("mirror_error", "mirror", "error"),
    ("git_ref", "git", "ref"),
    ("commits", "git", "commits"),
    ("merges", "git", "merges"),
    ("first_commit_at", "git", "first_commit_at"),
    ("last_commit_at", "git", "last_commit_at"),
    ("authors", "git", "authors"),
    ("insertions", "git", "insertions"),
    ("deletions", "git", "deletions"),
    ("lines_total", "git", "lines_total"),
    ("lines_by_language", "git", "lines_by_language"),
    ("primary_language", "git", "primary_language"),
    ("stars", "forge", "stars"),
    ("forks", "forge", "forks"),
    ("contributors", "forge", "contributors"),
    ("contributors_basis", "forge", "contributors_basis"),
    ("releases", "forge", "releases"),
    ("created_at", "forge", "created_at"),
    ("pushed_at", "forge", "pushed_at"),
    ("forge_last_commit_at", "forge", "last_commit_at"),
    ("latest_release_at", "forge", "latest_release_at"),
    ("archived", "forge", "archived"),
    ("visibility", "forge", "visibility"),
    ("language", "forge", "language"),
    ("has_docs", "forge", "has_docs"),
    ("has_tests", "forge", "has_tests"),
    ("has_ci", "forge", "has_ci"),
    ("license_detected", "forge", "license_detected"),
    ("pypi_downloads_30d", "registry", "pypi_downloads_30d"),
    ("pypi_downloads_180d", "registry", "pypi_downloads_180d"),
    ("conda_downloads_total", "registry", "conda_downloads_total"),
    ("dependencies", "registry", "dependencies"),
    ("practices", "practices", "practices"),
    ("has_python", "dependencies", "has_python"),
    ("requires", "dependencies", "required"),
    ("optional_requires", "dependencies", "optional"),
    ("citations_total", "publications", "citations_total"),
    ("canonical_citations", "publications", "canonical_citations"),
]

FIELDS = (
    CURATED_FIELDS
    + [column for column, _, _ in MEASURED_COLUMNS]
    + [f"{source}_missing" for source in MEASURED_SOURCES]
    + [f"{source}_scanned_at" for source in MEASURED_SOURCES]
)


def cell(value: Any) -> str:
    """Flatten a frontmatter value into one CSV cell."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, dict):
        return ";".join(f"{k}={v}" for k, v in value.items())
    if isinstance(value, list):
        return ";".join(str(v) for v in value)
    return str(value)


def curated_row(project: ProjectRecord) -> dict[str, str]:
    canonical = next((p.doi for p in project.publications if p.role == "canonical"), "")
    return {
        "id": project.id,
        "name": project.name,
        "repository": project.repository or "",
        "repository_url": project.repository_url or "",
        "forge_kind": project.forge.kind.value if project.repository else "",
        "forge_host": project.forge.host if project.repository else "",
        "owner": project.owner or "",
        "homepage": project.homepage or "",
        "description": project.description,
        "status": project.status.value,
        "decision_reason": project.decision_reason,
        "primary_category": project.primary_category,
        "capabilities": ";".join(project.capabilities),
        "das_focus": project.das_focus.value,
        "license_spdx": project.license_spdx or "",
        "license_class": project.license_class.value,
        "pypi": ";".join(project.registries.pypi),
        "conda": ";".join(project.registries.conda),
        "julia": ";".join(project.registries.julia),
        "canonical_doi": canonical,
        "reviewed_at": project.reviewed_at or "",
    }


def load_measured(source: str) -> dict[str, dict[str, Any]]:
    out = {}
    for path in (
        sorted(PATHS.measured(source).glob("*.md"))
        if PATHS.measured(source).exists()
        else []
    ):
        front = read_frontmatter(path)
        if front.get("id") != path.stem or front.get("source") != source:
            raise ValueError(
                f"{path}: frontmatter id/source {front.get('id')!r}/"
                f"{front.get('source')!r} do not match the file"
            )
        out[path.stem] = front
    return out


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--max-age", type=int, default=7, help="Days before a measurement is stale."
    )
    parser.add_argument(
        "--allow-stale", action="store_true", help="Warn instead of refusing."
    )
    args = parser.parse_args()

    projects = load_projects()
    measured = {source: load_measured(source) for source in MEASURED_SOURCES}
    now = datetime.now(UTC)
    problems: list[str] = []
    for project in projects:
        for source in MEASURED_SOURCES:
            record = measured[source].get(project.id)
            if record is None:
                problems.append(f"{project.id}: no {source} measurement")
                continue
            scanned = record.get("scanned_at")
            try:
                age = now - datetime.fromisoformat(str(scanned)).astimezone(UTC)
            except ValueError:
                problems.append(
                    f"{project.id}: {source} has no usable scanned_at ({scanned!r})"
                )
                continue
            if age > timedelta(days=args.max_age):
                problems.append(f"{project.id}: {source} is {age.days} days old")
    if problems:
        for line in problems[:40]:
            print(f"  {line}", file=sys.stderr)
        if len(problems) > 40:
            print(f"  ... {len(problems) - 40} more", file=sys.stderr)
        if not args.allow_stale:
            print(
                f"refusing to build: {len(problems)} missing or stale measurements (--allow-stale to override)",
                file=sys.stderr,
            )
            return 1
        print(
            f"warning: building with {len(problems)} missing or stale measurements",
            file=sys.stderr,
        )

    rows = []
    for project in projects:
        row = curated_row(project)
        for column, source, key in MEASURED_COLUMNS:
            row[column] = cell(measured[source].get(project.id, {}).get(key))
        for source in MEASURED_SOURCES:
            record = measured[source].get(project.id, {})
            row[f"{source}_missing"] = cell(record.get("missing") or {})
            row[f"{source}_scanned_at"] = cell(record.get("scanned_at"))
        rows.append(row)
    write_csv(PATHS.public / "ecosystem.csv", rows, FIELDS)

    ids = {project.id for project in projects}
    commit_rows: list[dict[str, str]] = []
    fields: list[str] = []
    for path in sorted(PATHS.commits.glob("*.csv")):
        if path.stem not in ids:
            continue
        table = read_csv(path)
        for record in table:
            record.setdefault("project_id", path.stem)
            record.pop("status", None)
            commit_rows.append(record)
        for key in table[0].keys() if table else []:
            if key not in fields and key != "status":
                fields.append(key)
    if "project_id" in fields:
        fields.remove("project_id")
    write_csv(PATHS.public / "commits.csv", commit_rows, ["project_id", *fields])
    print(
        f"wrote {len(rows)} projects and {len(commit_rows)} commits to {PATHS.public}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
