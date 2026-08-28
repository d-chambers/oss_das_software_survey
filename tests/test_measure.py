"""Tests for the per-source measured-record builders; no network."""

from __future__ import annotations

import shutil
import subprocess
from datetime import date

import httpx
import pytest

from oss_das.clients import (
    CondaClient,
    JuliaRegistryClient,
    OpenAlexClient,
    PyPIClient,
    PyPIStatsClient,
)
from oss_das.clients.base import NotFoundError, SourceError
from oss_das.core import read_csv, read_frontmatter
from oss_das.measure import (
    FORGE_FIELDS,
    GIT_COMMIT_FIELDS,
    ForgeClients,
    commit_rows,
    count_authors,
    dependency_names,
    downloads_in_window,
    forge_fields,
    forge_record,
    git_record,
    mirror_record,
    publication_record,
    registry_record,
    write_commits,
    write_measured,
)
from oss_das.models import ForgeKind, ProjectRecord


def project(**overrides) -> ProjectRecord:
    base = {
        "id": "demo",
        "name": "Demo",
        "repository": "acme/demo",
        "description": "A demo project.",
        "status": "excluded",
        "decision_reason": "Fixture; excluded to prove status does not matter.",
        "primary_category": "library",
        "forge": {"kind": "github"},
    }
    return ProjectRecord.model_validate({**base, **overrides})


REGISTRY_ONLY = project(repository=None, registries={"pypi": ["demo"]})


def mock_client(handler, base_url):
    return httpx.Client(transport=httpx.MockTransport(handler), base_url=base_url)


# --- shared -------------------------------------------------------------------


class TestWriteMeasured:
    def test_common_keys_lead_and_missing_trails(self, tmp_path):
        path = write_measured(
            "forge",
            {"id": "x", "stars": 3, "missing": {"forks": "unavailable"}},
            tmp_path,
        )
        assert path == tmp_path / "x.md"
        front = read_frontmatter(path)
        assert list(front) == ["id", "source", "scanned_at", "stars", "missing"]
        assert front["source"] == "forge"
        assert front["scanned_at"].endswith("+00:00")
        assert front["missing"] == {"forks": "unavailable"}

    def test_missing_is_always_present(self, tmp_path):
        front = read_frontmatter(write_measured("git", {"id": "x"}, tmp_path))
        assert front["missing"] == {}


# --- mirror -------------------------------------------------------------------


pytestmark_git = pytest.mark.skipif(shutil.which("git") is None, reason="git required")


def git(repo, *args):
    subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        env={
            "PATH": "/usr/bin:/bin",
            "HOME": str(repo),
            "GIT_AUTHOR_NAME": "Ada",
            "GIT_AUTHOR_EMAIL": "ada@example.com",
            "GIT_COMMITTER_NAME": "Ada",
            "GIT_COMMITTER_EMAIL": "ada@example.com",
            "GIT_AUTHOR_DATE": "2024-01-02T03:04:05+00:00",
            "GIT_COMMITTER_DATE": "2024-01-02T03:04:05+00:00",
        },
    )


@pytest.fixture
def source_repo(tmp_path):
    """Two commits on `trunk`: one Python file, then a second by a bot."""
    repo = tmp_path / "source"
    repo.mkdir()
    git(repo, "init", "--quiet", "--initial-branch", "trunk")
    (repo / "a.py").write_text("one\ntwo\n")
    git(repo, "add", "a.py")
    git(repo, "commit", "--quiet", "-m", "first")
    (repo / "a.py").write_text("one\ntwo\nthree\n")
    git(repo, "add", "a.py")
    git(
        repo,
        "commit",
        "--quiet",
        "-m",
        "second",
        "--author=dependabot[bot] <bot@example.com>",
        "--date=2024-02-03T00:00:00+00:00",
    )
    return repo


