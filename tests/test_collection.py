from __future__ import annotations

import httpx

from oss_das.clients.base import NotFoundError, SourceError
from oss_das.clients.forge import SearchResult
from oss_das.clients.packages import CondaClient, PyPIClient, PyPIStatsClient
from oss_das.collection import (
    GITHUB_DISCOVERY_QUERIES,
    PATH_SEARCH_QUERIES,
    collect_packages,
    collect_repositories,
    discover_projects,
    missingness,
    probe_conda_forge,
)
from oss_das.models import Forge, ForgeKind, ProjectRecord

PROJECT = ProjectRecord.model_validate(
    {
        "id": "example",
        "name": "Example",
        "repository": "owner/example",
        "description": "Example DAS package.",
        "status": "included",
        "decision_reason": "Meets the policy.",
        "primary_category": "processing",
        "license_spdx": "MIT",
        "registries": {"pypi": ["Example.Tool"], "conda": ["conda-forge/example"]},
    }
)

PYPI_PAYLOAD = {
    "info": {
        "name": "Example.Tool",
        "version": "1.0",
        "requires_python": ">=3.10",
        "requires_dist": ["numpy>=1.26", "example-extra; extra == 'docs'"],
        "project_url": "https://pypi.org/project/Example.Tool/",
    },
    "releases": {"1.0": [{"upload_time_iso_8601": "2026-01-01T00:00:00Z"}]},
}


def _clients(stats_handler, conda_handler=None):
    def pypi_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=PYPI_PAYLOAD)

    def default_conda(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"name": "example", "files": []})

    def build(handler, base_url):
        return httpx.Client(transport=httpx.MockTransport(handler), base_url=base_url)

    return (
        PyPIClient(client=build(pypi_handler, "https://pypi.org")),
        PyPIStatsClient(
            client=build(stats_handler, "https://pypistats.org"),
            min_interval=0,
            backoff=0,
        ),
        CondaClient(
            client=build(conda_handler or default_conda, "https://api.anaconda.org")
        ),
    )


def test_missingness_separates_absence_from_unreachability() -> None:
    absent = missingness(NotFoundError("url"), absent_reason="not_published")
    assert absent == {"missing_reason": "not_published"}

    unreachable = missingness(SourceError("boom"), absent_reason="not_published")
    assert unreachable["missing_reason"] == "fetch_error"
    assert unreachable["error"] == "boom"

    prefixed = missingness(SourceError("boom"), absent_reason="x", prefix="stats_")
    assert set(prefixed) == {"stats_missing_reason", "stats_error"}


def test_stats_failure_keeps_registry_metadata_and_records_the_reason() -> None:
    def stats_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429)

    pypi, stats, conda = _clients(stats_handler)
    records, daily = collect_packages(pypi, stats, conda, [PROJECT])

    pypi_record = next(item for item in records if item["registry"] == "pypi")
    assert pypi_record["missing_reason"] is None
    assert pypi_record["version"] == "1.0"
    assert pypi_record["requires_dist"] == [
        "numpy>=1.26",
        "example-extra; extra == 'docs'",
    ]
    assert pypi_record["stats_missing_reason"] == "fetch_error"
    assert "downloads_last_month" not in pypi_record
    assert daily == []


def test_absent_stats_package_is_unavailable_not_a_fetch_error() -> None:
    """A 404 from PyPI Stats is a different claim from an unreachable service."""

    def stats_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404)

    pypi, stats, conda = _clients(stats_handler)
    records, _ = collect_packages(pypi, stats, conda, [PROJECT])

    pypi_record = next(item for item in records if item["registry"] == "pypi")
    assert pypi_record["stats_missing_reason"] == "unavailable"
    assert "stats_error" not in pypi_record


def test_stats_uses_the_pep_503_normalized_package_name() -> None:
    requested: list[str] = []

    def stats_handler(request: httpx.Request) -> httpx.Response:
        requested.append(request.url.path)
        if request.url.path.endswith("/recent"):
            return httpx.Response(200, json={"data": {"last_month": 7}})
        return httpx.Response(200, json={"data": []})

    pypi, stats, conda = _clients(stats_handler)
    records, _ = collect_packages(pypi, stats, conda, [PROJECT])

    assert requested == [
        "/api/packages/example-tool/recent",
        "/api/packages/example-tool/overall",
    ]
    pypi_record = next(item for item in records if item["registry"] == "pypi")
    assert pypi_record["downloads_last_month"] == 7
    assert pypi_record["stats_missing_reason"] is None


