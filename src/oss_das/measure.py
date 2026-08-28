"""Build one measured record per curated project for each B source.

Reads:  data/repos/<id>.git and the public APIs behind the clients
Writes: data/measured/<source>/<id>.md (through :func:`write_measured`) and
        data/commits/<id>.csv (through :func:`write_commits`)

Every builder returns the frontmatter of one ``data/measured/<source>/<id>.md``
file in the shape ``scripts/c010_build_tables.py`` documents. Every curated
project gets a record from every source, whatever its status: a value no
source publishes goes under ``missing`` with a reason, never as a zero, and a
project a source cannot speak about at all (no repository, no packages, no
DOIs) gets ``not_applicable`` so the build stage still sees a file for it.
"""

from __future__ import annotations

import re
import shutil
from collections import Counter
from collections.abc import Iterable
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any

from packaging.requirements import InvalidRequirement, Requirement

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
from oss_das.clients.base import NotFoundError
from oss_das.collection import SOURCE_FAILURES
from oss_das.commits import (
    COMMIT_FIELDS,
    CommitStat,
    GitError,
    clone_or_update,
    directory_bytes,
    read_commits,
    resolve_mainline,
    run_git,
)
from oss_das.core import load_projects, write_csv, write_record
from oss_das.loc import measure_repo
from oss_das.models import ForgeKind, ProjectRecord
from oss_das.utils import normalize_name, utc_now

GIB = 1024**3

#: The commit CSV columns. ``status`` is curated, not measured, so it is not
#: exported; the build stage joins it back from the catalogue.
GIT_COMMIT_FIELDS = [field for field in COMMIT_FIELDS if field != "status"]

#: Commit identities that are automation rather than people.
BOT = re.compile(r"(\[bot\]|dependabot|github-action|pre-commit-ci|renovate)", re.I)

#: The forge fields the build stage reads, in the order they are written.
FORGE_FIELDS = (
    "stars",
    "forks",
    "contributors",
    "contributors_basis",
    "releases",
    "created_at",
    "pushed_at",
    "last_commit_at",
    "latest_release_at",
    "archived",
    "visibility",
    "language",
    "language_bytes",
    "has_docs",
    "has_tests",
    "has_ci",
    "license_detected",
    "license_detected_vocabulary",
)

#: Days of PyPI Stats daily history summed into ``downloads_180d``.
DOWNLOAD_WINDOW_DAYS = 180


# --- shared -------------------------------------------------------------------


def select_projects(only: Iterable[str] | None = None) -> list[ProjectRecord]:
    """Every curated project, whatever its status, or just the ids named."""
    projects = load_projects()
    if only is None:
        return projects
    wanted = set(only)
    unknown = wanted - {project.id for project in projects}
    if unknown:
        raise SystemExit(f"unknown project ids: {', '.join(sorted(unknown))}")
    return [project for project in projects if project.id in wanted]


def write_measured(source: str, record: dict[str, Any], directory: Path) -> Path:
    """Stamp ``scanned_at`` and write ``directory/<id>.md``, frontmatter only.

    The common keys come first so a record reads the same whichever source
    wrote it; ``missing`` is always present, and always last.
    """
    body = {
        k: v
        for k, v in record.items()
        if k not in {"id", "source", "scanned_at", "missing"}
    }
    front = {
        "id": record["id"],
        "source": source,
        "scanned_at": utc_now(),
        **body,
        "missing": dict(record.get("missing") or {}),
    }
    path = directory / f"{record['id']}.md"
    write_record(path, front)
    return path


def missing_reason(error: Exception, *, absent: str) -> str:
    """A 404 is a different claim from an unreachable source."""
    return absent if isinstance(error, NotFoundError) else "fetch_error"


def mirror_path(repos: Path, project_id: str) -> Path:
    return repos / f"{project_id}.git"


# --- mirror -------------------------------------------------------------------