@pytestmark_git
class TestMirrorRecord:
    def test_registry_only_project_is_not_applicable(self, tmp_path):
        record = mirror_record(REGISTRY_ONLY, tmp_path)
        assert record["result"] == "not_applicable"
        assert record["missing"] == {"repository": "not_applicable"}
        assert record["path"] is None

    def test_clone_then_unchanged_then_updated(self, tmp_path, source_repo):
        local = project().model_copy(update={"repository_url": str(source_repo)})
        first = mirror_record(local, tmp_path / "repos")
        assert first["result"] == "cloned"
        assert first["repo_bytes"] > 0
        assert first["missing"] == {}
        assert (tmp_path / "repos" / "demo.git").exists()
        assert mirror_record(local, tmp_path / "repos")["result"] == "unchanged"
        assert (
            mirror_record(local, tmp_path / "repos", update=True)["result"] == "updated"
        )

    def test_failed_clone_carries_the_error(self, tmp_path):
        local = project().model_copy(update={"repository_url": str(tmp_path / "nope")})
        record = mirror_record(local, tmp_path / "repos", timeout=60)
        assert record["result"] == "failed"
        assert record["error"]
        assert record["missing"] == {"mirror": "fetch_error"}
        assert record["repo_bytes"] is None

    def test_disk_admission_blocks_fresh_clones_only(self, tmp_path, source_repo):
        local = project().model_copy(update={"repository_url": str(source_repo)})
        blocked = mirror_record(local, tmp_path / "repos", min_free_gb=1e9)
        assert blocked["result"] == "failed"
        assert "disk space" in blocked["error"]
        assert not (tmp_path / "repos" / "demo.git").exists()
        mirror_record(local, tmp_path / "repos")
        assert mirror_record(local, tmp_path / "repos", min_free_gb=1e9)["result"] == (
            "unchanged"
        )


# --- git ----------------------------------------------------------------------


class TestCountAuthors:
    def test_names_and_emails_join_one_person(self):
        pairs = [
            ("Ada", "ada@example.com"),
            ("Ada Lovelace", "ada@example.com"),
            ("Ada Lovelace", "ada@work.org"),
            ("Bo", "bo@example.com"),
        ]
        assert count_authors(pairs) == 2

    def test_bots_are_not_people(self):
        pairs = [("Ada", "ada@example.com"), ("dependabot[bot]", "x@y.z")]
        assert count_authors(pairs) == 1

    def test_empty(self):
        assert count_authors([]) == 0


@pytestmark_git
class TestGitRecord:
    def test_registry_only_project_is_not_applicable(self, tmp_path):
        record, commits = git_record(REGISTRY_ONLY, tmp_path)
        assert record["missing"] == {"git": "not_applicable"}
        assert commits == []
        assert record["commits"] is None

    def test_missing_mirror_is_unavailable(self, tmp_path):
        record, _ = git_record(project(), tmp_path)
        assert record["missing"] == {"git": "unavailable"}
        assert record["commits"] is None

    def test_measures_a_mirror(self, tmp_path, source_repo):
        local = project().model_copy(update={"repository_url": str(source_repo)})
        mirror_record(local, tmp_path / "repos")
        record, commits = git_record(local, tmp_path / "repos")
        assert record["ref"] == "trunk"
        assert len(record["tip"]) == 40
        assert record["commits"] == 2
        assert record["merges"] == 0
        assert record["authors"] == 1  # the bot does not count
        assert record["first_commit_at"].startswith("2024-01-02")
        assert record["last_commit_at"].startswith("2024-02-03")
        assert (record["insertions"], record["deletions"]) == (3, 0)
        assert record["lines_by_language"] == {"Python": 3}
        assert record["lines_total"] == 3
        assert record["primary_language"] == "Python"
        assert record["missing"] == {}
        assert len(commits) == 2

    def test_no_counted_source_is_a_reason_not_zero(self, tmp_path):
        repo = tmp_path / "prose"
        repo.mkdir()
        git(repo, "init", "--quiet", "--initial-branch", "main")
        (repo / "README.md").write_text("words\n")
        git(repo, "add", "README.md")
        git(repo, "commit", "--quiet", "-m", "docs")
        local = project().model_copy(update={"repository_url": str(repo)})
        mirror_record(local, tmp_path / "repos")
        record, _ = git_record(local, tmp_path / "repos")
        assert record["commits"] == 1
        assert record["lines_total"] is None
        assert record["primary_language"] is None
        assert record["missing"] == {"lines": "not_published"}

    def test_empty_mirror_is_unavailable(self, tmp_path):
        repos = tmp_path / "repos"
        repos.mkdir()
        subprocess.run(
            ["git", "init", "--quiet", "--bare", str(repos / "demo.git")],
            check=True,
            capture_output=True,
        )
        record, _ = git_record(project(), repos)
        assert record["missing"] == {"git": "unavailable"}
        assert record["error"] == "no mainline ref"

    def test_commit_csv_has_no_status_column(self, tmp_path, source_repo):
        local = project().model_copy(update={"repository_url": str(source_repo)})
        mirror_record(local, tmp_path / "repos")
        _, commits = git_record(local, tmp_path / "repos")
        path = tmp_path / "commits" / "demo.csv"
        write_commits(path, commit_rows(local, commits))
        rows = read_csv(path)
        assert list(rows[0]) == GIT_COMMIT_FIELDS
        assert "status" not in rows[0]
        assert {row["project_id"] for row in rows} == {"demo"}
        assert not list(path.parent.glob("*.partial"))


