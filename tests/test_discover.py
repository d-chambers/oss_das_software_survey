from __future__ import annotations

import pytest

from oss_das.clients.base import NotFoundError, SourceError
from oss_das.clients.forge import SearchResult
from oss_das.collection import GITHUB_DISCOVERY_QUERIES, PATH_SEARCH_QUERIES
from oss_das.core import read_record
from oss_das.discover import (
    CandidateStore,
    conda_candidate,
    forge_candidate,
    julia_candidate,
    julia_registry_names,
    name_matches,
    namespaces_of,
    pypi_candidate,
    refresh_candidate,
    registry_failure_row,
    repository_url_from,
    search_forges,
    sweep_registry,
    text_matches,
    write_forge_candidates,
)
from oss_das.models import ForgeKind, ProjectRecord

PROJECT = ProjectRecord.model_validate(
    {
        "id": "example",
        "name": "Example",
        "repository": "owner/example",
        "description": "Example DAS package.",
        "status": "included",
        "decision_reason": "Meets the policy.",
        "primary_category": "processing",
    }
)

REGISTRY_ONLY = ProjectRecord.model_validate(
    {
        "id": "pkg",
        "name": "Pkg",
        "description": "Registry-only DAS package.",
        "status": "included",
        "decision_reason": "Meets the policy.",
        "primary_category": "processing",
        "registries": {"pypi": ["pkg"]},
    }
)


class FakeForge:
    """Fixed answers, so the discovery logic is what gets tested."""

    def __init__(
        self, kind, host, results=None, total=None, namespaces=None, readmes=None
    ):
        self.kind = kind
        self.host = host
        self._results = results or {}
        self._total = total
        self._namespaces = namespaces or {}
        self._readmes = readmes or {}
        self.readme_calls: list[str] = []

    def search_repositories(self, query):
        hits = self._results.get(query)
        if hits is None:
            raise SourceError(f"{self.host} refused {query}")
        truncated = None if self._total is None else self._total > len(hits)
        return SearchResult(list(hits), self._total, truncated)

    def list_namespace_repositories(self, namespace):
        return list(self._namespaces.get(namespace, []))

    def readme(self, repository):
        self.readme_calls.append(repository)
        if repository not in self._readmes:
            raise NotFoundError(repository)
        return self._readmes[repository]

    def repository(self, repository):
        return _hit(self.host, repository, self.kind, description="refreshed", stars=9)


def _hit(host, repository, kind=ForgeKind.GITHUB, description=None, stars=3):
    return {
        "forge_kind": kind.value,
        "forge_host": host,
        "repository": repository,
        "name": repository.split("/")[-1],
        "description": description,
        "html_url": f"https://{host}/{repository}",
        "stars_at_discovery": stars,
        "language": "Python",
    }


def _answers(queries, hits):
    return {query: list(hits) for query in queries}


def _run(forges, curated=(), unavailable=None):
    rows = []
    hits = search_forges(
        forges,
        curated,
        fetched_at="2026-08-28T00:00:00+00:00",
        coverage=rows.append,
        unavailable=unavailable,
    )
    return hits, rows


# --- search -------------------------------------------------------------------


def test_every_probe_appends_one_coverage_row_even_when_empty() -> None:
    forge = FakeForge(
        ForgeKind.GITLAB, "git.example.org", results=_answers(PATH_SEARCH_QUERIES, [])
    )
    hits, rows = _run([forge], [])
    assert hits == {}
    assert len(rows) == len(PATH_SEARCH_QUERIES)
    assert {row["status"] for row in rows} == {"ok"}
    assert {row["retrieved"] for row in rows} == {0}


def test_github_probes_are_recorded_as_skipped_without_a_token() -> None:
    _, rows = _run([], [PROJECT], unavailable={"github.com": "no GITHUB_TOKEN"})
    searches = [row for row in rows if row["probe"] == "search"]
    assert len(searches) == len(GITHUB_DISCOVERY_QUERIES)
    assert {row["status"] for row in rows} == {"skipped"}
    assert {row["error"] for row in rows} == {"no GITHUB_TOKEN"}
    namespace = next(row for row in rows if row["probe"] == "namespace")
    assert namespace["query"] == "owner"


def test_probes_merge_by_key_and_keep_every_probe_that_found_a_hit() -> None:
    hit = _hit("github.com", "Org/Tool")
    forge = FakeForge(
        ForgeKind.GITHUB,
        "github.com",
        results=_answers(GITHUB_DISCOVERY_QUERIES, [hit]),
        total=1,
        namespaces={"owner": [hit]},
    )
    hits, rows = _run([forge], [PROJECT])
    assert list(hits) == ["github.com/org/tool"]
    assert (
        len(hits["github.com/org/tool"]["probes"]) == len(GITHUB_DISCOVERY_QUERIES) + 1
    )
    assert hits["github.com/org/tool"]["found_by"] == {"search", "namespace"}
    assert rows[-1] == {
        "fetched_at": "2026-08-28T00:00:00+00:00",
        "host": "github.com",
        "kind": "github",
        "probe": "namespace",
        "query": "owner",
        "status": "ok",
        "reported_total": 1,
        "retrieved": 1,
        "truncated": False,
    }


