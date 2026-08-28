"""Shared collection workflows used by the numbered scripts."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from oss_das.clients import (
    CondaClient,
    ForgeClient,
    GiteaClient,
    GitHubClient,
    GitLabClient,
    JuliaRegistryClient,
    OpenAlexClient,
    PyPIClient,
    PyPIStatsClient,
)
from oss_das.clients.base import NotFoundError, SourceError
from oss_das.models import CatalogStatus, ForgeKind, ProjectRecord
from oss_das.utils import normalize_name, utc_now

#: Full-text queries for hosts that index README content, which is where a
#: package usually spells out the phrase its name abbreviates. The physics
#: names (OTDR spellings) and the vendor names matter as much as the topic
#: label: interrogator-adjacent tooling rarely calls itself "DAS" anywhere a
#: name-only search would reach.
GITHUB_DISCOVERY_QUERIES = (
    '"distributed acoustic sensing" in:name,description,readme',
    '"distributed fiber optic sensing" in:name,description,readme',
    '"distributed fibre optic sensing" in:name,description,readme',
    '"distributed strain sensing" in:name,description,readme',
    '"distributed temperature sensing" in:name,description,readme',
    '"phase-sensitive OTDR" in:name,description,readme',
    '"phi-OTDR" OR "φ-OTDR" in:name,description,readme',
    '"acoustic sensing" interrogator in:name,description,readme',
    "silixa OR optasense OR optodas OR febus OR terra15 OR sintela in:name,description,readme",
    "topic:distributed-acoustic-sensing",
    "topic:fiber-optic-sensing",
    "topic:dfos",
    "distributed acoustic sensing language:MATLAB",
    "distributed acoustic sensing language:Julia",
    "distributed acoustic sensing language:R",
)

#: Hosts whose search covers only project names and descriptions. The phrases
#: are kept short because a name-only index will not match a sentence.
PATH_SEARCH_QUERIES = (
    "distributed acoustic sensing",
    "fiber optic sensing",
    "das",
    "otdr",
)

#: Probes that match a bare acronym. They are worth running — GEOFON's
#: ``dastools`` is only reachable through one — but "das" also matches German
#: prose, dashboards, and a blockchain naming service, so a candidate found
#: *only* this way is labelled broad. Without the label, a headline count of
#: everything discovered would invite the reader to treat thousands of
#: unrelated repositories as an ecosystem.
BROAD_QUERIES = frozenset({"das", "otdr"})

#: Non-GitHub hosts worth sweeping. GEOFON's ``dastools`` lives on the GFZ
#: instance, so this list is the difference between cataloguing that package
#: and reporting an ecosystem that happens to end at github.com.
FORGE_HOSTS: tuple[tuple[ForgeKind, str], ...] = (
    (ForgeKind.GITLAB, "gitlab.com"),
    (ForgeKind.GITLAB, "git.gfz-potsdam.de"),
    (ForgeKind.GITLAB, "code.usgs.gov"),
    (ForgeKind.GITLAB, "codebase.helmholtz.cloud"),
    (ForgeKind.GITEA, "codeberg.org"),
    (ForgeKind.GITEA, "git.pyrocko.org"),
)

#: Every way a source lookup is allowed to fail without ending the collection.
SOURCE_FAILURES = (SourceError, KeyError, TypeError)


def missingness(
    error: Exception, *, absent_reason: str, prefix: str = ""
) -> dict[str, Any]:
    """Describe a failed lookup as a missingness reason, never as a zero.

    ``NotFoundError`` means the record genuinely does not exist, which is a
    different claim from "we could not reach the source", so the two get
    different reasons. ``prefix`` namespaces the keys for records that carry
    more than one source, such as PyPI metadata alongside PyPI Stats.
    """
    if isinstance(error, NotFoundError):
        return {f"{prefix}missing_reason": absent_reason}
    return {f"{prefix}missing_reason": "fetch_error", f"{prefix}error": str(error)}


def open_forges(github_token: str | None = None) -> list[ForgeClient]:
    """Build one client per configured host, GitHub first when a token is given.

    Without a token GitHub is left out rather than probed anonymously: the
    unauthenticated search budget is ten requests a minute, and a discovery
    run that hammers it produces a coverage ledger full of throttled rows
    instead of one honest "skipped". Callers own the returned clients and are
    expected to close them; every client is a context manager, so an
    ``ExitStack`` closes the whole set.
    """
    builders = {ForgeKind.GITLAB: GitLabClient, ForgeKind.GITEA: GiteaClient}
    forges: list[ForgeClient] = [GitHubClient(github_token)] if github_token else []
    forges.extend(builders[kind](host) for kind, host in FORGE_HOSTS)
    return forges


def collect_repositories(
    forges: Iterable[ForgeClient], projects: Iterable[ProjectRecord]
) -> list[dict[str, Any]]:
    """Collect repository signals for each project from whichever host holds it.

    A project whose host has no configured client is reported with a reason
    rather than skipped, because a silently absent row and a project with no
    activity look identical once they reach a chart.
    """
    by_host = {(forge.kind, forge.host): forge for forge in forges}
    output = []
    for project in projects:
        if project.status == CatalogStatus.EXCLUDED:
            continue
        forge = by_host.get((project.forge.kind, project.forge.host))
        record: dict[str, Any] = {
            "project_id": project.id,
            "repository": project.repository,
            "forge_kind": project.forge.kind.value,
            "forge_host": project.forge.host,
            "source_url": project.repository_url,
            "fetched_at": utc_now(),
        }
        if forge is None:
            record["missing_reason"] = "unavailable"
            record["error"] = f"no client configured for {project.forge.host}"
            output.append(record)
            continue
        try:
            record.update(
                forge.collect_repository(project.repository), missing_reason=None
            )
        except SOURCE_FAILURES as error:
            record.update(missingness(error, absent_reason="unavailable"))
        output.append(record)
    return output


def collect_julia(
    registry: JuliaRegistryClient, projects: Iterable[ProjectRecord]
) -> list[dict[str, Any]]:
    """Check every declared Julia package against the General registry.

    Julia publishes no download counts, so registration is the only claim
    this census can verify. It is worth verifying: the catalog previously
    asserted a General-registry name for a package that was never registered
    there, and nothing in the pipeline was positioned to notice.
    """
    output = []
    for project in projects:
        if project.status == CatalogStatus.EXCLUDED:
            continue
        for package in project.registries.julia:
            record: dict[str, Any] = {
                "project_id": project.id,
                "registry": "julia",
                "name": package,
                "fetched_at": utc_now(),
                "source_url": (
                    f"https://github.com/JuliaRegistries/General/tree/master/"
                    f"{package[0].upper()}/{package}"
                ),
            }
            try:
                record.update(registry.package(package), missing_reason=None)
            except SOURCE_FAILURES as error:
                record["registered"] = False
                record.update(missingness(error, absent_reason="not_published"))
            output.append(record)
    return output


def collect_packages(
    pypi: PyPIClient,
    stats: PyPIStatsClient,
    conda: CondaClient,
    projects: Iterable[ProjectRecord],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    records: list[dict[str, Any]] = []
    daily: list[dict[str, Any]] = []
    for project in projects:
        if project.status == CatalogStatus.EXCLUDED:
            continue
        for package in project.registries.pypi:
            fetched_at = utc_now()
            stats_package = normalize_name(package)
            record: dict[str, Any] = {
                "project_id": project.id,
                "registry": "pypi",
                "name": package,
                "source_url": f"https://pypi.org/pypi/{package}/json",
                "fetched_at": fetched_at,
            }
            try:
                record.update(pypi.package(package), missing_reason=None)
            except SOURCE_FAILURES as error:
                # Nothing on PyPI means nothing on PyPI Stats either.
                record.update(missingness(error, absent_reason="not_published"))
                records.append(record)
                continue
            # Recorded before the request so a failed download metric still
            # cites PyPI Stats rather than falling back to the PyPI URL.
            record["stats_source_url"] = (
                f"https://pypistats.org/api/packages/{stats_package}/recent"
            )
            try:
                recent, history = stats.package(stats_package)
            except SOURCE_FAILURES as error:
                record.update(
                    missingness(error, absent_reason="unavailable", prefix="stats_")
                )
            else:
                record.update(
                    downloads_last_day=recent.get("last_day"),
                    downloads_last_week=recent.get("last_week"),
                    downloads_last_month=recent.get("last_month"),
                    stats_missing_reason=None,
                )
                daily.extend(
                    {
                        "project_id": project.id,
                        "package": package,
                        "date": item["date"],
                        "downloads": item["downloads"],
                        "category": item.get("category", "without_mirrors"),
                        "source_url": (
                            "https://pypistats.org/api/packages/"
                            f"{stats_package}/overall?mirrors=false"
                        ),
                        "fetched_at": fetched_at,
                    }
                    for item in history
                )
            records.append(record)

        for identifier in project.registries.conda:
            channel, name = identifier.split("/", 1)
            record = {
                "project_id": project.id,
                "registry": "conda",
                "channel": channel,
                "name": name,
                "source_url": f"https://api.anaconda.org/package/{channel}/{name}",
                "fetched_at": utc_now(),
            }
            try:
                record.update(conda.package(channel, name), missing_reason=None)
            except SOURCE_FAILURES as error:
                record.update(missingness(error, absent_reason="not_published"))
            records.append(record)
    return records, sorted(daily, key=lambda item: (item["project_id"], item["date"]))


def probe_conda_forge(
    conda: CondaClient, projects: Iterable[ProjectRecord]
) -> list[dict[str, Any]]:
    """Report conda-forge packages that exist but are absent from curation.

    Conda identifiers are hand-declared, so an undeclared package is never
    looked for and is published as "not_published" — an unasked question
    reported as a finding. This only suggests what to review; like discovery,
    it never changes a curated decision. A package that could not be checked
    is reported too, because silence must not read as absence.
    """
    findings: list[dict[str, Any]] = []
    for project in projects:
        if project.status == CatalogStatus.EXCLUDED:
            continue
        declared = {item.lower() for item in project.registries.conda}
        for package in project.registries.pypi:
            identifier = f"conda-forge/{normalize_name(package)}"
            if identifier in declared:
                continue
            finding = {"project_id": project.id, "identifier": identifier}
            try:
                conda.package(*identifier.split("/", 1))
            except NotFoundError:
                continue
            except SOURCE_FAILURES as error:
                findings.append(finding | {"status": "unchecked", "error": str(error)})
                continue
            findings.append(finding | {"status": "undeclared"})
    return findings


def collect_publications(
    openalex: OpenAlexClient, projects: Iterable[ProjectRecord]
) -> list[dict[str, Any]]:
    output = []
    for project in projects:
        if project.status == CatalogStatus.EXCLUDED:
            continue
        for reference in project.publications:
            record: dict[str, Any] = {
                "project_id": project.id,
                "doi": reference.doi,
                "role": reference.role,
                "note": reference.note,
                "source_url": (
                    f"https://api.openalex.org/works/https://doi.org/{reference.doi}"
                ),
                "fetched_at": utc_now(),
            }
            try:
                record.update(openalex.work_by_doi(reference.doi), missing_reason=None)
            except SOURCE_FAILURES as error:
                record.update(missingness(error, absent_reason="unavailable"))
            output.append(record)
    return output