def mirror_record(
    project: ProjectRecord,
    repos: Path,
    *,
    update: bool = False,
    timeout: int = 1800,
    min_free_gb: float = 0.0,
) -> dict[str, Any]:
    """Clone or refresh one project's bare mirror and describe the outcome.

    ``result`` is ``cloned``, ``updated``, ``unchanged`` (a mirror exists and
    ``update`` is off), ``failed``, or ``not_applicable`` for a project with
    no repository. The free-space check only guards a fresh clone; concurrent
    workers may each pass it, so it is a floor rather than a guarantee.
    """
    record: dict[str, Any] = {
        "id": project.id,
        "repository_url": project.repository_url,
        "result": None,
        "error": "",
        "path": None,
        "repo_bytes": None,
        "missing": {},
    }
    if project.repository is None:
        record["result"] = "not_applicable"
        record["missing"] = {"repository": "not_applicable"}
        return record
    path = mirror_path(repos, project.id)
    record["path"] = str(path)
    if not path.exists() and min_free_gb > 0:
        repos.mkdir(parents=True, exist_ok=True)
        free = shutil.disk_usage(repos).free / GIB
        if free < min_free_gb:
            record["result"] = "failed"
            record["error"] = f"insufficient disk space ({free:.1f} GiB free)"
            record["missing"] = {"mirror": "unavailable"}
            return record
    try:
        result = clone_or_update(
            project.repository_url, path, update=update, timeout=timeout
        )
    except GitError as error:
        record["result"] = "failed"
        record["error"] = str(error)
        record["missing"] = {"mirror": "fetch_error"}
    else:
        record["result"] = "unchanged" if result == "skipped" else result
    if path.exists():
        record["repo_bytes"] = directory_bytes(path)
    return record


# --- git ----------------------------------------------------------------------


def count_authors(identities: Iterable[tuple[str, str]]) -> int:
    """Count distinct people across (name, email) commit identities.

    Git identities fork: the same person commits as two names, or one name
    against several addresses. Names and addresses are joined into one
    identity graph and its components counted, rather than taking distinct
    names (which merges two people who share a name) or distinct addresses
    (which splits one person across their laptop and their CI). Bots are left
    out.
    """
    parent: dict[tuple[str, str], tuple[str, str]] = {}

    def find(node: tuple[str, str]) -> tuple[str, str]:
        parent.setdefault(node, node)
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node

    people: list[tuple[str, str]] = []
    for name, email in identities:
        name, email = name.strip().lower(), email.strip().lower()
        if BOT.search(name) or BOT.search(email):
            continue
        root_name, root_email = find(("name", name)), find(("email", email))
        if root_name != root_email:
            parent[root_name] = root_email
        people.append(("name", name))
    return len({find(person) for person in people})


def commit_rows(
    project: ProjectRecord, commits: Iterable[CommitStat]
) -> list[dict[str, Any]]:
    return [
        {k: v for k, v in commit.row(project).items() if k != "status"}
        for commit in commits
    ]


def write_commits(path: Path, rows: list[dict[str, Any]]) -> None:
    """Write the commit CSV via a temporary name so an interrupted run cannot
    leave a truncated file that later looks complete."""
    staging = path.with_name(f"{path.name}.partial")
    write_csv(staging, rows, GIT_COMMIT_FIELDS)
    staging.replace(path)