def test_a_refused_query_is_a_failed_row_not_a_missing_one() -> None:
    answers = _answers(PATH_SEARCH_QUERIES, [])
    answers.pop("das")
    forge = FakeForge(ForgeKind.GITEA, "codeberg.org", results=answers)
    _, rows = _run([forge], [])
    failed = [row for row in rows if row["status"] == "failed"]
    assert [row["query"] for row in failed] == ["das"]
    assert "refused" in failed[0]["error"]


def test_truncation_is_reported_from_the_host_total() -> None:
    forge = FakeForge(
        ForgeKind.GITHUB,
        "github.com",
        results=_answers(GITHUB_DISCOVERY_QUERIES, [_hit("github.com", "a/b")]),
        total=2366,
    )
    _, rows = _run([forge], [])
    assert all(row["truncated"] for row in rows)
    assert {row["reported_total"] for row in rows} == {2366}


def test_namespace_walk_skips_registry_only_projects() -> None:
    assert namespaces_of([PROJECT, REGISTRY_ONLY]) == [
        (ForgeKind.GITHUB, "github.com", "owner")
    ]


def test_same_path_on_two_hosts_stays_apart() -> None:
    forges = [
        FakeForge(
            ForgeKind.GITHUB,
            "github.com",
            results=_answers(
                GITHUB_DISCOVERY_QUERIES, [_hit("github.com", "org/tool")]
            ),
            total=1,
        ),
        FakeForge(
            ForgeKind.GITLAB,
            "git.example.org",
            results=_answers(
                PATH_SEARCH_QUERIES,
                [_hit("git.example.org", "org/tool", ForgeKind.GITLAB)],
            ),
        ),
    ]
    hits, _ = _run(forges, [])
    assert sorted(hits) == ["git.example.org/org/tool", "github.com/org/tool"]


# --- candidate files ----------------------------------------------------------


def test_forge_candidate_found_only_by_an_acronym_probe_is_broad() -> None:
    front = forge_candidate(
        _hit("h", "u/dashboard"),
        probes=["h:das", "h:owner:u"],
        found_by=["search"],
        first_seen="2026-08-28",
    )
    assert front["probe_class"] == "broad-acronym"
    specific = forge_candidate(
        _hit("h", "u/x"),
        probes=["h:das", "h:distributed acoustic sensing"],
        found_by=["search"],
        first_seen="d",
    )
    assert specific["probe_class"] == "domain-specific"


def test_candidates_are_written_once_with_the_readme_as_body(tmp_path) -> None:
    hit = _hit("github.com", "Org/Tool", description="DAS reader")
    forge = FakeForge(
        ForgeKind.GITHUB,
        "github.com",
        results=_answers(GITHUB_DISCOVERY_QUERIES, [hit]),
        total=1,
        readmes={"Org/Tool": "# Tool\n\nReads DAS files."},
    )
    store = CandidateStore(root=tmp_path)
    hits, _ = _run([forge], [])
    assert write_forge_candidates(
        hits, store=store, forges=[forge], first_seen="2026-08-28"
    ) == ["github.com/org/tool"]
    path = tmp_path / "github.com" / "org--tool.md"
    front, body = read_record(path)
    assert front["key"] == "github.com/org/tool"
    assert front["source"] == "forge"
    assert front["repository"] == "Org/Tool"
    assert front["first_seen"] == "2026-08-28"
    assert front["found_by"] == ["search"]
    assert body == "# Tool\n\nReads DAS files."

    before = path.read_text()
    hits["github.com/org/tool"]["description"] = "changed upstream"
    assert (
        write_forge_candidates(
            hits, store=store, forges=[forge], first_seen="2026-09-01"
        )
        == []
    )
    assert path.read_text() == before
    assert forge.readme_calls == ["Org/Tool"], (
        "no README fetch for a key already on disk"
    )


def test_rejected_keys_are_never_written(tmp_path) -> None:
    hit = _hit("codeberg.org", "theseus/das", ForgeKind.GITEA)
    forge = FakeForge(
        ForgeKind.GITEA, "codeberg.org", results=_answers(PATH_SEARCH_QUERIES, [hit])
    )
    store = CandidateStore(
        root=tmp_path, rejected=frozenset({"codeberg.org/theseus/das"})
    )
    hits, _ = _run([forge], [])
    assert (
        write_forge_candidates(hits, store=store, forges=[forge], first_seen="d") == []
    )
    assert not list(tmp_path.rglob("*.md"))


