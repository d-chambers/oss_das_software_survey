from __future__ import annotations

from oss_das.overlap import (
    capability_sets,
    cluster_layout,
    components,
    inverse_frequency,
    neighbour_edges,
    similarity,
    spring_layout,
)

# Every project claims "processing"; "visualization" is common, "compression"
# rarer, and "modeling"/"inversion" unique. a~b and c~g are each described
# identically, but only c~g agree on something rare.
SETS = {
    "a": frozenset({"io", "processing", "visualization"}),
    "b": frozenset({"io", "processing", "visualization"}),
    "h": frozenset({"processing", "visualization"}),
    "c": frozenset({"io", "processing", "compression"}),
    "g": frozenset({"io", "processing", "compression"}),
    "d": frozenset({"modeling", "processing", "inversion"}),
}


def test_a_universal_capability_carries_no_weight() -> None:
    """Everything claims processing, so sharing it is not evidence of anything."""
    weights = inverse_frequency(SETS)

    assert weights["processing"] == 0.0
    assert weights["inversion"] > weights["compression"] > weights["io"] > 0


def test_identical_descriptions_score_alike_but_differ_in_evidence() -> None:
    """The pair of numbers is the point: equal scores are not equal claims."""
    edges = {
        (left, right): (score, evidence)
        for left, right, score, evidence, _ in neighbour_edges(SETS)
    }

    assert edges[("a", "b")][0] == edges[("c", "g")][0] == 1.0
    assert edges[("c", "g")][1] > edges[("a", "b")][1]


def test_sharing_something_rare_outranks_sharing_something_common() -> None:
    edges = neighbour_edges(SETS)
    ranked = [(left, right) for left, right, _, _, _ in edges]

    # c~g agree on the rarer capability, so they outrank the a~b match.
    assert ranked.index(("c", "g")) < ranked.index(("a", "b"))


def test_unrelated_projects_are_not_joined() -> None:
    """Sharing only the universal tag must never be enough to draw an edge."""
    pairs = {(left, right) for left, right, _, _, _ in neighbour_edges(SETS)}

    assert ("a", "d") not in pairs


def test_capability_sets_ignore_absent_tags() -> None:
    records = [
        {"project_id": "a", "capability": "io", "present": "True"},
        {"project_id": "a", "capability": "modeling", "present": "False"},
        {"project_id": "z", "capability": "io", "present": "True"},
    ]
    assert capability_sets(records, ["a"]) == {"a": frozenset({"io"})}


def test_layout_is_identical_across_runs() -> None:
    """A random layout would redraw the same data differently every rebuild."""
    edges = [("a", "b", 1.0), ("b", "c", 0.5)]
    first = spring_layout(["a", "b", "c"], edges)
    second = spring_layout(["c", "b", "a"], edges)

    assert first == second
    assert len(first) == 3


def test_similarity_of_disjoint_sets_is_zero() -> None:
    weights = inverse_frequency(SETS)
    assert similarity(frozenset({"io"}), frozenset({"modeling"}), weights) == 0.0


def test_components_group_only_what_is_actually_connected() -> None:
    groups = components(["a", "b", "c", "d"], [("a", "b"), ("b", "c")])

    assert groups == [["a", "b", "c"], ["d"]]


def test_clusters_never_share_a_position() -> None:
    """Small multiples: one cluster must not be drawn on top of another."""
    layout = cluster_layout([["a", "b"], ["c", "d"], ["e", "f"]], columns=2)

    assert len(set(layout.values())) == 6
    assert layout == cluster_layout([["a", "b"], ["c", "d"], ["e", "f"]], columns=2)