# --- forge --------------------------------------------------------------------


class FakeForge:
    def __init__(self, payload=None, error=None):
        self.payload, self.error = payload, error

    def collect_repository(self, repository):
        if self.error:
            raise self.error
        return self.payload


class FakeClients(ForgeClients):
    def __init__(self, forge):
        super().__init__("token")
        self.forge = forge

    def get(self, kind, host):
        return self.forge


GITHUB_PAYLOAD = {
    "stars": 5,
    "forks": 1,
    "contributors": 2,
    "contributors_basis": "linked accounts, bots removed",
    "release_count": 0,
    "created_at": "2020-01-01T00:00:00Z",
    "pushed_at": "2024-01-01T00:00:00Z",
    "last_commit_at": "2024-01-01T00:00:00Z",
    "latest_release_at": None,
    "archived": False,
    "visibility": "public",
    "language": "Python",
    "language_bytes": {"Python": 100},
    "has_docs": True,
    "has_tests": False,
    "has_ci": True,
    "license_detected": None,
    "license_detected_vocabulary": "spdx",
    "commits": 12,
    "commits_missing_reason": None,
    "source_url": "https://api.github.com/repos/acme/demo",
}


class TestForgeRecord:
    def test_registry_only_project_is_not_applicable(self):
        record = forge_record(REGISTRY_ONLY, ForgeClients("token"))
        assert record["missing"] == {"repository": "not_applicable"}
        # The failure record still has every contract field, all empty.
        assert {record[field] for field in FORGE_FIELDS} == {None}

    def test_truncated_tree_makes_negative_signals_unavailable(self):
        payload = {**GITHUB_PAYLOAD, "tree_truncated": True}
        record = forge_fields(payload)
        assert record["has_docs"] is True
        assert record["has_tests"] is None
        assert record["missing"]["has_tests"] == "unavailable"
        assert "has_docs" not in record["missing"]

    def test_github_without_token_is_unavailable_not_fetched(self):
        record = forge_record(project(), ForgeClients(None))
        assert record["missing"] == {"repository": "unavailable"}
        assert record["error"] == "no GITHUB_TOKEN"

    def test_gitlab_needs_no_token(self):
        clients = ForgeClients(None)
        client = clients.get(ForgeKind.GITLAB, "git.example.org")
        assert client is not None
        assert client.host == "git.example.org"
        clients.close()

    def test_contract_fields_and_reasons(self):
        record = forge_record(project(), FakeClients(FakeForge(GITHUB_PAYLOAD)))
        assert record["stars"] == 5
        assert record["releases"] == 0
        assert record["source_url"] == "https://api.github.com/repos/acme/demo"
        assert "commits" not in record
        assert record["missing"] == {
            "latest_release_at": "not_applicable",
            "license_detected": "not_published",
        }

    def test_client_reasons_are_carried(self):
        payload = {
            **GITHUB_PAYLOAD,
            "contributors": None,
            "contributors_missing_reason": "unavailable",
            "last_commit_at": None,
            "commits_missing_reason": "unavailable",
            "language_bytes": {},
        }
        missing = forge_fields(payload)["missing"]
        assert missing["contributors"] == "unavailable"
        assert missing["last_commit_at"] == "unavailable"
        assert missing["language_bytes"] == "not_published"

    def test_not_found_is_unavailable_and_failure_is_fetch_error(self):
        gone = forge_record(project(), FakeClients(FakeForge(error=NotFoundError("x"))))
        assert gone["missing"] == {"repository": "unavailable"}
        down = forge_record(
            project(), FakeClients(FakeForge(error=SourceError("boom")))
        )
        assert down["missing"] == {"repository": "fetch_error"}
        assert down["error"] == "boom"


# --- registry -----------------------------------------------------------------


class TestDependencyNames:
    def test_strips_specifiers_markers_and_extras(self):
        requires = [
            "numpy>=1.26",
            "PyYAML (>=6) ; python_version >= '3.10'",
            "sphinx; extra == 'docs'",
            'pytest>=8 ; extra == "test"',
            "pyyaml",
            "h5py[mpi]>=3",
        ]
        assert dependency_names(requires) == ["h5py", "numpy", "pyyaml"]

    def test_unparseable_requirement_keeps_its_name(self):
        assert dependency_names(["weird-pkg >>> 1", "gone; extra == 'x' >>>"]) == [
            "weird-pkg"
        ]


