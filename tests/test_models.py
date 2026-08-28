from __future__ import annotations

import pytest
from pydantic import ValidationError

from oss_das.models import MetricObservation, ProjectRecord


def test_project_normalizes_and_sorts_capabilities() -> None:
    project = ProjectRecord.model_validate(
        {
            "id": "example",
            "name": "Example",
            "repository": "owner/repo",
            "description": "A reusable DAS tool.",
            "status": "included",
            "decision_reason": "Meets the policy.",
            "primary_category": "processing",
            "capabilities": ["io", "processing", "io"],
            "publications": [
                {"doi": "https://doi.org/10.1234/ABC", "role": "canonical"}
            ],
        }
    )
    assert project.capabilities == ["io", "processing"]
    assert project.publications[0].doi == "10.1234/abc"


def test_project_rejects_multiple_canonical_publications() -> None:
    with pytest.raises(ValidationError, match="at most one canonical"):
        ProjectRecord.model_validate(
            {
                "id": "example",
                "name": "Example",
                "repository": "owner/repo",
                "description": "A reusable DAS tool.",
                "status": "included",
                "decision_reason": "Meets the policy.",
                "primary_category": "processing",
                "publications": [
                    {"doi": "10.1234/one", "role": "canonical"},
                    {"doi": "10.1234/two", "role": "canonical"},
                ],
            }
        )


def test_metric_requires_value_or_missing_reason() -> None:
    base = {
        "project_id": "example",
        "metric": "repo_stars",
        "unit": "stars",
        "source_url": "https://example.com",
        "fetched_at": "2026-08-03T00:00:00+00:00",
    }
    assert MetricObservation(**base, value=0).value == 0
    assert MetricObservation(**base, missing_reason="unavailable").value is None
    with pytest.raises(ValidationError, match="exactly one"):
        MetricObservation(**base)


def _project(**overrides):
    base = {
        "id": "example",
        "name": "Example",
        "repository": "owner/repo",
        "description": "A reusable DAS tool.",
        "status": "included",
        "decision_reason": "Meets the policy.",
        "primary_category": "processing",
    }
    return ProjectRecord.model_validate(base | overrides)


def test_an_unlicensed_project_is_catalogued_rather_than_rejected() -> None:
    """Licensing is measured here, so no license is a finding, not a filter."""
    project = _project(license_class="unlicensed")

    assert project.status.value == "included"
    assert project.license_spdx is None


def test_an_unlicensed_project_may_not_also_claim_an_spdx_id() -> None:
    with pytest.raises(ValidationError, match="must not carry an SPDX id"):
        _project(license_class="unlicensed", license_spdx="MIT")


def test_a_classified_license_must_name_the_license_it_classifies() -> None:
    with pytest.raises(ValidationError, match="requires a license_spdx"):
        _project(license_class="osi-approved")


def test_a_gitlab_project_builds_its_url_from_its_own_host() -> None:
    project = _project(
        repository="geofon/dastools",
        license_class="osi-approved",
        license_spdx="GPL-3.0-or-later",
        forge={"kind": "gitlab", "host": "git.gfz-potsdam.de"},
    )

    assert project.repository_url == "https://git.gfz-potsdam.de/geofon/dastools"
    assert project.forge_key == "git.gfz-potsdam.de/geofon/dastools"


def test_a_nested_gitlab_group_path_is_accepted() -> None:
    """GitHub paths have two parts; GitLab subgroups can have more."""
    project = _project(repository="group/subgroup/tool", license_class="unlicensed")

    assert project.repository == "group/subgroup/tool"


def test_a_forge_host_must_be_a_bare_hostname() -> None:
    with pytest.raises(ValidationError, match="bare hostname"):
        _project(
            license_class="unlicensed",
            forge={"kind": "gitlab", "host": "https://x.org"},
        )


def test_owner_is_the_top_level_namespace_on_any_host() -> None:
    """Concentration by publisher is only countable if the owner is recorded."""
    assert _project(repository="DASDAE/derzug", license_class="unlicensed").owner == (
        "DASDAE"
    )
    nested = _project(repository="group/subgroup/tool", license_class="unlicensed")
    assert nested.owner == "group"