def git_record(
    project: ProjectRecord, repos: Path, *, timeout: int = 900
) -> tuple[dict[str, Any], list[CommitStat]]:
    """Measure one project's mirror without the network.

    Returns the record and the commits it was built from, so the caller can
    export them. A project with no repository is ``not_applicable``; one whose
    mirror is absent is ``unavailable``; a mirror git cannot read is a
    ``fetch_error`` with the message.
    """
    record: dict[str, Any] = {
        "id": project.id,
        "ref": None,
        "tip": None,
        "commits": None,
        "merges": None,
        "first_commit_at": None,
        "last_commit_at": None,
        "authors": None,
        "insertions": None,
        "deletions": None,
        "lines_total": None,
        "lines_by_language": {},
        "primary_language": None,
        "error": "",
        "missing": {},
    }
    if project.repository is None:
        record["missing"] = {"git": "not_applicable"}
        return record, []
    repo = mirror_path(repos, project.id)
    if not repo.exists():
        record["missing"] = {"git": "unavailable"}
        record["error"] = f"no mirror at {repo}"
        return record, []
    try:
        ref = resolve_mainline(repo, timeout=timeout)
        if ref is None:
            # An empty repository or a broken mirror: nothing was measured,
            # which is different from a repository with no commits.
            record["missing"] = {"git": "unavailable"}
            record["error"] = "no mainline ref"
            return record, []
        tip = run_git(
            ["-C", str(repo), "rev-parse", f"{ref}^{{commit}}"], timeout=timeout
        ).strip()
        commits = read_commits(repo, ref, timeout=timeout)
        languages = measure_repo(repo, ref, timeout=timeout)
    except GitError as error:
        record["missing"] = {"git": "fetch_error"}
        record["error"] = str(error)
        return record, []
    # Sorted as instants, not strings: authored_at carries the author's local
    # UTC offset, so lexical order is wrong across timezones.
    dates = sorted((c.authored_at for c in commits), key=datetime.fromisoformat)
    measured = [c for c in commits if not c.is_merge]
    record.update(
        ref=ref,
        tip=tip,
        commits=len(commits),
        merges=sum(1 for c in commits if c.is_merge),
        first_commit_at=dates[0] if dates else None,
        last_commit_at=dates[-1] if dates else None,
        authors=count_authors((c.author_name, c.author_email) for c in commits),
        insertions=_sum_or_none(c.insertions for c in measured),
        deletions=_sum_or_none(c.deletions for c in measured),
        lines_by_language=dict(sorted(languages.items())),
    )
    for field in ("insertions", "deletions"):
        if record[field] is None:
            record.setdefault("missing", {})[field] = "not_published"
    if languages:
        record["lines_total"] = sum(languages.values())
        record["primary_language"] = max(
            languages, key=lambda name: (languages[name], name)
        )
    else:
        # No counted source at the tip is a finding, not a total of zero.
        record["missing"] = {"lines": "not_published"}
    return record, commits


# --- forge --------------------------------------------------------------------


class ForgeClients:
    """One client per host, opened on demand and closed together.

    GitHub is only opened with a token: the unauthenticated limit is sixty
    requests an hour and one repository costs several, so a tokenless run
    would fail most of the catalogue after hammering the limit. GitLab and
    Gitea instances answer public reads without one.
    """

    def __init__(self, github_token: str | None = None) -> None:
        self.github_token = github_token
        self._clients: dict[tuple[ForgeKind, str], ForgeClient] = {}

    def get(self, kind: ForgeKind, host: str) -> ForgeClient | None:
        key = (kind, host)
        if key not in self._clients:
            if kind == ForgeKind.GITHUB:
                if not self.github_token:
                    return None
                self._clients[key] = GitHubClient(self.github_token, host=host)
            elif kind == ForgeKind.GITLAB:
                self._clients[key] = GitLabClient(host)
            else:
                self._clients[key] = GiteaClient(host)
        return self._clients[key]

    def close(self) -> None:
        for client in self._clients.values():
            client.close()
        self._clients.clear()

    def __enter__(self) -> ForgeClients:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


