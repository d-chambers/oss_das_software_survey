"""Functional-overlap analysis over the curated capability tags.

Every number here is derived from hand-assigned tags, so this module measures
how the catalog *describes* software, not how the software behaves. That limit
is real enough to be worth stating twice: two projects joined by an edge below
have been described in similar words, which is a hypothesis about redundancy
rather than a demonstration of it.

The layout is deterministic on purpose. A random spring layout would redraw the
same dataset differently on every rebuild, which would make a figure impossible
to cite and a rebuild impossible to diff.
"""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from collections.abc import Iterable, Sequence
from typing import Any

#: Below this weighted-overlap score two projects are not called neighbours.
#: Chosen so that sharing only the universal tags is never enough on its own.
NEIGHBOUR_THRESHOLD = 0.34

#: A capability this common says almost nothing about what a project is for.
#: Reported so the page can name the hubs instead of hiding the heuristic.
UBIQUITY_SHARE = 0.35


def capability_sets(
    capabilities: Iterable[dict[str, str]], project_ids: Iterable[str]
) -> dict[str, frozenset[str]]:
    """Group present capability tags by project, restricted to ``project_ids``."""
    wanted = set(project_ids)
    grouped: dict[str, set[str]] = defaultdict(set)
    for record in capabilities:
        if record["project_id"] in wanted and str(record["present"]).lower() == "true":
            grouped[record["project_id"]].add(record["capability"])
    return {key: frozenset(value) for key, value in grouped.items() if value}


def inverse_frequency(sets: dict[str, frozenset[str]]) -> dict[str, float]:
    """Weight each capability by how little it narrows the field.

    Two thirds of this catalog claims ``processing``; three claim
    ``surface-waves``. Treating those as equal evidence of overlap would make
    every project look like every other project, so a shared tag is worth
    ``log(N / projects with the tag)`` — near zero for a universal tag, large
    for a rare one.
    """
    total = len(sets)
    counts = Counter(tag for tags in sets.values() for tag in tags)
    return {
        tag: math.log(total / count) if count < total else 0.0
        for tag, count in counts.items()
    }


def similarity(
    left: frozenset[str], right: frozenset[str], weights: dict[str, float]
) -> float:
    """Weighted Jaccard overlap of two capability sets, in ``[0, 1]``."""
    union = left | right
    if not union:
        return 0.0
    denominator = sum(weights.get(tag, 0.0) for tag in union)
    if denominator <= 0:
        return 0.0
    shared = sum(weights.get(tag, 0.0) for tag in left & right)
    return shared / denominator


def neighbour_edges(
    sets: dict[str, frozenset[str]], *, threshold: float = NEIGHBOUR_THRESHOLD
) -> list[tuple[str, str, float, float, frozenset[str]]]:
    """Pairs whose descriptions overlap enough to be worth a second look.

    Each pair carries two numbers, because one is not enough. ``score`` is how
    identically the two are described; ``evidence`` is how much that agreement
    is worth, summed over the rarity of the tags they actually share. Two
    projects described only as "io, processing, visualization" score a perfect
    1.0 while carrying almost no evidence — and conflating those with a pair
    that agrees on something rare would turn the vaguest entries in the catalog
    into its strongest claims.
    """
    weights = inverse_frequency(sets)
    keys = sorted(sets)
    edges = []
    for index, left in enumerate(keys):
        for right in keys[index + 1 :]:
            score = similarity(sets[left], sets[right], weights)
            if score >= threshold:
                shared = sets[left] & sets[right]
                evidence = sum(weights.get(tag, 0.0) for tag in shared)
                edges.append((left, right, score, evidence, shared))
    return sorted(edges, key=lambda item: (-item[3], -item[2], item[0], item[1]))


def ubiquitous(
    sets: dict[str, frozenset[str]], *, share: float = UBIQUITY_SHARE
) -> list[str]:
    """Capabilities so widely claimed they cannot distinguish two projects."""
    counts = Counter(tag for tags in sets.values() for tag in tags)
    limit = share * len(sets)
    return sorted(tag for tag, count in counts.items() if count >= limit)


