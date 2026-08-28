"""Dependency relationships derived from published package metadata."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable


def catalog_edges(
    dependencies: Iterable[dict[str, str]], project_ids: Iterable[str]
) -> list[tuple[str, str]]:
    """Return direct observed edges whose two endpoints are catalogued projects."""
    included = set(project_ids)
    return sorted(
        {
            (item["project_id"], item["dependency_project_id"])
            for item in dependencies
            if item["project_id"] in included
            and item.get("dependency_project_id") in included
        }
    )


def shared_external_dependencies(
    dependencies: Iterable[dict[str, str]], project_ids: Iterable[str]
) -> dict[str, int]:
    """Count non-catalogued requirements shared by two or more projects."""
    included = set(project_ids)
    projects_by_dependency: dict[str, set[str]] = {}
    for item in dependencies:
        if item["project_id"] not in included or item.get("dependency_project_id"):
            continue
        projects_by_dependency.setdefault(item["dependency"], set()).add(
            item["project_id"]
        )
    return {
        dependency: len(projects)
        for dependency, projects in projects_by_dependency.items()
        if len(projects) >= 2
    }


def incoming_counts(edges: Iterable[tuple[str, str]]) -> Counter[str]:
    """Count catalogued projects with a direct dependent in the catalog."""
    return Counter(target for _, target in edges)