def test_unpublished_conda_package_is_not_published() -> None:
    def stats_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/recent"):
            return httpx.Response(200, json={"data": {"last_month": 1}})
        return httpx.Response(200, json={"data": []})

    def conda_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404)

    pypi, stats, conda = _clients(stats_handler, conda_handler)
    records, _ = collect_packages(pypi, stats, conda, [PROJECT])

    conda_record = next(item for item in records if item["registry"] == "conda")
    assert conda_record["missing_reason"] == "not_published"
    assert conda_record["channel"] == "conda-forge"
    assert conda_record["name"] == "example"


def _conda_only(handler) -> CondaClient:
    return CondaClient(
        client=httpx.Client(
            transport=httpx.MockTransport(handler), base_url="https://api.anaconda.org"
        )
    )


def test_probe_reports_an_undeclared_conda_forge_package() -> None:
    """DASPy shipped on conda-forge for months without being curated."""
    conda = _conda_only(
        lambda request: httpx.Response(200, json={"name": "example-tool", "files": []})
    )
    assert probe_conda_forge(conda, [PROJECT]) == [
        {
            "project_id": "example",
            "identifier": "conda-forge/example-tool",
            "status": "undeclared",
        }
    ]


def test_probe_stays_quiet_when_the_package_is_absent() -> None:
    conda = _conda_only(lambda request: httpx.Response(404))
    assert probe_conda_forge(conda, [PROJECT]) == []


def test_probe_reports_a_package_it_could_not_check() -> None:
    """Silence must not read as absence when the source was unreachable."""
    conda = _conda_only(lambda request: httpx.Response(503))
    conda.backoff = 0  # do not spend the real retry delay in a test
    findings = probe_conda_forge(conda, [PROJECT])
    assert [item["status"] for item in findings] == ["unchecked"]


def test_probe_skips_packages_already_declared() -> None:
    declared = PROJECT.model_copy(
        update={
            "registries": PROJECT.registries.model_copy(
                update={"conda": ["conda-forge/example-tool"]}
            )
        }
    )
    conda = _conda_only(
        lambda request: httpx.Response(200, json={"name": "example-tool", "files": []})
    )
    assert probe_conda_forge(conda, [declared]) == []


class _FakeForge:
    """A forge whose answers are fixed, so discovery logic is what is tested."""

    def __init__(self, kind, host, results=None, total=None, namespaces=None):
        self.kind = kind
        self.host = host
        self._results = results or {}
        self._total = total
        self._namespaces = namespaces or {}

    def search_repositories(self, query):
        hits = self._results.get(query)
        if hits is None:
            raise SourceError(f"{self.host} refused {query}")
        truncated = None if self._total is None else self._total > len(hits)
        return SearchResult(hits, self._total, truncated)

    def list_namespace_repositories(self, namespace):
        return self._namespaces.get(namespace, [])


def _answers(queries, hits):
    """Give every query its own result list, so no test shares mutable state."""
    return {query: list(hits) for query in queries}


def _hit(host, repository, kind=ForgeKind.GITHUB):
    return {
        "forge_kind": kind.value,
        "forge_host": host,
        "repository": repository,
        "name": repository.split("/")[-1],
        "description": None,
        "html_url": f"https://{host}/{repository}",
        "stars_at_discovery": 3,
        "language": "Python",
    }


def test_discovery_merges_the_same_project_found_on_one_host_by_two_probes() -> None:
    forge = _FakeForge(
        ForgeKind.GITHUB,
        "github.com",
        results=_answers(GITHUB_DISCOVERY_QUERIES, [_hit("github.com", "org/tool")]),
        total=1,
        namespaces={"owner": [_hit("github.com", "org/tool")]},
    )
    records, _ = discover_projects([forge], [PROJECT])

    tool = next(item for item in records if item["repository"] == "org/tool")
    assert len(tool["probes"].split(";")) == len(GITHUB_DISCOVERY_QUERIES) + 1
    assert tool["source"] == "namespace;search"
    assert tool["catalog_status"] == "unreviewed"


