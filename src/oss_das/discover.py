"""Turn forge searches and registry sweeps into write-once candidate files.

A candidate file is the record that something was found, where, and by which
probe; it is written once and never updated, so the first sighting is what
git history shows. Everything that decides whether the finding matters lives
downstream in triage and review. The coverage ledger is the other half of the
story: a probe that returned nothing, or that could not run, is recorded
there so "we found nothing" stays distinguishable from "we did not look".
"""

from __future__ import annotations

import re
import tomllib
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from oss_das.clients.base import NotFoundError, SourceError
from oss_das.clients.forge import ForgeClient
from oss_das.collection import (
    BROAD_QUERIES,
    FORGE_HOSTS,
    GITHUB_DISCOVERY_QUERIES,
    PATH_SEARCH_QUERIES,
)
from oss_das.core import (
    PATHS,
    append_csv,
    candidate_key,
    candidate_path,
    read_record,
    write_record,
)
from oss_das.models import ForgeKind, ProjectRecord
from oss_das.utils import normalize_name

COVERAGE_FIELDS = [
    "fetched_at",
    "host",
    "kind",
    "probe",
    "query",
    "status",
    "reported_total",
    "retrieved",
    "truncated",
    "error",
]

#: How much README or long description a candidate file carries.
BODY_LIMIT = 6000

#: Name fragments worth a registry lookup. Substring matching is deliberate:
#: the packages this census exists for are called dascore, xdas, daspy and
#: dastools, none of which a word-boundary match would find.
NAME_TOKENS = ("das", "otdr", "dfos", "fiber", "fibre", "dts", "dss", "interrogator")

#: Words that contain "das" and never mean distributed acoustic sensing. They
#: are removed before the substring test so that "pandas-dashboard" is not a
#: name match while "dascore" still is; the description test below catches
#: anything this list is too eager about.
NAME_STOPWORDS = re.compile(
    r"pandas|dash|dask|midas|lambdas|adas|badass|dasein|dasilva|agendas"
    r"|idasen|cadasta|candas|fandas|tidas|mudassir|mudassar|dassault"
)

#: Prose vocabulary that says fiber sensing rather than an acronym collision.
DOMAIN_PHRASE = re.compile(
    r"distributed (acoustic|vibration|strain|temperature|fib(er|re)[ -]?optic)"
    r"|fib(er|re)[ -]?optic|\botdr\b|\bdfos\b|interrogator|phi-?otdr|φ-otdr",
    re.I,
)

#: Any of the name tokens, as a word, in prose.
TEXT_TOKEN = re.compile(r"\b(das|otdr|dfos|dts|dss|interrogator)\b|fib(er|re)", re.I)

#: Hosts whose ``/owner/name`` URLs are repositories, beyond the swept forges.
REPOSITORY_HOSTS = frozenset(
    {"github.com", "gitlab.com", "codeberg.org", "bitbucket.org"}
    | {host for _, host in FORGE_HOSTS}
)

#: Registry sweeps are recorded against these hosts and probe names.
REGISTRY_PROBES = {
    "pypi": ("pypi.org", "pypi:simple-index-sweep"),
    "conda": ("conda.anaconda.org", "conda-forge:index-sweep"),
    "julia": ("raw.githubusercontent.com", "julia-general:index-sweep"),
}


# --- matching -----------------------------------------------------------------


def name_matches(name: str) -> bool:
    """Whether a package name carries one of the sweep tokens."""
    lowered = NAME_STOPWORDS.sub("", name.lower())
    return any(token in lowered for token in NAME_TOKENS)


def text_matches(text: str | None) -> bool:
    """Whether prose mentions the domain, or at least one token as a word."""
    return bool(text) and bool(TEXT_TOKEN.search(text) or DOMAIN_PHRASE.search(text))


def text_probe_class(text: str | None) -> str:
    """Domain vocabulary in prose is specific; a bare acronym is not."""
    return "domain-specific" if text and DOMAIN_PHRASE.search(text) else "broad-acronym"


#: Path segments after which a forge URL stops naming the repository.
_PAGE_MARKERS = frozenset(
    {
        "-",
        "blob",
        "tree",
        "issues",
        "pull",
        "pulls",
        "wiki",
        "releases",
        "src",
        "commits",
        "archive",
    }
)

_GITLAB_HOSTS = frozenset(
    host for kind, host in FORGE_HOSTS if kind == ForgeKind.GITLAB
)


