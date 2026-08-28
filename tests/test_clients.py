from __future__ import annotations

import httpx
import pytest

from oss_das.clients import base
from oss_das.clients.base import JsonClient, NotFoundError, SourceError
from oss_das.clients.github import GitHubClient
from oss_das.clients.gitlab import GitLabClient
from oss_das.clients.julia import JuliaRegistryClient
from oss_das.clients.packages import CondaClient, PyPIStatsClient


def test_github_repository_normalization_and_signals() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path == "/repos/org/tool":
            return httpx.Response(
                200,
                json={
                    "id": 1,
                    "html_url": "https://github.com/org/tool",
                    "description": "Tool",
                    "stargazers_count": 12,
                    "forks_count": 3,
                    "created_at": "2020-01-01T00:00:00Z",
                    "pushed_at": "2026-08-01T00:00:00Z",
                    "archived": False,
                    "language": "Python",
                    "license": {"spdx_id": "MIT"},
                    "default_branch": "main",
                },
            )
        if path.endswith("/contributors"):
            return httpx.Response(
                200,
                json=[
                    {"login": "human", "type": "User"},
                    {"login": "dependabot[bot]", "type": "Bot"},
                ],
            )
        if path.endswith("/releases"):
            return httpx.Response(
                200,
                json=[{"draft": False, "published_at": "2026-07-01T00:00:00Z"}],
            )
        if path.endswith("/languages"):
            return httpx.Response(200, json={"Python": 3200, "Jupyter Notebook": 900})
        if path.endswith("/commits"):
            return httpx.Response(
                200,
                json=[{"commit": {"committer": {"date": "2026-08-01T00:00:00Z"}}}],
                headers={
                    "Link": "<https://api.github.com/repositories/1/commits"
                    '?per_page=1&page=42>; rel="last"'
                },
            )
        if "/git/trees/" in path:
            return httpx.Response(
                200,
                json={
                    "truncated": False,
                    "tree": [
                        {"path": "docs/index.md"},
                        {"path": "tests/test_api.py"},
                        {"path": ".github/workflows/test.yml"},
                    ],
                },
            )
        raise AssertionError(path)

    client = httpx.Client(
        transport=httpx.MockTransport(handler), base_url="https://api.github.com"
    )
    record = GitHubClient(client=client).collect_repository("org/tool")
    assert record["stars"] == 12
    assert record["contributors"] == 1
    assert record["release_count"] == 1
    assert record["has_docs"] and record["has_tests"] and record["has_ci"]


def test_conda_sums_artifact_downloads() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "name": "tool",
                "latest_version": "1.0",
                "files": [
                    {"version": "0.9", "basename": "old", "ndownloads": 4},
                    {"version": "1.0", "basename": "new", "ndownloads": 6},
                ],
            },
        )

    client = httpx.Client(
        transport=httpx.MockTransport(handler), base_url="https://api.anaconda.org"
    )
    record = CondaClient(client=client).package("conda-forge", "tool")
    assert record["downloads_cumulative"] == 10


def test_pypi_stats_keeps_only_mirror_filtered_history() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/recent"):
            return httpx.Response(
                200, json={"data": {"last_day": 1, "last_week": 7, "last_month": 30}}
            )
        return httpx.Response(
            200,
            json={
                "data": [
                    {"category": "with_mirrors", "date": "2026-08-01", "downloads": 9},
                    {
                        "category": "without_mirrors",
                        "date": "2026-08-01",
                        "downloads": 3,
                    },
                ]
            },
        )

    client = httpx.Client(
        transport=httpx.MockTransport(handler), base_url="https://pypistats.org"
    )
    recent, daily = PyPIStatsClient(client=client, min_interval=0).package("tool")
    assert recent["last_month"] == 30
    assert daily == [
        {"category": "without_mirrors", "date": "2026-08-01", "downloads": 3}
    ]


def _counting_client(responses: list[httpx.Response]) -> tuple[httpx.Client, list[int]]:
    calls = [0]

    def handler(request: httpx.Request) -> httpx.Response:
        index = min(calls[0], len(responses) - 1)
        calls[0] += 1
        return responses[index]

    return (
        httpx.Client(
            transport=httpx.MockTransport(handler), base_url="https://example.com"
        ),
        calls,
    )


def test_json_client_retries_rate_limit_response() -> None:
    client, calls = _counting_client(
        [
            httpx.Response(429, headers={"retry-after": "0"}),
            httpx.Response(200, json={"ok": True}),
        ]
    )
    source = JsonClient(base_url="https://example.com", client=client)

    assert source.get_json("/record") == {"ok": True}
    assert calls[0] == 2


def test_json_client_ignores_unparsable_retry_after_header() -> None:
    """A Retry-After HTTP-date must fall back to backoff, not crash the run."""
    client, calls = _counting_client(
        [
            httpx.Response(
                429, headers={"retry-after": "Wed, 21 Oct 2026 07:28:00 GMT"}
            ),
            httpx.Response(200, json={"ok": True}),
        ]
    )
    source = JsonClient(base_url="https://example.com", client=client, backoff=0)

    assert source.get_json("/record") == {"ok": True}
    assert calls[0] == 2