def capability_counts(sets: dict[str, frozenset[str]]) -> list[tuple[str, int]]:
    """Every capability with how many projects claim it, rarest last."""
    counts = Counter(tag for tags in sets.values() for tag in tags)
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))


def _initial_positions(nodes: Sequence[str]) -> dict[str, list[float]]:
    """Seed a layout without a random number generator.

    A golden-angle spiral spreads nodes evenly and depends only on sorted
    order, so the same catalog always produces the same picture.
    """
    golden = math.pi * (3.0 - math.sqrt(5.0))
    positions = {}
    for index, node in enumerate(nodes):
        radius = math.sqrt((index + 0.5) / len(nodes))
        angle = index * golden
        positions[node] = [radius * math.cos(angle), radius * math.sin(angle)]
    return positions


def spring_layout(
    nodes: Sequence[str],
    edges: Iterable[tuple[str, str, float]],
    *,
    iterations: int = 260,
    gravity: float = 0.012,
) -> dict[str, tuple[float, float]]:
    """Force-directed layout: repulsion everywhere, attraction along edges.

    A plain Fruchterman-Reingold step with linear cooling. It is written out
    rather than imported because the project carries no numerical dependency,
    and because a hand-rolled loop can be made deterministic where a library
    default usually is not.
    """
    nodes = sorted(nodes)
    if not nodes:
        return {}
    positions = _initial_positions(nodes)
    weighted = [(a, b, w) for a, b, w in edges if a in positions and b in positions]
    optimal = math.sqrt(1.0 / len(nodes))
    temperature = 0.12
    cooling = temperature / (iterations + 1)

    for _ in range(iterations):
        forces = {node: [0.0, 0.0] for node in nodes}
        for index, left in enumerate(nodes):
            lx, ly = positions[left]
            for right in nodes[index + 1 :]:
                rx, ry = positions[right]
                dx, dy = lx - rx, ly - ry
                distance = math.hypot(dx, dy) or 1e-6
                push = (optimal * optimal) / distance
                ux, uy = dx / distance, dy / distance
                forces[left][0] += ux * push
                forces[left][1] += uy * push
                forces[right][0] -= ux * push
                forces[right][1] -= uy * push
        for left, right, weight in weighted:
            lx, ly = positions[left]
            rx, ry = positions[right]
            dx, dy = lx - rx, ly - ry
            distance = math.hypot(dx, dy) or 1e-6
            pull = (distance * distance) / optimal * weight
            ux, uy = dx / distance, dy / distance
            forces[left][0] -= ux * pull
            forces[left][1] -= uy * pull
            forces[right][0] += ux * pull
            forces[right][1] += uy * pull
        for node in nodes:
            fx, fy = forces[node]
            # Pull gently toward the origin so disconnected nodes drift to the
            # margin instead of being flung off the plot entirely.
            fx -= positions[node][0] * gravity / optimal
            fy -= positions[node][1] * gravity / optimal
            magnitude = math.hypot(fx, fy) or 1e-6
            step = min(magnitude, temperature)
            positions[node][0] += fx / magnitude * step
            positions[node][1] += fy / magnitude * step
        temperature -= cooling

    return {node: (round(x, 6), round(y, 6)) for node, (x, y) in positions.items()}


def bipartite_graph(
    sets: dict[str, frozenset[str]],
) -> tuple[dict[str, tuple[float, float]], list[tuple[str, str]]]:
    """Lay out projects and capabilities together as a two-mode network.

    Drawing both kinds of node in one space is what makes the shape of the
    ecosystem visible: a capability with many projects becomes a hub, and a
    project that sits between hubs is doing something less common.
    """
    edges = [
        (project, f"cap:{tag}")
        for project, tags in sets.items()
        for tag in sorted(tags)
    ]
    nodes = sorted({project for project, _ in edges} | {tag for _, tag in edges})
    # Pull hard toward rare capabilities and barely at all toward ubiquitous
    # ones. Weighting every edge equally lets the three tags most of the
    # catalog claims drag every project into one unreadable knot at the centre,
    # which is also the least informative thing the picture could say.
    weights = inverse_frequency(sets)
    ceiling = max(weights.values(), default=1.0) or 1.0
    weighted = [
        (
            project,
            tag,
            0.06 + 0.94 * weights.get(tag.removeprefix("cap:"), 0.0) / ceiling,
        )
        for project, tag in edges
    ]
    layout = spring_layout(nodes, weighted)
    return layout, sorted(edges)