def forge_fields(raw: dict[str, Any]) -> dict[str, Any]:
    """Reduce a client's repository payload to the contract fields plus reasons.

    The clients already name what they could not read (``*_missing_reason``);
    those reasons are carried over under the contract's field names, and any
    contract field the host left empty is reported as ``not_published``,
    except ``latest_release_at``, which is simply inapplicable to a project
    that has never made a release.
    """
    record: dict[str, Any] = {"source_url": raw.get("source_url")}
    for field in FORGE_FIELDS:
        record[field] = raw.get("release_count" if field == "releases" else field)
    missing: dict[str, str] = {}
    carried = {
        "contributors": "contributors_missing_reason",
        "last_commit_at": "commits_missing_reason",
        "license_detected": "license_detected_missing_reason",
    }
    for field, key in carried.items():
        if record.get(field) is None and raw.get(key):
            missing[field] = raw[key]
    if raw.get("tree_truncated"):
        # A file not seen in a truncated listing may still exist, so only a
        # positive signal survives; a negative one is unsupported.
        for field in ("has_docs", "has_tests", "has_ci"):
            if record[field] is False:
                record[field] = None
                missing[field] = "unavailable"
    for field in FORGE_FIELDS:
        value = record[field]
        if field in missing or value not in (None, {}):
            continue
        if field == "latest_release_at" and not record.get("releases"):
            missing[field] = "not_applicable"
        else:
            missing[field] = "not_published"
    record["missing"] = missing
    return record


def forge_record(project: ProjectRecord, clients: ForgeClients) -> dict[str, Any]:
    """Read one project's host API record, or say why it could not be read."""
    record: dict[str, Any] = {
        "id": project.id,
        "source_url": project.repository_url,
        **dict.fromkeys(FORGE_FIELDS),
        "error": "",
        "missing": {},
    }
    if project.repository is None:
        record["missing"] = {"repository": "not_applicable"}
        return record
    client = clients.get(project.forge.kind, project.forge.host)
    if client is None:
        record["missing"] = {"repository": "unavailable"}
        record["error"] = (
            "no GITHUB_TOKEN"
            if project.forge.kind == ForgeKind.GITHUB
            else f"no client for {project.forge.host}"
        )
        return record
    try:
        raw = client.collect_repository(project.repository)
    except SOURCE_FAILURES as error:
        record["missing"] = {"repository": missing_reason(error, absent="unavailable")}
        record["error"] = str(error)
        return record
    record.update(forge_fields(raw))
    return record


# --- registry -----------------------------------------------------------------


def dependency_names(requires_dist: Iterable[str]) -> list[str]:
    """Direct runtime requirement names, normalized, extras-only ones dropped.

    A requirement whose marker names an extra (``; extra == "docs"``) is not
    pulled in by a plain install, so it is not a runtime dependency. Names are
    PEP 503 normalized so ``PyYAML`` and ``pyyaml`` are one dependency.
    """
    names: set[str] = set()
    for text in requires_dist:
        try:
            requirement = Requirement(text)
        except InvalidRequirement:
            # Keep the leading name even when the rest does not parse: the
            # dependency is real, only its specifier is malformed.
            head = re.match(r"\s*([A-Za-z0-9][A-Za-z0-9._-]*)", text)
            if head and "extra ==" not in text.split(";", 1)[-1]:
                names.add(normalize_name(head.group(1)))
            continue
        if requirement.marker is not None and "extra ==" in str(requirement.marker):
            continue
        names.add(normalize_name(requirement.name))
    return sorted(names)


def downloads_in_window(
    daily: Iterable[dict[str, Any]],
    *,
    days: int = DOWNLOAD_WINDOW_DAYS,
    today: date | None = None,
) -> int | None:
    """Sum daily download rows dated within the last ``days`` days.

    None, not zero, when no usable row falls inside the window: PyPI Stats
    publishes a row per day it observed, so an empty window is an absence of
    observations rather than a count of none.
    """
    today = today or datetime.now(UTC).date()
    start = today - timedelta(days=days)
    total: int | None = None
    for item in daily:
        try:
            when = date.fromisoformat(str(item.get("date", ""))[:10])
        except ValueError:
            continue
        if start < when <= today and item.get("downloads") is not None:
            total = (total or 0) + int(item["downloads"])
    return total


def _note_unpublished(record: dict[str, Any], fields: Iterable[str]) -> None:
    """A field the source answered but left empty is unpublished, not zero."""
    for field in fields:
        if record.get(field) is None:
            record["missing"].setdefault(field, "not_published")


