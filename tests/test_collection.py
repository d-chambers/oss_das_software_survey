from __future__ import annotations

import httpx
import pytest

from oss_das.clients.base import NotFoundError, SourceError
from oss_das.clients.packages import CondaClient, PyPIClient, PyPIStatsClient
from oss_das.collection import (
    collect_packages,
    collect_repositories,
    missingness,
    open_forges,
    probe_conda_forge,
)
from oss_das.core import load_projects, load_rejections
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


def test_open_forges_leaves_github_out_without_a_token() -> None:
    """Anonymous GitHub search is ten requests a minute; skipping beats hammering."""
    anonymous = open_forges(None)
    try:
        assert ForgeKind.GITHUB not in {forge.kind for forge in anonymous}
        assert {forge.kind for forge in anonymous} == {
            ForgeKind.GITLAB,
            ForgeKind.GITEA,
        }
    finally:
        for forge in anonymous:
            forge.close()
    with_token = open_forges("token")
    try:
        assert with_token[0].kind == ForgeKind.GITHUB
    finally:
        for forge in with_token:
            forge.close()


def test_repository_collection_reports_a_host_with_no_client() -> None:
    """A project on an unconfigured forge must not silently vanish."""
    elsewhere = PROJECT.model_copy(
        update={"forge": Forge(kind=ForgeKind.GITLAB, host="git.example.org")}
    )
    records = collect_repositories([], [elsewhere])

    assert records[0]["missing_reason"] == "unavailable"
    assert "no client configured" in records[0]["error"]


class TestRejectionLedger:
    """A reviewed rejection must stop a candidate coming back as unreviewed."""

    def test_missing_ledger_is_empty_not_an_error(self, tmp_path):
        assert load_rejections(tmp_path / "absent.yml") == {}

    def test_keys_are_lowercased_to_match_forge_key(self, tmp_path):
        path = tmp_path / "rejected.yml"
        path.write_text(
            "rejections:\n"
            '  "GitHub.com/Acme/Thing":\n'
            "    reason: duplicate\n"
            "    note: Already catalogued.\n"
        )
        loaded = load_rejections(path)
        assert loaded == {
            "github.com/acme/thing": {
                "reason": "duplicate",
                "note": "Already catalogued.",
            }
        }

    def test_note_is_optional(self, tmp_path):
        path = tmp_path / "rejected.yml"
        path.write_text('rejections:\n  "a.com/x/y":\n    reason: teaching\n')
        assert load_rejections(path)["a.com/x/y"]["note"] == ""

    def test_entry_without_a_reason_is_rejected(self, tmp_path):
        path = tmp_path / "rejected.yml"
        path.write_text('rejections:\n  "a.com/x/y":\n    note: no reason given\n')
        with pytest.raises(ValueError, match="needs a 'reason'"):
            load_rejections(path)

    def test_non_mapping_rejections_block_is_rejected(self, tmp_path):
        path = tmp_path / "rejected.yml"
        path.write_text("rejections:\n  - a.com/x/y\n")
        with pytest.raises(ValueError, match="must be a mapping"):
            load_rejections(path)

    def test_shipped_ledger_loads_and_keys_look_like_candidate_keys(self):
        """Forge keys are host/owner/name; registry keys are registry/name."""
        ledger = load_rejections()
        assert ledger, "the repository ships a reviewed ledger"
        for key, value in ledger.items():
            assert key == key.lower()
            assert len(key.split("/")) >= 2, key
            assert value["reason"]

    def test_ledger_never_claims_a_catalogued_project(self):
        # A curated file wins; a key in both would make the catalog ambiguous.
        catalogued = {project.forge_key for project in load_projects()}
        assert not (catalogued & set(load_rejections()))
