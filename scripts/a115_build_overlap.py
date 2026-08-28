#!/usr/bin/env python3
"""Build the functional-overlap page: who does the same things as whom."""

from __future__ import annotations

import html
import math

import plotly.graph_objects as go

from oss_das.cli import resolve_snapshot_date, snapshot_parser
from oss_das.overlap import (
    bipartite_graph,
    capability_counts,
    capability_sets,
    cluster_layout,
    components,
    neighbour_edges,
    summarize,
)
from oss_das.site import load_plot_data, render_page

#: Two validated categorical hues. A network is an all-pairs form, so the
#: palette caps well below the number of primary categories; position and
#: labels carry the rest of the meaning instead of more colour.
PROJECT_HUE = "#2a78d6"
CAPABILITY_HUE = "#eb6834"
EDGE_INK = "rgba(19,41,61,0.16)"
MUTED = "#5f6b76"

#: Evidence below this is agreement on capabilities most of the catalog
#: claims, which is not worth an edge in a sixty-three node graph.
BACKBONE_EVIDENCE = 4.6


def _edge_trace(
    layout: dict[str, tuple[float, float]],
    edges: list[tuple[str, str]],
    *,
    width: float = 1.0,
    color: str = EDGE_INK,
    name: str | None = None,
) -> go.Scatter:
    """Draw many edges as one trace, separated by None breaks."""
    x: list[float | None] = []
    y: list[float | None] = []
    for left, right in edges:
        if left not in layout or right not in layout:
            continue
        x.extend([layout[left][0], layout[right][0], None])
        y.extend([layout[left][1], layout[right][1], None])
    return go.Scatter(
        x=x,
        y=y,
        mode="lines",
        line={"width": width, "color": color},
        hoverinfo="skip",
        showlegend=name is not None,
        name=name or "",
    )


def _blank_axes(figure: go.Figure, height: int) -> None:
    axis = {
        "showgrid": False,
        "zeroline": False,
        "showticklabels": False,
        "visible": False,
    }
    figure.update_layout(
        xaxis=axis,
        yaxis={**axis, "scaleanchor": "x", "scaleratio": 1},
        height=height,
        hovermode="closest",
        plot_bgcolor="white",
    )


def capability_map(sets, names) -> go.Figure:
    """Projects and capabilities in one space, so the shape is visible."""
    layout, edges = bipartite_graph(sets)
    counts = dict(capability_counts(sets))
    figure = go.Figure()
    figure.add_trace(_edge_trace(layout, edges, width=0.7))

    cap_keys = sorted(counts)
    figure.add_trace(
        go.Scatter(
            x=[layout[f"cap:{key}"][0] for key in cap_keys],
            y=[layout[f"cap:{key}"][1] for key in cap_keys],
            mode="markers+text",
            name="Capability",
            marker={
                "size": [11 + 6.5 * math.sqrt(counts[key]) for key in cap_keys],
                "color": CAPABILITY_HUE,
                "symbol": "diamond",
                "line": {"width": 2, "color": "white"},
            },
            text=cap_keys,
            textposition=[
                "top center" if index % 2 == 0 else "bottom center"
                for index, _ in enumerate(cap_keys)
            ],
            textfont={"size": 11, "color": "#13293d"},
            customdata=[counts[key] for key in cap_keys],
            hovertemplate="<b>%{text}</b><br>%{customdata} projects<extra></extra>",
        )
    )
    project_keys = sorted(sets)
    figure.add_trace(
        go.Scatter(
            x=[layout[key][0] for key in project_keys],
            y=[layout[key][1] for key in project_keys],
            mode="markers",
            name="Project",
            marker={
                "size": 11,
                "color": PROJECT_HUE,
                "line": {"width": 2, "color": "white"},
            },
            text=[names[key] for key in project_keys],
            customdata=[", ".join(sorted(sets[key])) for key in project_keys],
            hovertemplate="<b>%{text}</b><br>%{customdata}<extra></extra>",
        )
    )

    figure.update_layout(
        title="Capability map<br><sup>Included projects joined to the capabilities they claim; "
        "diamond size is how many projects claim each one</sup>",
        legend={"orientation": "h", "y": 1.02, "x": 0},
    )
    _blank_axes(figure, 760)
    return figure