def repository_url_from(urls: Iterable[str | None]) -> str | None:
    """The first URL that names a repository on a known forge, normalized.

    GitLab nests groups, so ``gitlab.com/group/subgroup/project`` keeps every
    segment up to a page marker; GitHub and Gitea paths are owner/name only.
    """
    for url in urls:
        if not url:
            continue
        parsed = urlparse(url.strip())
        host = parsed.netloc.lower()
        if parsed.scheme not in {"http", "https"} or not host:
            continue
        known = host in REPOSITORY_HOSTS or "gitlab" in host or "gitea" in host
        segments = [part for part in parsed.path.split("/") if part]
        if (
            not known
            or len(segments) < 2
            or segments[0] in {"sponsors", "orgs", "topics", "search"}
        ):
            continue
        nested = "gitlab" in host or host in _GITLAB_HOSTS
        kept: list[str] = []
        for segment in segments:
            if segment in _PAGE_MARKERS or (not nested and len(kept) == 2):
                break
            kept.append(segment)
        if len(kept) < 2:
            continue
        kept[-1] = kept[-1].removesuffix(".git")
        return f"https://{host}/{'/'.join(kept)}"
    return None


# --- candidate files ----------------------------------------------------------


@dataclass
class CandidateStore:
    """Write-once access to ``data/raw/candidates``.

    A key that already has a file, or that sits in the rejection ledger, is
    never written again; the store reports which so the caller can count.
    """

    root: Path = field(default_factory=lambda: PATHS.candidates)
    rejected: frozenset[str] = frozenset()

    def path(self, key: str) -> Path:
        return candidate_path(key, self.root)

    def exists(self, key: str) -> bool:
        return self.path(key).exists()

    def keys(self) -> set[str]:
        return {read_record(path)[0]["key"] for path in self.root.glob("*/*.md")}

    def read(self, key: str) -> tuple[dict[str, Any], str]:
        return read_record(self.path(key))

    def write(
        self, front: dict[str, Any], body: str = "", *, force: bool = False
    ) -> bool:
        key = front["key"]
        if key in self.rejected:
            return False
        if self.exists(key):
            existing = read_record(self.path(key))[0].get("key")
            if existing != key:
                raise ValueError(
                    f"{self.path(key)} holds {existing!r}, not {key!r}: "
                    "two candidate keys fold to the same filename"
                )
            if not force:
                return False
        write_record(self.path(key), front, body[:BODY_LIMIT])
        return True


def forge_candidate(
    hit: dict[str, Any],
    *,
    probes: Iterable[str],
    found_by: Iterable[str],
    first_seen: str,
) -> dict[str, Any]:
    """The frontmatter of a forge candidate, from a normalized search hit."""
    probes = sorted(set(probes))
    specific = any(
        ":owner:" not in probe and probe.split(":", 1)[1] not in BROAD_QUERIES
        for probe in probes
    )
    return {
        "key": candidate_key(hit["forge_host"], hit["repository"]),
        "source": "forge",
        "forge_kind": hit["forge_kind"],
        "forge_host": hit["forge_host"],
        "repository": hit["repository"],
        "name": hit["name"],
        "description": hit.get("description"),
        "html_url": hit["html_url"],
        "language": hit.get("language"),
        "stars_at_discovery": hit.get("stars_at_discovery"),
        "probes": probes,
        "probe_class": "domain-specific" if specific else "broad-acronym",
        "found_by": sorted(set(found_by)),
        "first_seen": first_seen,
    }


def _registry_candidate(
    source: str,
    package: str,
    *,
    name: str,
    description: str | None,
    registry_url: str,
    version: str | None,
    last_release: str | None,
    repository_url: str | None,
    license_stated: str | None,
    author: str | None,
    probe_text: str,
    first_seen: str,
) -> dict[str, Any]:
    return {
        "key": candidate_key(source, package),
        "source": source,
        "name": name,
        "package": package,
        "description": description or None,
        "registry_url": registry_url,
        "version": version,
        "last_release": last_release,
        "repository_url": repository_url,
        "repository_declared_in_metadata": repository_url is not None,
        "license_stated": license_stated or None,
        "author": author or None,
        "probes": [REGISTRY_PROBES[source][1]],
        "probe_class": text_probe_class(probe_text),
        "found_by": ["search"],
        "first_seen": first_seen,
    }


def pypi_candidate(
    payload: dict[str, Any], *, first_seen: str
) -> tuple[dict[str, Any], str] | None:
    """A candidate from the PyPI JSON API, or None when the prose never mentions the domain."""
    info = payload.get("info") or {}
    summary = info.get("summary") or ""
    description = info.get("description") or ""
    text = f"{summary}\n{description}"
    if not text_matches(text):
        return None
    uploads = [
        file.get("upload_time_iso_8601", "")
        for files in (payload.get("releases") or {}).values()
        for file in files
    ]
    urls = list((info.get("project_urls") or {}).values())
    urls += [info.get("home_page"), info.get("download_url")]
    package = normalize_name(info["name"])
    front = _registry_candidate(
        "pypi",
        package,
        name=info["name"],
        description=summary,
        registry_url=f"https://pypi.org/project/{package}/",
        version=info.get("version"),
        last_release=max(uploads, default="")[:10] or None,
        repository_url=repository_url_from(urls),
        license_stated=info.get("license_expression") or info.get("license"),
        author=info.get("author") or info.get("author_email"),
        probe_text=text,
        first_seen=first_seen,
    )
    return front, description or summary


