"""Build and validate the public tabular snapshot."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from packaging.requirements import InvalidRequirement, Requirement

from oss_das.core import (
    PATHS,
    load_projects,
    read_csv,
    read_json,
    read_jsonl,
    write_csv,
    write_json,
)
from oss_das.models import CatalogStatus, MetricObservation, MissingReason
from oss_das.utils import days_between, normalize_name, sha256_file, utc_now

PROJECT_FIELDS = [
    "id",
    "name",
    "status",
    "decision_reason",
    "primary_category",
    "description",
    "repository",
    "repository_url",
    "owner",
    "forge_kind",
    "forge_host",
    "homepage",
    "license_spdx",
    "license_class",
    "capabilities",
    "language",
    "created_at",
    "pushed_at",
    "latest_release_at",
    "project_age_days",
    "days_since_push",
    "days_since_release",
    "archived",
    "visibility",
    "has_docs",
    "has_tests",
    "has_ci",
    "pypi_packages",
    "conda_packages",
    "julia_packages",
    "julia_registry_status",
]

METRIC_FIELDS = [
    "project_id",
    "metric",
    "value",
    "unit",
    "window_start",
    "window_end",
    "source_url",
    "fetched_at",
    "missing_reason",
]

PUBLICATION_FIELDS = [
    "project_id",
    "doi",
    "role",
    "title",
    "publication_year",
    "work_type",
    "cited_by_count",
    "openalex_id",
    "source_url",
    "fetched_at",
    "missing_reason",
]

PYPI_DAILY_FIELDS = [
    "project_id",
    "package",
    "date",
    "downloads",
    "category",
    "source_url",
    "fetched_at",
]

DEPENDENCY_FIELDS = [
    "project_id",
    "package",
    "dependency",
    "requirement",
    "marker",
    "dependency_project_id",
    "source_url",
    "fetched_at",
]


def dependency_rows(
    packages: Iterable[dict[str, Any]], projects: Iterable[Any]
) -> list[dict[str, Any]]:
    """Normalize direct PyPI runtime requirements into auditable edges.

    This intentionally does not claim a complete software bill of materials:
    packages without a PyPI distribution and optional extras have no observed
    runtime edge here.  Each row retains the PyPI response that supplied it.
    """
    package_projects = {
        normalize_name(package): project.id
        for project in projects
        if project.status != CatalogStatus.EXCLUDED
        for package in project.registries.pypi
    }
    rows = []
    for record in packages:
        if record.get("registry") != "pypi" or record.get("missing_reason"):
            continue
        for raw in record.get("requires_dist", []):
            try:
                requirement = Requirement(raw)
            except InvalidRequirement:
                # A malformed third-party metadata entry is neither an edge
                # nor evidence that no edge exists, so leave it unclaimed.
                continue
            marker = str(requirement.marker or "")
            if "extra" in marker:
                continue
            name = normalize_name(requirement.name)
            rows.append(
                {
                    "project_id": record["project_id"],
                    "package": record["name"],
                    "dependency": name,
                    "requirement": str(requirement.specifier),
                    "marker": marker,
                    "dependency_project_id": package_projects.get(name),
                    "source_url": record["source_url"],
                    "fetched_at": record["fetched_at"],
                }
            )
    return sorted(
        rows,
        key=lambda item: (item["project_id"], item["package"], item["dependency"]),
    )


def _combined_reason(reasons: Iterable[str | None]) -> str:
    """Summarize per-record missingness for one aggregated registry metric.

    An unreachable source outranks an absent one: if any record failed to
    fetch, the aggregate cannot be claimed as "nothing was published".
    """
    collected = {reason or "unavailable" for reason in reasons}
    if "fetch_error" in collected:
        return "fetch_error"
    if collected == {"not_published"}:
        return "not_published"
    return "unavailable"


def _registry_total(
    records: list[dict[str, Any]], value_key: str, *reason_keys: str
) -> tuple[int | None, str | None]:
    """Total a registry metric only when every declared package is accounted for.

    A package that was never published contributes a genuine zero, so it does
    not block the total. A package whose source could not be read makes any
    total a guess, so no value is reported and the reason is carried instead —
    a partial sum presented as complete would understate real adoption.
    """
    observed: list[int] = []
    unaccounted: list[str | None] = []
    for record in records:
        value = record.get(value_key)
        if value is not None:
            observed.append(value)
            continue
        reason = next((record.get(key) for key in reason_keys if record.get(key)), None)
        if reason != "not_published":
            unaccounted.append(reason)
    if unaccounted:
        return None, _combined_reason(unaccounted)
    if not observed:
        return None, "not_published"
    return sum(observed), None


def _julia_status(declared: list[str], records: list[dict[str, Any]]) -> str:
    """Say whether declared Julia packages are actually in the General registry.

    Julia publishes no download counts, so registration is the only adoption
    signal available, and "declared but unregistered" is a real finding rather
    than a gap: a package installable only by URL reaches a smaller audience
    than one ``Pkg.add`` can name.
    """
    if not declared:
        return "not_applicable"
    if len(records) < len(declared):
        return "unknown"
    if all(record.get("registered") for record in records):
        return "registered"
    reasons = {
        record.get("missing_reason")
        for record in records
        if not record.get("registered")
    }
    return "unregistered" if reasons <= {"not_published"} else "unknown"


def _metric(
    project_id: str,
    name: str,
    value: int | float | None,
    unit: str,
    source_url: str,
    fetched_at: str,
    *,
    missing_reason: str | None = None,
    window_start: str | None = None,
    window_end: str | None = None,
) -> dict[str, Any]:
    reason = MissingReason(missing_reason or "unavailable") if value is None else None
    return MetricObservation(
        project_id=project_id,
        metric=name,
        value=value,
        unit=unit,
        source_url=source_url,
        fetched_at=fetched_at,
        missing_reason=reason,
        window_start=window_start,
        window_end=window_end,
    ).model_dump(mode="json")


def build_snapshot(snapshot_date: str, *, paths=PATHS) -> Path:
    snapshot = paths.snapshot(snapshot_date)
    raw = paths.raw(snapshot_date)
    projects = load_projects(paths.curated)
    github = {item["project_id"]: item for item in read_jsonl(raw / "github.jsonl")}
    packages = read_jsonl(raw / "packages.jsonl")
    dependency_packages = read_jsonl(raw / "dependencies.jsonl") or packages
    publications = read_jsonl(raw / "publications.jsonl")
    pypi_daily = read_jsonl(raw / "pypi_daily.jsonl")
    package_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    daily_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    publication_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in packages:
        package_groups[record["project_id"]].append(record)
    for record in pypi_daily:
        daily_groups[record["project_id"]].append(record)
    for record in publications:
        publication_groups[record["project_id"]].append(record)

    project_rows: list[dict[str, Any]] = []
    metric_rows: list[dict[str, Any]] = []
    capability_rows: list[dict[str, Any]] = []
    for project in projects:
        gh = github.get(project.id, {})
        row = {
            "id": project.id,
            "name": project.name,
            "status": project.status.value,
            "decision_reason": project.decision_reason,
            "primary_category": project.primary_category,
            "description": project.description,
            "repository": project.repository,
            "repository_url": project.repository_url,
            "owner": project.owner,
            "forge_kind": project.forge.kind.value,
            "forge_host": project.forge.host,
            "homepage": project.homepage,
            "license_spdx": project.license_spdx,
            "license_class": project.license_class.value,
            "capabilities": ";".join(project.capabilities),
            "language": gh.get("language"),
            "created_at": gh.get("created_at"),
            "pushed_at": gh.get("pushed_at"),
            "latest_release_at": gh.get("latest_release_at"),
            "project_age_days": days_between(gh.get("created_at"), snapshot_date),
            "days_since_push": days_between(gh.get("pushed_at"), snapshot_date),
            "days_since_release": days_between(
                gh.get("latest_release_at"), snapshot_date
            ),
            "archived": gh.get("archived"),
            "visibility": gh.get("visibility"),
            "has_docs": gh.get("has_docs"),
            "has_tests": gh.get("has_tests"),
            "has_ci": gh.get("has_ci"),
            "pypi_packages": ";".join(project.registries.pypi),
            "conda_packages": ";".join(project.registries.conda),
            "julia_packages": ";".join(project.registries.julia),
            "julia_registry_status": _julia_status(
                project.registries.julia,
                [
                    item
                    for item in package_groups.get(project.id, [])
                    if item["registry"] == "julia"
                ],
            ),
        }
        project_rows.append(row)
        capability_rows.extend(
            {
                "project_id": project.id,
                "capability": capability,
                "present": True,
                "source": "curated",
            }
            for capability in project.capabilities
        )
        if project.status == CatalogStatus.EXCLUDED:
            continue

        gh_source = gh.get("source_url", project.repository_url)
        gh_fetched = gh.get("fetched_at", f"{snapshot_date}T00:00:00+00:00")
        for name, field, unit in (
            ("repo_stars", "stars", "stars"),
            ("repo_forks", "forks", "forks"),
            ("repo_contributors", "contributors", "contributors"),
            ("repo_releases", "release_count", "releases"),
        ):
            # A field can be absent because the whole repository lookup failed
            # or because only that endpoint is closed on this host, and the
            # narrower reason is the more truthful one when both exist.
            reason = gh.get(f"{field}_missing_reason") or gh.get("missing_reason")
            metric_rows.append(
                _metric(
                    project.id,
                    name,
                    gh.get(field),
                    unit,
                    gh_source,
                    gh_fetched,
                    missing_reason=reason,
                )
            )

        package_records = package_groups.get(project.id, [])
        pypi_records = [item for item in package_records if item["registry"] == "pypi"]
        conda_records = [
            item for item in package_records if item["registry"] == "conda"
        ]
        pypi_source = (
            ";".join(
                item.get("stats_source_url", item["source_url"])
                for item in pypi_records
            )
            or "https://pypistats.org/api/"
        )
        package_fetched = next(
            (item.get("fetched_at") for item in package_records), gh_fetched
        )
        history = daily_groups.get(project.id, [])
        # A PyPI download figure can be absent because nothing was published or
        # because PyPI Stats was unreachable; keep those claims distinct.
        month_value, pypi_reason = _registry_total(
            pypi_records,
            "downloads_last_month",
            "stats_missing_reason",
            "missing_reason",
        )
        metric_rows.append(
            _metric(
                project.id,
                "pypi_downloads_30d",
                month_value,
                "downloads",
                pypi_source,
                package_fetched,
                missing_reason=pypi_reason,
                window_end=snapshot_date,
            )
        )
        # The daily history comes from the same requests as the 30-day figure,
        # so it is complete on exactly the same terms.
        history_value = (
            sum(int(item["downloads"]) for item in history)
            if history and pypi_reason is None
            else None
        )
        metric_rows.append(
            _metric(
                project.id,
                "pypi_downloads_180d",
                history_value,
                "downloads",
                pypi_source,
                package_fetched,
                missing_reason=pypi_reason,
                window_start=min((item["date"] for item in history), default=None),
                window_end=max((item["date"] for item in history), default=None),
            )
        )
        conda_value, conda_reason = _registry_total(
            conda_records, "downloads_cumulative", "missing_reason"
        )
        metric_rows.append(
            _metric(
                project.id,
                "conda_downloads_cumulative",
                conda_value,
                "downloads",
                ";".join(item["source_url"] for item in conda_records)
                or "https://api.anaconda.org/",
                package_fetched,
                missing_reason=conda_reason,
                window_end=snapshot_date,
            )
        )
        canonical = next(
            (
                item
                for item in publication_groups.get(project.id, [])
                if item["role"] == "canonical"
            ),
            None,
        )
        # A curated canonical DOI that collection has not seen yet is not the
        # same as a project that has no publication at all: the first is an
        # uncollected value, the second a genuine non-answer.
        declares_canonical = any(
            item.role == "canonical" for item in project.publications
        )
        metric_rows.append(
            _metric(
                project.id,
                "canonical_citations",
                canonical.get("cited_by_count") if canonical else None,
                "citations",
                canonical["source_url"] if canonical else "https://api.openalex.org/",
                canonical.get("fetched_at", gh_fetched) if canonical else gh_fetched,
                missing_reason=(
                    canonical.get("missing_reason")
                    if canonical
                    else ("unavailable" if declares_canonical else "not_applicable")
                ),
                window_end=snapshot_date,
            )
        )

    write_csv(snapshot / "projects.csv", project_rows, PROJECT_FIELDS)
    write_csv(snapshot / "metrics.csv", metric_rows, METRIC_FIELDS)
    write_csv(snapshot / "publications.csv", publications, PUBLICATION_FIELDS)
    write_csv(
        snapshot / "capabilities.csv",
        capability_rows,
        ["project_id", "capability", "present", "source"],
    )
    write_csv(snapshot / "pypi_daily.csv", pypi_daily, PYPI_DAILY_FIELDS)
    dependencies = dependency_rows(dependency_packages, projects)
    write_csv(snapshot / "dependencies.csv", dependencies, DEPENDENCY_FIELDS)
    files = [
        snapshot / "projects.csv",
        snapshot / "metrics.csv",
        snapshot / "publications.csv",
        snapshot / "capabilities.csv",
        snapshot / "pypi_daily.csv",
        snapshot / "dependencies.csv",
    ]
    # Discovery outputs are optional, because the dataset can be rebuilt from
    # recorded sources without rerunning a search, but they are checksummed
    # whenever they exist: the coverage file is the evidence for what the
    # search could and could not see, and it must not drift unnoticed.
    files.extend(
        path
        for name in ("candidates.csv", "discovery_coverage.csv")
        if (path := snapshot / name).exists()
    )
    manifest = {
        "schema_version": "1",
        "snapshot_date": snapshot_date,
        "generated_at": utc_now(),
        "project_count": len(project_rows),
        "included_count": sum(
            item.status == CatalogStatus.INCLUDED for item in projects
        ),
        "files": {path.name: sha256_file(path) for path in files},
        "source_notes": {
            "github": "Point-in-time public repository metadata.",
            "pypi": "Mirror-filtered PyPI Stats counts; downloads include automation.",
            "conda": "Cumulative sum of declared-channel artifact download counts.",
            "citations": "OpenAlex cited_by_count snapshot for curated DOIs.",
            "hosts": (
                "Repository signals come from whichever host publishes each "
                "project; contributor counts state their basis and are not "
                "strictly comparable across hosts."
            ),
            "licensing": (
                "Every reusable DAS code is catalogued regardless of license; "
                "license_class records reuse terms and never gates inclusion."
            ),
        },
    }
    write_json(snapshot / "manifest.json", manifest)
    return snapshot


def validate_snapshot(snapshot_date: str, *, paths=PATHS) -> None:
    snapshot = paths.snapshot(snapshot_date)
    projects = read_csv(snapshot / "projects.csv")
    metrics = read_csv(snapshot / "metrics.csv")
    publications = read_csv(snapshot / "publications.csv")
    manifest = read_json(snapshot / "manifest.json")
    ids = [item["id"] for item in projects]
    if len(ids) != len(set(ids)):
        raise ValueError("projects.csv contains duplicate project ids")
    # Every row must state a license class. An unlicensed project is a
    # finding to report, not a row to drop, so absence of a license is no
    # longer an error; absence of a *decision* about the license still is.
    unclassified = [item["id"] for item in projects if not item["license_class"]]
    if unclassified:
        raise ValueError(f"projects lack a license class: {unclassified}")
    contradictory = [
        item["id"]
        for item in projects
        if (item["license_class"] == "unlicensed") != (not item["license_spdx"])
        and item["license_class"] != "unknown"
    ]
    if contradictory:
        raise ValueError(f"license class contradicts the SPDX id: {contradictory}")
    # A private repository is not open-source software, however complete its
    # metadata looks to an authenticated collector.
    private = [
        item["id"]
        for item in projects
        if item["status"] != "excluded" and item["visibility"] == "private"
    ]
    if private:
        raise ValueError(f"catalogued projects are not public: {private}")
    metric_keys = [(item["project_id"], item["metric"]) for item in metrics]
    if len(metric_keys) != len(set(metric_keys)):
        raise ValueError("metrics.csv contains duplicate project/metric pairs")
    for item in metrics:
        # CSV blanks, not falsy numbers: a recorded 0 is a value, "" is not.
        has_value = item["value"] != ""
        has_reason = item["missing_reason"] != ""
        if has_value == has_reason:
            raise ValueError(
                f"metric must have one value or reason: {item['project_id']} "
                f"{item['metric']}"
            )
    publication_keys = [(item["project_id"], item["doi"]) for item in publications]
    if len(publication_keys) != len(set(publication_keys)):
        raise ValueError("publications.csv contains duplicate project/DOI pairs")
    for filename, expected in manifest["files"].items():
        actual = sha256_file(snapshot / filename)
        if actual != expected:
            raise ValueError(f"checksum mismatch for {filename}")