def test_readme_failure_leaves_an_empty_body(tmp_path) -> None:
    hit = _hit("gitlab.com", "g/p", ForgeKind.GITLAB)
    forge = FakeForge(
        ForgeKind.GITLAB, "gitlab.com", results=_answers(PATH_SEARCH_QUERIES, [hit])
    )
    store = CandidateStore(root=tmp_path)
    hits, _ = _run([forge], [])
    write_forge_candidates(hits, store=store, forges=[forge], first_seen="d")
    _, body = read_record(tmp_path / "gitlab.com" / "g--p.md")
    assert body == ""


def test_refresh_rewrites_metadata_but_keeps_the_discovery_record(tmp_path) -> None:
    hit = _hit("github.com", "org/tool")
    forge = FakeForge(
        ForgeKind.GITHUB, "github.com", readmes={"org/tool": "fresh readme"}
    )
    store = CandidateStore(root=tmp_path)
    store.write(
        forge_candidate(
            hit,
            probes=["github.com:topic:dfos"],
            found_by=["search"],
            first_seen="2026-01-01",
        )
    )
    assert refresh_candidate("github.com/org/tool", store=store, forges=[forge])
    front, body = read_record(store.path("github.com/org/tool"))
    assert front["description"] == "refreshed"
    assert front["stars_at_discovery"] == 3, "the first sighting is kept"
    assert front["probes"] == ["github.com:topic:dfos"]
    assert front["first_seen"] == "2026-01-01"
    assert body == "fresh readme"


# --- registries ---------------------------------------------------------------


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("dascore", True),
        ("xdas", True),
        ("DASPy-toolbox", True),
        ("otdr-reader", True),
        ("pyfibre", True),
        ("dtscalibration", True),
        ("dashboard", False),
        ("dash-bootstrap-components", False),
        ("pandas-dashboard", False),
        ("geopandas", False),
        ("dask-ml", False),
        ("requests", False),
    ],
)
def test_name_token_filter(name, expected) -> None:
    assert name_matches(name) is expected


def test_text_token_filter_needs_a_whole_word() -> None:
    assert text_matches("Tools for DAS data")
    assert text_matches("A fibre-optic strain reader")
    assert not text_matches("A dashboard for DTSchema")
    assert not text_matches("")
    assert not text_matches(None)


def test_repository_url_is_taken_from_the_first_forge_link() -> None:
    urls = [
        "https://readthedocs.org/x",
        "https://github.com/Org/Tool.git/",
        "https://gitlab.com/a/b",
    ]
    assert repository_url_from(urls) == "https://github.com/Org/Tool"
    assert repository_url_from(["https://github.com/sponsors/someone"]) is None
    assert (
        repository_url_from(["https://git.gfz-potsdam.de/geofon/dastools"])
        == "https://git.gfz-potsdam.de/geofon/dastools"
    )
    assert repository_url_from([None, ""]) is None
    nested = "https://gitlab.com/group/subgroup/project/-/tree/main"
    assert repository_url_from([nested]) == "https://gitlab.com/group/subgroup/project"
    assert (
        repository_url_from(["https://github.com/org/tool/tree/main/docs"])
        == "https://github.com/org/tool"
    )
    assert repository_url_from(["git@github.com:org/tool.git"]) is None


def _pypi_payload(
    name="DASPAL", summary="DAS processing library", description="", urls=None
):
    return {
        "info": {
            "name": name,
            "version": "1.0",
            "summary": summary,
            "description": description,
            "project_urls": urls or {},
            "home_page": None,
            "license": "MIT",
            "author": "Someone",
        },
        "releases": {"1.0": [{"upload_time_iso_8601": "2026-08-03T10:00:00Z"}]},
    }


def test_pypi_candidate_carries_the_declared_repository_and_long_description() -> None:
    payload = _pypi_payload(
        description="Long text about distributed acoustic sensing.",
        urls={"Source": "https://github.com/org/daspal"},
    )
    front, body = pypi_candidate(payload, first_seen="2026-08-28")
    assert front["key"] == "pypi/daspal"
    assert front["source"] == "pypi"
    assert front["package"] == "daspal"
    assert front["name"] == "DASPAL"
    assert front["repository_url"] == "https://github.com/org/daspal"
    assert front["repository_declared_in_metadata"] is True
    assert front["probe_class"] == "domain-specific"
    assert front["last_release"] == "2026-08-03"
    assert front["license_stated"] == "MIT"
    assert front["probes"] == ["pypi:simple-index-sweep"]
    assert body.startswith("Long text")