def test_json_client_gives_up_after_max_attempts() -> None:
    client, calls = _counting_client([httpx.Response(429)])
    source = JsonClient(
        base_url="https://example.com", client=client, max_attempts=4, backoff=0
    )

    with pytest.raises(SourceError, match="repeated HTTP 429"):
        source.get_json("/record")
    assert calls[0] == 4


def test_json_client_retries_then_reports_transport_failures() -> None:
    """A timeout must become a SourceError, not escape and end the census."""
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        raise httpx.ConnectTimeout("connection timed out", request=request)

    client = httpx.Client(
        transport=httpx.MockTransport(handler), base_url="https://example.com"
    )
    source = JsonClient(
        base_url="https://example.com", client=client, max_attempts=3, backoff=0
    )

    with pytest.raises(SourceError, match="connection timed out"):
        source.get_json("/record")
    assert calls == 3


def test_json_client_recovers_from_a_transient_transport_failure() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise httpx.ConnectError("connection refused", request=request)
        return httpx.Response(200, json={"ok": True})

    client = httpx.Client(
        transport=httpx.MockTransport(handler), base_url="https://example.com"
    )
    source = JsonClient(base_url="https://example.com", client=client, backoff=0)

    assert source.get_json("/record") == {"ok": True}
    assert calls == 2


@pytest.mark.parametrize("header", ["-1", "nan", "inf", "soon"])
def test_json_client_falls_back_for_unusable_retry_after(header: str) -> None:
    """A negative or non-finite delay would crash time.sleep; backoff instead."""
    client, calls = _counting_client(
        [
            httpx.Response(429, headers={"retry-after": header}),
            httpx.Response(200, json={"ok": True}),
        ]
    )
    source = JsonClient(base_url="https://example.com", client=client, backoff=0)

    assert source.get_json("/record") == {"ok": True}
    assert calls[0] == 2


def test_json_client_caps_an_excessive_retry_after(monkeypatch) -> None:
    """An hour-long Retry-After must not stall a whole collection run."""
    slept: list[float] = []
    monkeypatch.setattr(base.time, "sleep", slept.append)
    client, calls = _counting_client(
        [
            httpx.Response(429, headers={"retry-after": "9999"}),
            httpx.Response(200, json={"ok": True}),
        ]
    )
    source = JsonClient(base_url="https://example.com", client=client)

    assert source.get_json("/record") == {"ok": True}
    assert slept == [base.MAX_RETRY_DELAY]
    assert calls[0] == 2


def test_json_client_reports_a_missing_record_distinctly() -> None:
    client, _ = _counting_client([httpx.Response(404)])
    source = JsonClient(base_url="https://example.com", client=client)

    with pytest.raises(NotFoundError):
        source.get_json("/record")


def _gitlab_handler(request: httpx.Request) -> httpx.Response:
    path = request.url.path
    page = request.url.params.get("page", "1")
    if path.endswith("/repository/contributors"):
        if page != "1":
            return httpx.Response(200, json=[])
        return httpx.Response(
            200,
            json=[
                {"name": "Ada Lovelace", "email": "ada@work.example"},
                {"name": "ada lovelace", "email": "ada@home.example"},
            ],
        )
    if path.endswith("/repository/commits"):
        if page != "1":
            return httpx.Response(200, json=[])
        return httpx.Response(
            200,
            json=[{"committed_date": "2026-01-02T00:00:00Z"}],
            headers={"X-Total": "137"},
        )
    if path.endswith("/repository/tree"):
        if page != "1":
            return httpx.Response(200, json=[])
        return httpx.Response(
            200,
            json=[
                {"path": "doc/index.rst"},
                {"path": "tests/test_read.py"},
                {"path": ".gitlab-ci.yml"},
            ],
        )
    if path.endswith("/repository/commits"):
        return httpx.Response(
            200,
            json=[{"committed_date": "2026-01-02T00:00:00Z"}],
            headers={"X-Total": "137"},
        )
    if path.endswith("/releases"):
        if page != "1":
            return httpx.Response(200, json=[])
        return httpx.Response(
            200, json=[{"tag_name": "v1.0", "released_at": "2026-01-01T00:00:00Z"}]
        )
    if path.endswith("/languages"):
        return httpx.Response(200, json={"Python": 90.0, "Shell": 10.0})
    return httpx.Response(
        200,
        json={
            "id": 7,
            "path_with_namespace": "group/tool",
            "name": "tool",
            "description": "DAS tool",
            "web_url": "https://git.example.org/group/tool",
            "star_count": 2,
            "forks_count": 0,
            "created_at": "2019-01-01T00:00:00Z",
            "last_activity_at": "2026-01-02T00:00:00Z",
            "default_branch": "master",
            "license": {"key": "gpl-3.0+"},
        },
    )


def _gitlab_client() -> GitLabClient:
    return GitLabClient(
        "git.example.org",
        client=httpx.Client(
            transport=httpx.MockTransport(_gitlab_handler),
            base_url="https://git.example.org/api/v4",
        ),
    )