def conda_candidate(
    name: str, entry: dict[str, Any], *, first_seen: str
) -> tuple[dict[str, Any], str] | None:
    summary = entry.get("summary") or ""
    description = entry.get("description") or ""
    text = f"{summary}\n{description}"
    if not text_matches(text):
        return None
    stamp = entry.get("timestamp")
    last_release = None
    if isinstance(stamp, int | float) and stamp > 0:
        last_release = datetime.fromtimestamp(stamp, UTC).date().isoformat()
    urls = [entry.get("dev_url"), entry.get("source_url"), entry.get("home")]
    front = _registry_candidate(
        "conda",
        name.lower(),
        name=name,
        description=summary,
        registry_url=f"https://anaconda.org/conda-forge/{name}",
        version=entry.get("version"),
        last_release=last_release,
        repository_url=repository_url_from(urls),
        license_stated=entry.get("license"),
        author=None,
        probe_text=text,
        first_seen=first_seen,
    )
    return front, description or summary


def julia_candidate(
    name: str, path: str, package_toml: str, *, first_seen: str
) -> tuple[dict[str, Any], str]:
    """A Julia candidate; the registry has no prose, so the name is the evidence.

    With no description to test, a name match is left ``domain-specific`` so
    triage shows it to the model instead of dropping it as a bare acronym;
    the General registry yields a few dozen such names, which is cheap.
    """
    repo = tomllib.loads(package_toml).get("repo")
    front = _registry_candidate(
        "julia",
        name,
        name=name,
        description=None,
        registry_url=f"https://github.com/JuliaRegistries/General/tree/master/{path}",
        version=None,
        last_release=None,
        repository_url=repository_url_from([repo]),
        license_stated=None,
        author=None,
        probe_text=name,
        first_seen=first_seen,
    )
    front["probe_class"] = "domain-specific"
    return front, ""


def julia_registry_names(registry_toml: str) -> dict[str, str]:
    """``name -> path`` for every package in ``Registry.toml``."""
    packages = tomllib.loads(registry_toml).get("packages", {})
    return {entry["name"]: entry["path"] for entry in packages.values()}


# --- forges -------------------------------------------------------------------

CoverageSink = Callable[[dict[str, Any]], None]


def namespaces_of(curated: Iterable[ProjectRecord]) -> list[tuple[ForgeKind, str, str]]:
    """The (kind, host, owner) triples worth walking; registry-only projects have none."""
    found = {
        (project.forge.kind, project.forge.host, project.owner)
        for project in curated
        if project.repository is not None
    }
    return sorted(found, key=lambda item: (item[1], item[2]))


def search_forges(
    forges: Iterable[ForgeClient],
    curated: Iterable[ProjectRecord],
    *,
    fetched_at: str,
    coverage: CoverageSink,
    unavailable: dict[str, str] | None = None,
) -> dict[str, dict[str, Any]]:
    """Run every probe and merge hits by key, keeping which probes found each.

    ``unavailable`` names hosts that have no client this run and why, so their
    probes are recorded as skipped instead of silently not happening.
    """
    by_host = {forge.host: forge for forge in forges}
    unavailable = dict(unavailable or {})
    hits: dict[str, dict[str, Any]] = {}

    def record(key: str, hit: dict[str, Any], probe: str, found_by: str) -> None:
        entry = hits.setdefault(key, {**hit, "probes": set(), "found_by": set()})
        entry["probes"].add(probe)
        entry["found_by"].add(found_by)

    planned: list[tuple[ForgeKind, str, str, str]] = []
    for forge in forges:
        queries = (
            GITHUB_DISCOVERY_QUERIES
            if forge.kind == ForgeKind.GITHUB
            else PATH_SEARCH_QUERIES
        )
        planned.extend((forge.kind, forge.host, "search", query) for query in queries)
    if "github.com" in unavailable and "github.com" not in by_host:
        planned.extend(
            (ForgeKind.GITHUB, "github.com", "search", q)
            for q in GITHUB_DISCOVERY_QUERIES
        )
    planned.extend(
        (kind, host, "namespace", owner) for kind, host, owner in namespaces_of(curated)
    )

    for kind, host, probe, query in planned:
        row: dict[str, Any] = {
            "fetched_at": fetched_at,
            "host": host,
            "kind": kind.value,
            "probe": probe,
            "query": query,
        }
        forge = by_host.get(host)
        if forge is None:
            error = unavailable.get(host, f"no client for {host}")
            coverage(row | {"status": "skipped", "error": error})
            continue
        try:
            if probe == "search":
                result = forge.search_repositories(query)
                found, total, truncated = (
                    result.hits,
                    result.reported_total,
                    result.truncated,
                )
                label = f"{host}:{query}"
            else:
                found = forge.list_namespace_repositories(query)
                total, truncated = len(found), False
                label = f"{host}:owner:{query}"
        except (SourceError, KeyError, TypeError) as error:
            coverage(row | {"status": "failed", "error": str(error)})
            continue
        for hit in found:
            record(
                candidate_key(hit["forge_host"], hit["repository"]), hit, label, probe
            )
        coverage(
            row
            | {
                "status": "ok",
                "reported_total": total,
                "retrieved": len(found),
                "truncated": truncated,
            }
        )
    return hits