def test_pypi_candidate_without_domain_prose_is_dropped() -> None:
    assert (
        pypi_candidate(
            _pypi_payload(summary="A dashboard.", description="Nothing here."),
            first_seen="d",
        )
        is None
    )
    front, _ = pypi_candidate(_pypi_payload(summary="DAS helper"), first_seen="d")
    assert front["probe_class"] == "broad-acronym"
    assert front["repository_url"] is None
    assert front["repository_declared_in_metadata"] is False


def test_conda_candidate_reads_channeldata_fields() -> None:
    entry = {
        "summary": "Fiber optic DTS calibration",
        "description": None,
        "dev_url": "https://github.com/dtscalibration/python-dts-calibration",
        "license": "BSD-3-Clause",
        "version": "3.0",
        "timestamp": 1_700_000_000,
    }
    front, body = conda_candidate("dtscalibration", entry, first_seen="d")
    assert front["key"] == "conda/dtscalibration"
    assert front["registry_url"] == "https://anaconda.org/conda-forge/dtscalibration"
    assert front["repository_url"].endswith("python-dts-calibration")
    assert front["last_release"] == "2023-11-14"
    assert body == "Fiber optic DTS calibration"
    assert conda_candidate("dash", {"summary": "web apps"}, first_seen="d") is None


def test_julia_candidate_reads_the_registry_toml_files() -> None:
    registry = 'name = "General"\n\n[packages]\nabc = { name = "Dascore", path = "D/Dascore" }\n'
    assert julia_registry_names(registry) == {"Dascore": "D/Dascore"}
    front, body = julia_candidate(
        "Dascore",
        "D/Dascore",
        'name = "Dascore"\nrepo = "https://github.com/org/Dascore.jl.git"\n',
        first_seen="d",
    )
    assert front["key"] == "julia/dascore"
    assert front["repository_url"] == "https://github.com/org/Dascore.jl"
    assert front["registry_url"].endswith("/tree/master/D/Dascore")
    assert front["probe_class"] == "domain-specific", "name is the only evidence"
    assert body == ""


def test_registry_sweep_filters_by_name_then_prose_and_records_coverage(
    tmp_path,
) -> None:
    index = ["dascore", "dashboard", "requests", "fiberis", "pypi-rejected-das"]
    payloads = {
        "dascore": _pypi_payload("dascore", "DAS library"),
        "fiberis": _pypi_payload("fiberis", "Nothing about the domain"),
        "pypi-rejected-das": _pypi_payload("pypi-rejected-das", "DAS thing"),
    }
    asked: list[str] = []

    def build(name):
        asked.append(name)
        return pypi_candidate(payloads[name], first_seen="d")

    store = CandidateStore(
        root=tmp_path, rejected=frozenset({"pypi/pypi-rejected-das"})
    )
    rows = []
    written = sweep_registry(
        "pypi", index, build, store=store, fetched_at="t", coverage=rows.append
    )
    assert asked == ["dascore", "fiberis", "pypi-rejected-das"]
    assert written == ["pypi/dascore"]
    assert rows == [
        {
            "fetched_at": "t",
            "host": "pypi.org",
            "kind": "registry",
            "probe": "pypi:simple-index-sweep",
            "query": "das otdr dfos fiber fibre dts dss interrogator",
            "status": "ok",
            "reported_total": 5,
            "retrieved": 2,
            "truncated": False,
            "error": "",
        }
    ]
    assert (
        sweep_registry(
            "pypi", index, build, store=store, fetched_at="t", coverage=rows.append
        )
        == []
    )


def test_registry_sweep_reports_a_failed_lookup_and_continues(tmp_path) -> None:
    failures = []

    def build(name):
        if name == "das-broken":
            raise SourceError("boom")
        if name == "das-deleted":
            raise NotFoundError("gone")
        return pypi_candidate(_pypi_payload(name, "DAS"), first_seen="d")

    rows = []
    written = sweep_registry(
        "pypi",
        ["das-broken", "das-deleted", "das-ok"],
        build,
        store=CandidateStore(root=tmp_path),
        fetched_at="t",
        coverage=rows.append,
        on_error=lambda name, error: failures.append(name),
    )
    assert failures == ["das-broken"], "a deleted release is routine, not a failure"
    assert written == ["pypi/das-ok"]
    assert rows[0]["status"] == "ok"
    assert rows[0]["error"] == "1 of 3 metadata lookups failed"

    failure = registry_failure_row("conda", SourceError("index down"), fetched_at="t")
    assert failure["status"] == "failed"
    assert failure["host"] == "conda.anaconda.org"
    assert failure["error"] == "index down"