def pypi_package_record(
    name: str, pypi: PyPIClient, stats: PyPIStatsClient, *, today: date | None = None
) -> dict[str, Any]:
    record: dict[str, Any] = {
        "name": name,
        "version": None,
        "latest_upload_at": None,
        "release_count": None,
        "downloads_30d": None,
        "downloads_180d": None,
        "requires_dist": [],
        "source_url": f"https://pypi.org/pypi/{name}/json",
        "missing": {},
    }
    try:
        info = pypi.package(name)
    except SOURCE_FAILURES as error:
        # Nothing on PyPI means nothing on PyPI Stats either.
        reason = missing_reason(error, absent="not_published")
        record["missing"] = {"metadata": reason, "downloads": reason}
        record["error"] = str(error)
        return record
    record.update(
        version=info.get("version"),
        latest_upload_at=info.get("latest_upload_at"),
        release_count=info.get("release_count"),
        requires_dist=(
            None if info.get("requires_dist") is None else list(info["requires_dist"])
        ),
    )
    _note_unpublished(
        record, ("version", "latest_upload_at", "release_count", "requires_dist")
    )
    stats_name = normalize_name(name)
    record["stats_source_url"] = (
        f"https://pypistats.org/api/packages/{stats_name}/recent"
    )
    try:
        recent, daily = stats.package(stats_name)
    except SOURCE_FAILURES as error:
        record["missing"] = {"downloads": missing_reason(error, absent="unavailable")}
        record["error"] = str(error)
        return record
    record["downloads_30d"] = recent.get("last_month")
    record["downloads_180d"] = downloads_in_window(daily, today=today)
    _note_unpublished(record, ("downloads_30d", "downloads_180d"))
    return record


def conda_package_record(identifier: str, conda: CondaClient) -> dict[str, Any]:
    channel, _, name = identifier.partition("/")
    record: dict[str, Any] = {
        "channel": channel,
        "name": name,
        "downloads_total": None,
        "source_url": f"https://api.anaconda.org/package/{channel}/{name}",
        "missing": {},
    }
    try:
        info = conda.package(channel, name)
    except SOURCE_FAILURES as error:
        record["missing"] = {
            "downloads_total": missing_reason(error, absent="not_published")
        }
        record["error"] = str(error)
        return record
    record["downloads_total"] = info.get("downloads_cumulative")
    if record["downloads_total"] is None:
        record["missing"] = {"downloads_total": "not_published"}
    return record


def julia_package_record(name: str, julia: JuliaRegistryClient) -> dict[str, Any]:
    record: dict[str, Any] = {
        "name": name,
        "registered": None,
        "source_url": (
            "https://api.github.com/repos/JuliaRegistries/General/contents/"
            f"{name[0].upper()}/{name}/Package.toml"
        ),
        "missing": {},
    }
    try:
        julia.package(name)
    except NotFoundError:
        # Absence from the registry is the measurement, not a gap in it.
        record["registered"] = False
    except SOURCE_FAILURES as error:
        record["missing"] = {"registered": "fetch_error"}
        record["error"] = str(error)
    else:
        record["registered"] = True
    return record


def _total(
    items: list[dict[str, Any]], key: str, *fallbacks: str
) -> tuple[int | None, str | None]:
    """Sum one metric across every item, or say why there is no total.

    A total that leaves an item out is not the total, so one missing
    component makes the sum missing with that component's reason (looked up
    under ``key`` and then ``fallbacks``); the per-item values stay in the
    record as the floor.
    """
    if not items:
        return None, "not_applicable"
    for item in items:
        if item.get(key) is None:
            reasons = item.get("missing", {})
            names = (key, *fallbacks)
            return None, next(
                (reasons[n] for n in names if n in reasons), "unavailable"
            )
    return sum(item[key] for item in items), None


def _sum_or_none(values: Iterable[int | None]) -> int | None:
    """A total with an unknown term is unknown, not smaller."""
    total = 0
    for value in values:
        if value is None:
            return None
        total += value
    return total