def write_forge_candidates(
    hits: dict[str, dict[str, Any]],
    *,
    store: CandidateStore,
    forges: Iterable[ForgeClient],
    first_seen: str,
) -> list[str]:
    """Write every new hit with its README; return the keys written."""
    by_host = {forge.host: forge for forge in forges}
    written = []
    for key in sorted(hits):
        hit = hits[key]
        if key in store.rejected or store.exists(key):
            continue
        front = forge_candidate(
            hit, probes=hit["probes"], found_by=hit["found_by"], first_seen=first_seen
        )
        body = fetch_readme(by_host.get(hit["forge_host"]), hit["repository"])
        if store.write(front, body):
            written.append(key)
    return written


def fetch_readme(forge: ForgeClient | None, repository: str) -> str:
    """A README when the host serves one cheaply; empty on any failure."""
    if forge is None:
        return ""
    try:
        return forge.readme(repository)
    except (SourceError, KeyError, TypeError, ValueError):
        return ""


def refresh_candidate(
    key: str, *, store: CandidateStore, forges: Iterable[ForgeClient]
) -> bool:
    """Rewrite one forge candidate from the host, keeping its discovery record."""
    front, _ = store.read(key)
    forge = next((f for f in forges if f.host == front["forge_host"]), None)
    if forge is None:
        raise SourceError(f"no client for {front['forge_host']}")
    hit = forge.repository(front["repository"])
    fresh = forge_candidate(
        hit,
        probes=front["probes"],
        found_by=front["found_by"],
        first_seen=front["first_seen"],
    )
    # The first sighting is what the file records; only the description,
    # language, URL and README are worth refreshing.
    fresh["stars_at_discovery"] = front.get("stars_at_discovery")
    return store.write(fresh, fetch_readme(forge, hit["repository"]), force=True)


# --- registries ---------------------------------------------------------------


def sweep_registry(
    source: str,
    names: Iterable[str],
    build: Callable[[str], tuple[dict[str, Any], str] | None],
    *,
    store: CandidateStore,
    fetched_at: str,
    coverage: CoverageSink,
    on_error: Callable[[str, Exception], None] | None = None,
) -> list[str]:
    """Filter an index by name, build candidates for the matches, write the new ones.

    ``build`` fetches whatever metadata the registry keeps per package and
    returns a candidate, or None when the prose never mentions the domain.
    One coverage row records the sweep: index size as the reported total and
    the number of matches as retrieved.
    """
    host, probe = REGISTRY_PROBES[source]
    names = list(names)
    matched = [name for name in names if name_matches(name)]
    written: list[str] = []
    hits = 0
    failed = 0
    for name in matched:
        try:
            built = build(name)
        except NotFoundError:
            # The simple index keeps names whose releases were deleted; a
            # 404 on the metadata is routine there, not a failure to report.
            continue
        except (SourceError, KeyError, TypeError, ValueError) as error:
            failed += 1
            if on_error:
                on_error(name, error)
            continue
        if built is None:
            continue
        hits += 1
        front, body = built
        if store.write(front, body):
            written.append(front["key"])
    coverage(
        {
            "fetched_at": fetched_at,
            "host": host,
            "kind": "registry",
            "probe": probe,
            "query": " ".join(NAME_TOKENS),
            "status": "ok",
            "reported_total": len(names),
            "retrieved": hits,
            "truncated": False,
            "error": f"{failed} of {len(matched)} metadata lookups failed"
            if failed
            else "",
        }
    )
    return written


def registry_failure_row(
    source: str, error: Exception, *, fetched_at: str
) -> dict[str, Any]:
    """The coverage row for a registry whose index could not be read at all."""
    host, probe = REGISTRY_PROBES[source]
    return {
        "fetched_at": fetched_at,
        "host": host,
        "kind": "registry",
        "probe": probe,
        "query": " ".join(NAME_TOKENS),
        "status": "failed",
        "error": str(error),
    }


def append_coverage(row: dict[str, Any], path: Path | None = None) -> None:
    append_csv(path or PATHS.coverage, [row], COVERAGE_FIELDS)