def test_gitlab_detects_ci_from_its_own_pipeline_file() -> None:
    """Probing only GitHub's workflow directory would report no CI anywhere."""
    record = _gitlab_client().collect_repository("group/tool")

    assert record["has_ci"] is True
    assert record["signal_evidence"]["ci"] == ".gitlab-ci.yml"
    assert record["has_docs"] and record["has_tests"]


def test_gitlab_records_the_vocabulary_of_the_license_it_detected() -> None:
    """A GitLab license key is not an SPDX id and must not be labelled as one."""
    record = _gitlab_client().collect_repository("group/tool")

    assert record["license_detected"] == "gpl-3.0+"
    assert record["license_detected_vocabulary"] == "gitlab-license-key"


def test_gitlab_counts_one_person_committing_under_two_addresses_once() -> None:
    record = _gitlab_client().collect_repository("group/tool")

    assert record["contributors"] == 1
    assert record["contributors_basis"] == "distinct commit author names"


def test_gitlab_reports_a_closed_contributor_list_as_a_reason() -> None:
    """A restricted endpoint must not read as a project with no contributors."""

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/repository/contributors"):
            return httpx.Response(403)
        return _gitlab_handler(request)

    client = GitLabClient(
        "git.example.org",
        client=httpx.Client(
            transport=httpx.MockTransport(handler),
            base_url="https://git.example.org/api/v4",
        ),
    )
    record = client.collect_repository("group/tool")

    assert record["contributors"] is None
    assert record["contributors_missing_reason"] == "unavailable"


def test_github_search_pages_past_the_first_hundred_results() -> None:
    """One page silently truncated the broadest query to 100 of 150 matches."""
    requested: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        page = int(request.url.params["page"])
        requested.append(request.url.params["q"])
        size = 100 if page == 1 else 50
        return httpx.Response(
            200,
            json={
                "total_count": 150,
                "items": [
                    {
                        "full_name": f"org/tool{page}{index}",
                        "name": f"tool{page}{index}",
                        "description": None,
                        "html_url": "https://github.com/org/tool",
                        "stargazers_count": 1,
                        "language": "Python",
                    }
                    for index in range(size)
                ],
            },
        )

    client = httpx.Client(
        transport=httpx.MockTransport(handler), base_url="https://api.github.com"
    )
    result = GitHubClient(client=client).search_repositories("das")

    assert len(result.hits) == 150
    assert result.reported_total == 150
    assert result.truncated is False
    assert len(requested) == 2


def test_github_search_reports_the_cap_it_could_not_get_past() -> None:
    """GitHub serves at most 1000 hits, and a capped answer must say so."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "total_count": 2366,
                "items": [
                    {
                        "full_name": f"org/tool{index}",
                        "name": "tool",
                        "description": None,
                        "html_url": "https://github.com/org/tool",
                        "stargazers_count": 0,
                        "language": None,
                    }
                    for index in range(100)
                ],
            },
        )

    client = httpx.Client(
        transport=httpx.MockTransport(handler), base_url="https://api.github.com"
    )
    result = GitHubClient(client=client).search_repositories("das")

    assert result.reported_total == 2366
    assert result.truncated is True
    assert len(result.hits) < result.reported_total


def test_julia_registry_separates_unregistered_from_unreachable() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if "DASVader" in request.url.path:
            return httpx.Response(404)
        return httpx.Response(200, json={"type": "file", "name": "Package.toml"})

    client = httpx.Client(
        transport=httpx.MockTransport(handler), base_url="https://api.github.com"
    )
    registry = JuliaRegistryClient(client=client)

    assert registry.package("SeisIO")["registered"] is True
    with pytest.raises(NotFoundError):
        registry.package("DASVader")


def test_a_secondary_rate_limit_403_is_retried() -> None:
    """GitHub throttles search with 403, which is not a permission refusal."""
    client, calls = _counting_client(
        [
            httpx.Response(403, headers={"retry-after": "0"}),
            httpx.Response(200, json={"ok": True}),
        ]
    )
    source = JsonClient(base_url="https://example.com", client=client, backoff=0)

    assert source.get_json("/record") == {"ok": True}
    assert calls[0] == 2


def test_an_exhausted_rate_limit_budget_is_retried(monkeypatch) -> None:
    monkeypatch.setattr(base.time, "sleep", lambda _: None)
    client, calls = _counting_client(
        [
            httpx.Response(
                403,
                headers={"x-ratelimit-remaining": "0", "x-ratelimit-reset": "0"},
            ),
            httpx.Response(200, json={"ok": True}),
        ]
    )
    source = JsonClient(base_url="https://example.com", client=client)

    assert source.get_json("/record") == {"ok": True}
    assert calls[0] == 2


def test_a_plain_403_is_not_retried() -> None:
    """A permission refusal must fail once, not be hammered three times."""
    client, calls = _counting_client([httpx.Response(403)])
    source = JsonClient(base_url="https://example.com", client=client, backoff=0)

    with pytest.raises(SourceError):
        source.get_json("/record")
    assert calls[0] == 1
