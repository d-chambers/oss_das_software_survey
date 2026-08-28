from oss_das.dependencies import (
    catalog_edges,
    incoming_counts,
    shared_external_dependencies,
)

DEPENDENCIES = [
    {"project_id": "a", "dependency": "numpy", "dependency_project_id": ""},
    {"project_id": "b", "dependency": "numpy", "dependency_project_id": ""},
    {"project_id": "a", "dependency": "c", "dependency_project_id": "c"},
    {"project_id": "outsider", "dependency": "c", "dependency_project_id": "c"},
]


def test_catalog_edges_are_direct_and_restricted_to_requested_projects() -> None:
    assert catalog_edges(DEPENDENCIES, {"a", "b", "c"}) == [("a", "c")]


def test_shared_external_dependencies_count_distinct_projects() -> None:
    assert shared_external_dependencies(DEPENDENCIES, {"a", "b", "c"}) == {"numpy": 2}


def test_incoming_counts_measure_catalogued_dependents() -> None:
    assert incoming_counts([("a", "c"), ("b", "c")]) == {"c": 2}