def neighbour_map(sets, names) -> go.Figure:
    """The backbone, drawn as small multiples of each overlap cluster.

    Only pairs agreeing on capabilities rare enough to matter get an edge, and
    the clusters those edges form are laid out separately. A single force
    layout collapsed each clique to a point and filled the rest of the canvas
    with unconnected nodes, which showed the data less clearly than nothing.
    """
    edges = [item for item in neighbour_edges(sets) if item[3] >= BACKBONE_EVIDENCE]
    pairs = [(left, right) for left, right, _, _, _ in edges]
    joined = sorted({node for pair in pairs for node in pair})
    groups = [group for group in components(joined, pairs) if len(group) > 1]
    layout = cluster_layout(groups)

    degree: dict[str, int] = {key: 0 for key in joined}
    for left, right in pairs:
        degree[left] += 1
        degree[right] += 1

    figure = go.Figure()
    for low, high, width in ((0.0, 6.0, 1.2), (6.0, 7.5, 2.4), (7.5, 99.0, 3.6)):
        band = [(a, b) for a, b, _, ev, _ in edges if low <= ev < high]
        if band:
            figure.add_trace(_edge_trace(layout, band, width=width, color=EDGE_INK))

    figure.add_trace(
        go.Scatter(
            x=[layout[key][0] for key in joined],
            y=[layout[key][1] for key in joined],
            mode="markers+text",
            marker={
                "size": [11 + 2.4 * degree[key] for key in joined],
                "color": PROJECT_HUE,
                "line": {"width": 2, "color": "white"},
            },
            text=[names[key] for key in joined],
            textposition="middle right",
            textfont={"size": 11, "color": "#13293d"},
            customdata=[(degree[key], ", ".join(sorted(sets[key]))) for key in joined],
            hovertemplate=(
                "<b>%{text}</b><br>%{customdata[0]} strong neighbours"
                "<br>%{customdata[1]}<extra></extra>"
            ),
            showlegend=False,
        )
    )
    figure.update_layout(
        title="Functional backbone<br><sup>Clusters of projects that agree on capabilities rare "
        "enough to matter; thicker edges agree on rarer ones. Projects with no such "
        "neighbour are not drawn</sup>"
    )
    _blank_axes(figure, 700)
    figure.update_xaxes(range=[-1.3, 9.6])
    return figure


def crowding(sets) -> go.Figure:
    """Where the field is thick and where one project is holding a capability."""
    counts = capability_counts(sets)
    labels = [tag for tag, _ in counts][::-1]
    values = [count for _, count in counts][::-1]
    shade = ["#cde2fb", "#9ec5f4", "#5598e7", "#2a78d6", "#184f95"]
    colors = [
        shade[min(len(shade) - 1, int(value / max(values) * len(shade)))]
        for value in values
    ]
    figure = go.Figure(
        go.Bar(
            x=values,
            y=labels,
            orientation="h",
            marker={"color": colors},
            text=values,
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>%{x} projects<extra></extra>",
        )
    )
    figure.update_layout(
        title="Crowding and thin ice<br><sup>Projects claiming each capability. "
        "A bar of one is a capability the ecosystem holds in a single pair of hands</sup>",
        xaxis_title="Included projects",
        height=max(460, 22 * len(labels) + 170),
        bargap=0.3,
        plot_bgcolor="white",
    )
    return figure


def pairs_table(summary: dict) -> str:
    rows = "".join(
        "<tr>"
        f"<td>{html.escape(item['left'])} &middot; {html.escape(item['right'])}</td>"
        f"<td>{item['evidence']:.1f}</td>"
        f"<td>{item['score']:.2f}</td>"
        f"<td>{html.escape(', '.join(item['shared']))}</td>"
        "</tr>"
        for item in summary["closest"]
    )
    return (
        "<h2>The closest pairs</h2>"
        "<p>Ranked by evidence — the combined rarity of what the two projects "
        "agree on — rather than by the raw score, because two projects described "
        "only as “io, processing, visualization” match perfectly while telling "
        "you almost nothing.</p>"
        "<div class='table-wrap'><table><thead><tr>"
        "<th>Pair</th><th>Evidence</th><th>Score</th><th>Shared capabilities</th>"
        "</tr></thead><tbody>" + rows + "</tbody></table></div>"
    )


def main() -> None:
    args = snapshot_parser(__doc__).parse_args()
    snapshot_date = resolve_snapshot_date(args.snapshot_date, prefer_latest=True)
    data = load_plot_data(snapshot_date)
    included = [item for item in data["projects"] if item["status"] == "included"]
    names = {item["id"]: item["name"] for item in included}
    sets = capability_sets(data["capabilities"], names)
    summary = summarize(sets, names)

    sole = ", ".join(summary["sole_implementations"])
    hubs = ", ".join(summary["ubiquitous"])
    body = f"""
    <section class="cards">
      <div class="card"><strong>{summary["pairs"]}</strong>overlapping pairs</div>
      <div class="card"><strong>{len(summary["sole_implementations"])}</strong>capabilities with one implementation</div>
      <div class="card"><strong>{len(summary["isolated"])}</strong>projects with no close neighbour</div>
      <div class="card"><strong>{summary["capabilities"]}</strong>distinct capabilities</div>
    </section>
    <p class="note">These figures describe the <em>curated tags</em>, not the code. An edge
    says two projects were described in similar words by a human reviewer, which is a
    hypothesis about redundancy rather than a demonstration of one — the tags are intent,
    not measured behaviour. Three capabilities ({html.escape(hubs)}) are claimed by more than
    a third of the catalog, so agreeing on them is treated as weak evidence and weighted
    down accordingly.</p>
    <p>Read the map for two things it makes visible at a glance. Dense knots are places
    where several projects have been built to do the same job. The single-project
    capabilities — {html.escape(sole)} — are the opposite: the ecosystem depends on one
    codebase for each, and loses the capability entirely if that codebase is abandoned.</p>
    {pairs_table(summary)}
    """
    render_page(
        "overlap.html",
        title="Overlap",
        heading="Who does the same things as whom",
        lede=(
            "The same capability implemented five times is not automatically waste, "
            "and a capability implemented once is not automatically safe. This page "
            "shows where the work piles up and where it runs thin."
        ),
        snapshot_date=snapshot_date,
        figures=[
            capability_map(sets, names),
            neighbour_map(sets, names),
            crowding(sets),
        ],
        body=body,
    )


if __name__ == "__main__":
    main()