def registry_record(
    project: ProjectRecord,
    pypi: PyPIClient,
    stats: PyPIStatsClient,
    conda: CondaClient,
    julia: JuliaRegistryClient,
    *,
    today: date | None = None,
) -> dict[str, Any]:
    """Measure every package a project declares on PyPI, conda, and Julia."""
    pypi_items = [
        pypi_package_record(name, pypi, stats, today=today)
        for name in project.registries.pypi
    ]
    conda_items = [conda_package_record(i, conda) for i in project.registries.conda]
    julia_items = [julia_package_record(n, julia) for n in project.registries.julia]
    missing: dict[str, str] = {}
    totals: dict[str, int | None] = {}
    for field, items, key in (
        ("pypi_downloads_30d", pypi_items, "downloads_30d"),
        ("pypi_downloads_180d", pypi_items, "downloads_180d"),
        ("conda_downloads_total", conda_items, "downloads_total"),
    ):
        value, reason = _total(items, key, "downloads", "metadata")
        totals[field] = value
        if reason:
            missing[field] = reason
    unread = [
        item
        for item in pypi_items
        if "metadata" in item["missing"] or "requires_dist" in item["missing"]
    ]
    dependencies: list[str] = []
    if not pypi_items:
        missing["dependencies"] = "not_applicable"
    elif unread:
        # One unread package would leave the list incomplete, not shorter.
        first = unread[0]["missing"]
        missing["dependencies"] = first.get("metadata") or first["requires_dist"]
    else:
        dependencies = dependency_names(
            req for item in pypi_items for req in item["requires_dist"]
        )
    return {
        "id": project.id,
        "pypi": pypi_items,
        "conda": conda_items,
        "julia": julia_items,
        **totals,
        "dependencies": dependencies,
        "missing": missing,
    }


# --- publications -------------------------------------------------------------


def publication_record(
    project: ProjectRecord, openalex: OpenAlexClient
) -> dict[str, Any]:
    """Look up every curated DOI on OpenAlex and total the citations.

    ``citations_total`` sums every DOI, and is missing when any DOI could not
    be read; ``canonical_citations`` is the canonical DOI's own count, or
    missing when the project names none or that DOI could not be read.
    """
    items: list[dict[str, Any]] = []
    for reference in project.publications:
        item: dict[str, Any] = {
            "doi": reference.doi,
            "role": reference.role,
            "title": None,
            "year": None,
            "work_type": None,
            "cited_by_count": None,
            "openalex_id": None,
            "source_url": f"https://api.openalex.org/works/https://doi.org/{reference.doi}",
            "missing": {},
        }
        try:
            work = openalex.work_by_doi(reference.doi)
        except SOURCE_FAILURES as error:
            item["missing"] = {"work": missing_reason(error, absent="unavailable")}
            item["error"] = str(error)
        else:
            item.update(
                title=work.get("title"),
                year=work.get("publication_year"),
                work_type=work.get("work_type"),
                cited_by_count=work.get("cited_by_count"),
                openalex_id=work.get("openalex_id"),
            )
            _note_unpublished(
                item, ("title", "year", "work_type", "cited_by_count", "openalex_id")
            )
        items.append(item)
    missing: dict[str, str] = {}
    if not items:
        missing["publications"] = "not_applicable"
    total, reason = _total(items, "cited_by_count", "work")
    if reason and items:
        missing["citations_total"] = reason
    canonical = next((i for i in items if i["role"] == "canonical"), None)
    canonical_count = canonical["cited_by_count"] if canonical else None
    if canonical is None:
        missing["canonical_citations"] = "not_applicable"
    elif canonical_count is None:
        missing["canonical_citations"] = canonical["missing"].get("work") or canonical[
            "missing"
        ].get("cited_by_count")
    return {
        "id": project.id,
        "publications": items,
        "citations_total": total,
        "canonical_citations": canonical_count,
        "missing": missing,
    }


def language_totals(records: Iterable[dict[str, Any]]) -> Counter[str]:
    """Lines per language across git records, for a run summary."""
    totals: Counter[str] = Counter()
    for record in records:
        totals.update(record.get("lines_by_language") or {})
    return totals