class TestDownloadsInWindow:
    def test_sums_only_the_last_180_days(self):
        daily = [
            {"date": "2026-08-28", "downloads": 5},
            {"date": "2026-03-02", "downloads": 7},  # 179 days back: inside
            {"date": "2026-03-01", "downloads": 100},  # 180 days back: outside
            {"date": "2025-01-01", "downloads": 1000},
            {"date": "bad", "downloads": 1},
        ]
        assert downloads_in_window(daily, today=date(2026, 8, 28)) == 12

    def test_no_observations_is_none_not_zero(self):
        assert downloads_in_window([], today=date(2026, 8, 28)) is None
        old = [{"date": "2020-01-01", "downloads": 3}]
        assert downloads_in_window(old, today=date(2026, 8, 28)) is None
        blank = [{"date": "2026-08-28", "downloads": None}]
        assert downloads_in_window(blank, today=date(2026, 8, 28)) is None


PYPI_PAYLOAD = {
    "info": {
        "name": "demo",
        "version": "1.2",
        "requires_dist": ["numpy>=1.26", "sphinx; extra == 'docs'"],
    },
    "releases": {
        "1.0": [{"upload_time_iso_8601": "2025-01-01T00:00:00Z"}],
        "1.2": [{"upload_time_iso_8601": "2026-02-01T00:00:00Z"}],
    },
}


def registry_clients(
    *, pypi_status=200, stats_status=200, conda_status=200, julia_status=200
):
    def pypi(request):
        if "/gone/" in request.url.path:
            return httpx.Response(404)
        return httpx.Response(pypi_status, json=PYPI_PAYLOAD)

    def stats(request):
        if request.url.path.endswith("/recent"):
            return httpx.Response(stats_status, json={"data": {"last_month": 30}})
        return httpx.Response(
            stats_status,
            json={
                "data": [
                    {
                        "category": "without_mirrors",
                        "date": "2026-08-27",
                        "downloads": 4,
                    },
                    {
                        "category": "without_mirrors",
                        "date": "2025-01-01",
                        "downloads": 9,
                    },
                ]
            },
        )

    def conda(request):
        return httpx.Response(
            conda_status,
            json={"name": "demo", "files": [{"ndownloads": 40}, {"ndownloads": 2}]},
        )

    def julia(request):
        return httpx.Response(julia_status, json={"type": "file"})

    return (
        PyPIClient(client=mock_client(pypi, "https://pypi.org")),
        PyPIStatsClient(
            client=mock_client(stats, "https://pypistats.org"),
            min_interval=0,
            backoff=0,
        ),
        CondaClient(client=mock_client(conda, "https://api.anaconda.org")),
        JuliaRegistryClient(client=mock_client(julia, "https://api.github.com")),
    )


FULL = project(
    registries={"pypi": ["demo"], "conda": ["conda-forge/demo"], "julia": ["Demo"]}
)


class TestRegistryRecord:
    def test_project_with_no_packages(self):
        record = registry_record(project(), *registry_clients())
        assert record["pypi"] == record["conda"] == record["julia"] == []
        assert record["pypi_downloads_30d"] is None
        assert record["dependencies"] == []
        assert record["missing"] == {
            "pypi_downloads_30d": "not_applicable",
            "pypi_downloads_180d": "not_applicable",
            "conda_downloads_total": "not_applicable",
            "dependencies": "not_applicable",
        }

    def test_full_record(self):
        record = registry_record(FULL, *registry_clients(), today=date(2026, 8, 28))
        (pkg,) = record["pypi"]
        assert pkg["name"] == "demo"
        assert pkg["version"] == "1.2"
        assert pkg["latest_upload_at"] == "2026-02-01T00:00:00Z"
        assert pkg["release_count"] == 2
        assert pkg["downloads_30d"] == 30
        assert pkg["downloads_180d"] == 4
        assert pkg["source_url"] == "https://pypi.org/pypi/demo/json"
        assert pkg["missing"] == {}
        assert record["pypi_downloads_30d"] == 30
        assert record["pypi_downloads_180d"] == 4
        assert record["conda"][0]["downloads_total"] == 42
        assert record["conda_downloads_total"] == 42
        assert record["julia"] == [
            {
                "name": "Demo",
                "registered": True,
                "source_url": (
                    "https://api.github.com/repos/JuliaRegistries/General/contents/"
                    "D/Demo/Package.toml"
                ),
                "missing": {},
            }
        ]
        assert record["dependencies"] == ["numpy"]
        assert record["missing"] == {}

    def test_one_unread_package_makes_the_totals_missing(self):
        two = project(registries={"pypi": ["Demo", "gone"]})
        record = registry_record(two, *registry_clients(), today=date(2026, 8, 28))
        assert record["pypi"][0]["downloads_30d"] == 30  # the floor stays
        assert record["pypi_downloads_30d"] is None
        assert record["dependencies"] == []
        assert record["missing"] == {
            "pypi_downloads_30d": "not_published",
            "pypi_downloads_180d": "not_published",
            "conda_downloads_total": "not_applicable",
            "dependencies": "not_published",
        }

    def test_unpublished_pypi_package(self):
        record = registry_record(FULL, *registry_clients(pypi_status=404))
        (pkg,) = record["pypi"]
        assert pkg["missing"] == {
            "metadata": "not_published",
            "downloads": "not_published",
        }
        assert record["pypi_downloads_30d"] is None
        assert record["missing"]["pypi_downloads_30d"] == "not_published"
        assert record["missing"]["dependencies"] == "not_published"
        assert "conda_downloads_total" not in record["missing"]

    def test_stats_outage_is_a_fetch_error_and_keeps_metadata(self):
        record = registry_record(FULL, *registry_clients(stats_status=500))
        (pkg,) = record["pypi"]
        assert pkg["version"] == "1.2"
        assert pkg["missing"] == {"downloads": "fetch_error"}
        assert record["missing"]["pypi_downloads_180d"] == "fetch_error"

    def test_unregistered_julia_package_is_a_finding(self):
        record = registry_record(FULL, *registry_clients(julia_status=404))
        assert record["julia"][0]["registered"] is False
        assert record["julia"][0]["missing"] == {}

    def test_unpublished_conda_package(self):
        record = registry_record(FULL, *registry_clients(conda_status=404))
        assert record["conda"][0]["downloads_total"] is None
        assert record["missing"]["conda_downloads_total"] == "not_published"


