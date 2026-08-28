#!/usr/bin/env python3
"""Build the direct-package-dependency and in-catalog impact page."""

from __future__ import annotations

import html
import math

import plotly.graph_objects as go

from oss_das.cli import resolve_snapshot_date, snapshot_parser
from oss_das.dependencies import (
    catalog_edges,
    incoming_counts,
    shared_external_dependencies,
)
from oss_das.overlap import spring_layout
from oss_das.site import load_plot_data, render_page

PROJECT_HUE = "#2a78d6"
DEPENDENCY_HUE = "#eb6834"
EDGE_INK = "rgba(19,41,61,0.22)"


def _edge_trace(layout, edges) -> go.Scatter:
    x: list[float | None] = []
    y: list[float | None] = []
    for source, target in edges:
        x.extend([layout[source][0], layout[target][0], None])
        y.extend([layout[source][1], layout[target][1], None])
    return go.Scatter(
        x=x,
        y=y,
        mode="lines",
        line={"color": EDGE_INK, "width": 1.4},
        hoverinfo="skip",
        showlegend=False,
    )


def dependency_map(data: dict) -> go.Figure:
    projects = [item for item in data["projects"] if item["status"] == "included"]
    names = {item["id"]: item["name"] for item in projects}
    project_ids = set(names)
    internal = catalog_edges(data["dependencies"], project_ids)
    shared = shared_external_dependencies(data["dependencies"], project_ids)
    external_edges = sorted(
        {
            (item["project_id"], f"dep:{item['dependency']}")
            for item in data["dependencies"]
            if item["project_id"] in project_ids
            and item["dependency"] in shared
            and not item["dependency_project_id"]
        }
    )
    edges = internal + external_edges
    nodes = sorted({node for edge in edges for node in edge})
    layout = spring_layout(nodes, [(left, right, 1.0) for left, right in edges])
    incoming = incoming_counts(internal)
    figure = go.Figure(_edge_trace(layout, edges))
    project_nodes = sorted(node for node in nodes if not node.startswith("dep:"))
    external_nodes = sorted(node for node in nodes if node.startswith("dep:"))
    figure.add_trace(
        go.Scatter(
            x=[layout[node][0] for node in project_nodes],
            y=[layout[node][1] for node in project_nodes],
            mode="markers+text",
            name="Catalog project",
            marker={
                "size": [12 + 4 * incoming[node] for node in project_nodes],
                "color": PROJECT_HUE,
                "line": {"color": "white", "width": 2},
            },
            text=[names[node] for node in project_nodes],
            textposition="middle right",
            customdata=[incoming[node] for node in project_nodes],
            hovertemplate="<b>%{text}</b><br>%{customdata} catalogued dependents<extra></extra>",
        )
    )
    figure.add_trace(
        go.Scatter(
            x=[layout[node][0] for node in external_nodes],
            y=[layout[node][1] for node in external_nodes],
            mode="markers+text",
            name="Shared external dependency",
            marker={
                "size": [
                    11 + 3 * math.sqrt(shared[node.removeprefix("dep:")])
                    for node in external_nodes
                ],
                "color": DEPENDENCY_HUE,
                "symbol": "diamond",
                "line": {"color": "white", "width": 2},
            },
            text=[node.removeprefix("dep:") for node in external_nodes],
            textposition="top center",
            customdata=[shared[node.removeprefix("dep:")] for node in external_nodes],
            hovertemplate="<b>%{text}</b><br>%{customdata} catalogued projects depend on it<extra></extra>",
        )
    )
    figure.update_layout(
        title="Direct package relationships<br><sup>Arrows are omitted: each line joins a project to a package it declares as a runtime requirement.</sup>",
        height=760,
        legend={"orientation": "h", "y": 1.02, "x": 0},
        xaxis={"visible": False},
        yaxis={"visible": False, "scaleanchor": "x", "scaleratio": 1},
        plot_bgcolor="white",
    )
    return figure


def shared_dependency_figure(data: dict) -> go.Figure:
    project_ids = {
        item["id"] for item in data["projects"] if item["status"] == "included"
    }
    shared = shared_external_dependencies(data["dependencies"], project_ids)
    ranked = sorted(shared.items(), key=lambda item: (-item[1], item[0]))
    figure = go.Figure(
        go.Bar(
            x=[count for _, count in ranked],
            y=[name for name, _ in ranked],
            orientation="h",
            text=[count for _, count in ranked],
        )
    )
    figure.update_layout(
        title="Shared external foundations",
        xaxis_title="Included projects declaring the dependency",
        yaxis={"autorange": "reversed"},
        height=max(420, 24 * len(ranked) + 160),
    )
    return figure


def main() -> None:
    args = snapshot_parser(__doc__).parse_args()
    snapshot_date = resolve_snapshot_date(args.snapshot_date, prefer_latest=True)
    data = load_plot_data(snapshot_date)
    project_ids = {
        item["id"] for item in data["projects"] if item["status"] == "included"
    }
    internal = catalog_edges(data["dependencies"], project_ids)
    incoming = incoming_counts(internal)
    names = {item["id"]: item["name"] for item in data["projects"]}
    ranked = sorted(incoming.items(), key=lambda item: (-item[1], names[item[0]]))
    rows = (
        "".join(
            f"<tr><td>{html.escape(names[project_id])}</td><td>{count}</td></tr>"
            for project_id, count in ranked
        )
        or "<tr><td colspan='2'>No direct in-catalog package requirements observed.</td></tr>"
    )
    body = f"""
    <section class="cards">
      <div class="card"><strong>{len(internal)}</strong>direct in-catalog edges</div>
      <div class="card"><strong>{sum(bool(value) for value in incoming.values())}</strong>projects with an in-catalog dependent</div>
    </section>
    <p class="note">This is a direct dependency view, not a popularity ranking or a complete software bill of materials. It uses PyPI <code>requires_dist</code> metadata for catalogued Python distributions, excludes optional extras, and leaves projects without observed PyPI metadata unconnected rather than assuming they have no dependencies.</p>
    <h2>Catalogued downstream dependents</h2>
    <div class="table-wrap"><table><thead><tr><th>Dependency project</th><th>Direct catalogued dependents</th></tr></thead><tbody>{rows}</tbody></table></div>
    """
    render_page(
        "dependencies.html",
        title="Dependency impact",
        heading="Impact flows through declared dependencies",
        lede="Direct package requirements reveal shared foundations and the catalogued projects that rely on one another.",
        snapshot_date=snapshot_date,
        figures=[dependency_map(data), shared_dependency_figure(data)],
        body=body,
    )


if __name__ == "__main__":
    main()