def co_occurrence(sets: dict[str, frozenset[str]]) -> dict[tuple[str, str], int]:
    """How often each capability pair is claimed by the same project."""
    pairs: Counter[tuple[str, str]] = Counter()
    for tags in sets.values():
        ordered = sorted(tags)
        for index, left in enumerate(ordered):
            for right in ordered[index + 1 :]:
                pairs[(left, right)] += 1
    return dict(pairs)


def summarize(sets: dict[str, frozenset[str]], names: dict[str, str]) -> dict[str, Any]:
    """Headline findings the page quotes, computed once so they cannot drift."""
    counts = capability_counts(sets)
    edges = neighbour_edges(sets)
    degree: Counter[str] = Counter()
    for left, right, _, _, _ in edges:
        degree[left] += 1
        degree[right] += 1
    return {
        "projects": len(sets),
        "capabilities": len(counts),
        "sole_implementations": [tag for tag, count in counts if count == 1],
        "ubiquitous": ubiquitous(sets),
        "pairs": len(edges),
        "closest": [
            {
                "left": names.get(left, left),
                "right": names.get(right, right),
                "score": score,
                "evidence": evidence,
                "shared": sorted(shared),
            }
            for left, right, score, evidence, shared in edges[:12]
        ],
        "isolated": sorted(names.get(key, key) for key in sets if degree[key] == 0),
        "most_connected": [
            (names.get(key, key), count) for key, count in degree.most_common(5)
        ],
    }


def components(
    nodes: Iterable[str], edges: Iterable[tuple[str, str]]
) -> list[list[str]]:
    """Group nodes into connected clusters, largest first.

    The overlap backbone is not one graph but a scatter of small cliques, and
    a force-directed layout renders that shape badly: the cliques collapse to
    a point while unconnected nodes fill the canvas around them.
    """
    adjacency: dict[str, set[str]] = {node: set() for node in nodes}
    for left, right in edges:
        if left in adjacency and right in adjacency:
            adjacency[left].add(right)
            adjacency[right].add(left)
    seen: set[str] = set()
    found = []
    for node in sorted(adjacency):
        if node in seen:
            continue
        stack, group = [node], []
        seen.add(node)
        while stack:
            current = stack.pop()
            group.append(current)
            for neighbour in sorted(adjacency[current]):
                if neighbour not in seen:
                    seen.add(neighbour)
                    stack.append(neighbour)
        found.append(sorted(group))
    return sorted(found, key=lambda group: (-len(group), group[0]))


def cluster_layout(
    groups: Sequence[Sequence[str]], *, columns: int = 4, spacing: float = 2.8
) -> dict[str, tuple[float, float]]:
    """Place each cluster on its own small ring, clusters arranged in a grid.

    Small multiples rather than one crowded space: every cluster gets room
    proportional to its size, and no cluster can be pushed on top of another.
    """
    layout: dict[str, tuple[float, float]] = {}
    for index, group in enumerate(groups):
        cx = (index % columns) * spacing
        cy = -(index // columns) * spacing
        if len(group) == 1:
            layout[group[0]] = (cx, cy)
            continue
        radius = 0.42 + 0.1 * len(group)
        for position, node in enumerate(group):
            angle = 2 * math.pi * position / len(group) - math.pi / 2
            layout[node] = (
                round(cx + radius * math.cos(angle), 6),
                round(cy + radius * math.sin(angle), 6),
            )
    return layout