# --- publications -------------------------------------------------------------


def openalex_client(counts: dict[str, int | None]):
    def handler(request):
        doi = request.url.path.rsplit("doi.org/", 1)[-1]
        if doi not in counts:
            return httpx.Response(404)
        if counts[doi] == "down":
            return httpx.Response(500)
        return httpx.Response(
            200,
            json={
                "display_name": f"Paper {doi}",
                "publication_year": 2024,
                "type": "article",
                "cited_by_count": counts[doi],
                "id": f"https://openalex.org/W{abs(hash(doi)) % 1000}",
            },
        )

    return OpenAlexClient(client=mock_client(handler, "https://api.openalex.org"))


PAPERS = project(
    publications=[
        {"doi": "10.1/canon", "role": "canonical"},
        {"doi": "10.1/related", "role": "related"},
    ]
)


class TestPublicationRecord:
    def test_no_dois_is_not_applicable(self):
        record = publication_record(project(), openalex_client({}))
        assert record["publications"] == []
        assert record["citations_total"] is None
        assert record["missing"] == {
            "publications": "not_applicable",
            "canonical_citations": "not_applicable",
        }

    def test_total_versus_canonical(self):
        record = publication_record(
            PAPERS, openalex_client({"10.1/canon": 7, "10.1/related": 3})
        )
        assert record["citations_total"] == 10
        assert record["canonical_citations"] == 7
        assert record["missing"] == {}
        canon = record["publications"][0]
        assert canon["title"] == "Paper 10.1/canon"
        assert canon["year"] == 2024
        assert canon["work_type"] == "article"
        assert canon["openalex_id"].startswith("https://openalex.org/W")
        assert canon["source_url"].endswith("10.1/canon")

    def test_unindexed_canonical_makes_both_totals_unavailable(self):
        record = publication_record(PAPERS, openalex_client({"10.1/related": 3}))
        # A sum that leaves a DOI out is not the total; the related count
        # stays in the item list as the floor.
        assert record["citations_total"] is None
        assert record["publications"][1]["cited_by_count"] == 3
        assert record["canonical_citations"] is None
        assert record["publications"][0]["missing"] == {"work": "unavailable"}
        assert record["missing"] == {
            "citations_total": "unavailable",
            "canonical_citations": "unavailable",
        }

    def test_outage_is_a_fetch_error(self):
        record = publication_record(
            PAPERS, openalex_client({"10.1/canon": "down", "10.1/related": "down"})
        )
        assert record["citations_total"] is None
        assert record["missing"] == {
            "citations_total": "fetch_error",
            "canonical_citations": "fetch_error",
        }

    def test_only_related_dois(self):
        related = project(publications=[{"doi": "10.1/related", "role": "related"}])
        record = publication_record(related, openalex_client({"10.1/related": 3}))
        assert record["citations_total"] == 3
        assert record["missing"] == {"canonical_citations": "not_applicable"}