def test_discovery_keeps_same_path_on_two_hosts_apart() -> None:
    """github.com/org/tool and a GitLab org/tool are different projects."""
    forges = [
        _FakeForge(
            ForgeKind.GITHUB,
            "github.com",
            results=_answers(
                GITHUB_DISCOVERY_QUERIES, [_hit("github.com", "org/tool")]
            ),
            total=1,
        ),
        _FakeForge(
            ForgeKind.GITLAB,
            "git.example.org",
            results=_answers(
                PATH_SEARCH_QUERIES,
                [_hit("git.example.org", "org/tool", ForgeKind.GITLAB)],
            ),
        ),
    ]
    records, _ = discover_projects(forges, [])

    assert [item["forge_host"] for item in records] == [
        "git.example.org",
        "github.com",
    ]


def test_discovery_records_a_truncated_query_rather_than_hiding_it() -> None:
    forge = _FakeForge(
        ForgeKind.GITHUB,
        "github.com",
        results=_answers(GITHUB_DISCOVERY_QUERIES, [_hit("github.com", "org/tool")]),
        total=2366,
    )
    _, coverage = discover_projects([forge], [])

    assert all(entry["truncated"] for entry in coverage)
    assert {entry["reported_total"] for entry in coverage} == {2366}


def test_discovery_records_a_host_that_refused_a_query() -> None:
    """A failed probe must be distinguishable from a probe that found nothing."""
    queries = _answers(GITHUB_DISCOVERY_QUERIES, [])
    queries.pop(GITHUB_DISCOVERY_QUERIES[0])
    forge = _FakeForge(ForgeKind.GITHUB, "github.com", results=queries, total=0)

    _, coverage = discover_projects([forge], [])

    failed = [entry for entry in coverage if entry["status"] == "failed"]
    assert [entry["query"] for entry in failed] == [GITHUB_DISCOVERY_QUERIES[0]]
    assert "refused" in failed[0]["error"]


def test_discovery_keeps_a_curated_project_no_search_returned() -> None:
    forge = _FakeForge(
        ForgeKind.GITHUB,
        "github.com",
        results=_answers(GITHUB_DISCOVERY_QUERIES, []),
    )
    records, _ = discover_projects([forge], [PROJECT])

    seed = next(item for item in records if item["repository"] == "owner/example")
    assert seed["source"] == "curated-seed"
    assert seed["catalog_id"] == "example"


def test_repository_collection_reports_a_host_with_no_client() -> None:
    """A project on an unconfigured forge must not silently vanish."""
    elsewhere = PROJECT.model_copy(
        update={"forge": Forge(kind=ForgeKind.GITLAB, host="git.example.org")}
    )
    records = collect_repositories([], [elsewhere])

    assert records[0]["missing_reason"] == "unavailable"
    assert "no client configured" in records[0]["error"]


def test_a_candidate_found_only_by_an_acronym_probe_is_labelled_broad() -> None:
    """ "das" matches German prose and dashboards; the label keeps that visible."""
    forge = _FakeForge(
        ForgeKind.GITLAB,
        "git.example.org",
        results={
            "das": [_hit("git.example.org", "user/dashboard", ForgeKind.GITLAB)],
            "otdr": [],
            "distributed acoustic sensing": [],
            "fiber optic sensing": [],
        },
    )
    records, coverage = discover_projects([forge], [])

    assert records[0]["probe_class"] == "broad-acronym"
    broad = {entry["query"] for entry in coverage if entry["specific"] is False}
    assert broad == {"das", "otdr"}


def test_a_candidate_any_specific_probe_found_is_labelled_specific() -> None:
    hit = _hit("git.example.org", "group/dastools", ForgeKind.GITLAB)
    forge = _FakeForge(
        ForgeKind.GITLAB,
        "git.example.org",
        results={
            "das": [hit],
            "distributed acoustic sensing": [hit],
            "fiber optic sensing": [],
            "otdr": [],
        },
    )
    records, _ = discover_projects([forge], [])

    assert records[0]["probe_class"] == "domain-specific"


def test_a_curated_project_is_specific_even_if_no_probe_found_it() -> None:
    forge = _FakeForge(
        ForgeKind.GITHUB, "github.com", results=_answers(GITHUB_DISCOVERY_QUERIES, [])
    )
    records, _ = discover_projects([forge], [PROJECT])

    assert records[0]["probe_class"] == "domain-specific"
