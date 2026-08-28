"""Shared Plotly figures, HTML layout, and static-site output helpers."""

from __future__ import annotations

import html
import shutil
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import plotly.graph_objects as go
from jinja2 import BaseLoader, Environment, select_autoescape
from plotly.io import to_html

from oss_das.core import PATHS, load_projects, read_csv, read_frontmatter, read_json
from oss_das.utils import days_between

NAVIGATION = (
    ("Overview", "index.html"),
    ("Landscape", "landscape.html"),
    ("Overlap", "overlap.html"),
    ("Adoption", "adoption.html"),
    ("Health", "health.html"),
    ("Dependencies", "dependencies.html"),
    ("Catalog", "catalog.html"),
    ("Methodology", "methodology.html"),
)

PAGE_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{ title }} · Open-source DAS ecosystem</title>
  <style>
    :root { --ink: #13293d; --muted: #5f6b76; --accent: #087e8b; --paper: #f7f9fb; --line: #d9e2e8; }
    * { box-sizing: border-box; }
    body { margin: 0; color: var(--ink); background: var(--paper); font: 16px/1.55 system-ui, sans-serif; }
    header, main, footer { max-width: 1180px; margin: auto; padding: 1.2rem 1.5rem; }
    header { display: flex; gap: 1.5rem; align-items: baseline; flex-wrap: wrap; border-bottom: 1px solid var(--line); }
    header a { color: var(--ink); text-decoration: none; margin-right: 1rem; }
    header a:hover, a { color: var(--accent); }
    h1 { font-size: clamp(2rem, 6vw, 4.2rem); line-height: 1.03; margin: 2rem 0 1rem; max-width: 900px; }
    h2 { margin-top: 2.5rem; }
    .lede { color: var(--muted); font-size: 1.18rem; max-width: 850px; }
    .meta, .note { color: var(--muted); }
    .note { border-left: 4px solid var(--accent); padding: .7rem 1rem; background: white; }
    .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin: 2rem 0; }
    .card { background: white; padding: 1rem 1.2rem; border: 1px solid var(--line); border-radius: 8px; }
    .card strong { display: block; font-size: 2rem; }
    .plot { background: white; border: 1px solid var(--line); border-radius: 8px; margin: 1.5rem 0; overflow: hidden; }
    table { width: 100%; border-collapse: collapse; background: white; font-size: .92rem; }
    th, td { padding: .65rem; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }
    th { position: sticky; top: 0; background: #eaf0f3; }
    .table-wrap { max-height: 72vh; overflow: auto; border: 1px solid var(--line); }
    input, select { padding: .65rem; margin: .3rem .5rem .8rem 0; border: 1px solid #9aaab5; border-radius: 4px; min-width: 220px; }
    footer { color: var(--muted); border-top: 1px solid var(--line); margin-top: 3rem; }
    code { background: #eaf0f3; padding: .1rem .25rem; }
    @media (max-width: 650px) { header { display: block; } th, td { min-width: 120px; } }
  </style>
</head>
<body>
<header><strong>Open-source DAS ecosystem</strong><nav>{% for label, link in navigation %}<a href="{{ link }}">{{ label }}</a>{% endfor %}</nav></header>
<main>
  <h1>{{ heading }}</h1>
  <p class="lede">{{ lede }}</p>
  <p class="meta">Snapshot: {{ snapshot_date }}</p>
  {{ content | safe }}
</main>
<footer>Faceted evidence, not a league table. Missing values are not zeros. <a href="methodology.html">Read the methodology</a>.</footer>
</body>
</html>
"""


def load_site_data(snapshot_date: str) -> dict[str, Any]:
    """Load the normalized snapshot used by the catalog and public downloads."""
    snapshot = PATHS.snapshot(snapshot_date)
    return {
        "projects": read_csv(snapshot / "projects.csv"),
        "metrics": read_csv(snapshot / "metrics.csv"),
        "publications": read_csv(snapshot / "publications.csv"),
        "capabilities": read_csv(snapshot / "capabilities.csv"),
        "pypi_daily": read_csv(snapshot / "pypi_daily.csv"),
        "dependencies": read_csv(snapshot / "dependencies.csv"),
        "manifest": read_json(snapshot / "manifest.json"),
    }


def load_plot_data(snapshot_date: str) -> dict[str, Any]:
    """Build the plotting view from the per-project source records.

    Project files are the current, human-readable source for curation and the
    newest collection pass.  The CSV snapshot remains the historical export,
    but charts should not need a parallel flattened representation of the
    same facts.  Refuse to combine a requested snapshot date with project
    files produced from another scan: doing so would make the page label lie.
    """
    projects = []
    metrics = []
    publications = []
    capabilities = []
    dependencies = []
    metric_fields = {
        "stars": ("repo_stars", "stars"),
        "forks": ("repo_forks", "forks"),
        "contributors": ("repo_contributors", "contributors"),
        "releases": ("repo_releases", "releases"),
        "pypi_downloads_30d": ("pypi_downloads_30d", "downloads"),
        "pypi_downloads_180d": ("pypi_downloads_180d", "downloads"),
        "conda_downloads_total": ("conda_downloads_cumulative", "downloads"),
        "canonical_citations": ("canonical_citations", "citations"),
    }

    for project in load_projects():
        document = read_frontmatter(PATHS.curated / f"{project.id}.md")
        collected = document.get("collected", {})
        collected_snapshot = collected.get("snapshot")
        if collected_snapshot != snapshot_date:
            raise ValueError(
                f"{project.id} was collected for {collected_snapshot or 'no snapshot'}, not "
                f"{snapshot_date}; rebuild data/projects first"
            )

        def text(value: Any) -> str:
            return "" if value is None else str(value)

        projects.append(
            {
                "id": project.id,
                "name": project.name,
                "status": project.status.value,
                "decision_reason": project.decision_reason,
                "primary_category": project.primary_category,
                "description": project.description,
                "repository": project.repository,
                "repository_url": project.repository_url,
                "owner": project.owner,
                "forge_kind": project.forge.kind.value,
                "forge_host": project.forge.host,
                "homepage": text(project.homepage),
                "license_spdx": text(project.license_spdx),
                "license_class": project.license_class.value,
                "capabilities": ";".join(project.capabilities),
                "language": text(collected.get("language")),
                "created_at": text(collected.get("created_at")),
                "pushed_at": text(collected.get("last_commit_at")),
                "latest_release_at": text(collected.get("latest_release_at")),
                "project_age_days": text(
                    days_between(collected.get("created_at"), snapshot_date)
                ),
                "days_since_push": text(
                    days_between(collected.get("last_commit_at"), snapshot_date)
                ),
                "archived": text(collected.get("archived")),
                "visibility": text(collected.get("visibility")),
                "lines_of_code_estimate": text(
                    collected.get("lines_of_code_estimate")
                ),
                "has_docs": text(collected.get("has_docs")),
                "has_tests": text(collected.get("has_tests")),
                "has_ci": text(collected.get("has_ci")),
                "pypi_packages": ";".join(project.registries.pypi),
                "conda_packages": ";".join(project.registries.conda),
                "julia_packages": ";".join(project.registries.julia),
            }
        )
        for source_name, (metric_name, unit) in metric_fields.items():
            value = collected.get(source_name)
            if value is not None:
                metrics.append(
                    {
                        "project_id": project.id,
                        "metric": metric_name,
                        "value": str(value),
                        "unit": unit,
                    }
                )
        for publication in project.publications:
            publications.append(
                {
                    "project_id": project.id,
                    "doi": publication.doi,
                    "role": publication.role,
                    # A citation observation records that the canonical DOI was
                    # resolved, including when its count is zero.
                    "missing_reason": ""
                    if publication.role == "canonical"
                    and "canonical_citations" in collected
                    else "unknown",
                }
            )
        capabilities.extend(
            {
                "project_id": project.id,
                "capability": capability,
                "present": "True",
                "source": "curated",
            }
            for capability in project.capabilities
        )
        dependencies.extend(
            {
                "project_id": project.id,
                "package": item["package"],
                "dependency": item["dependency"],
                "requirement": item.get("requirement", ""),
                "marker": item.get("marker", ""),
                "dependency_project_id": item.get("dependency_project", ""),
            }
            for item in collected.get("dependencies", [])
        )

    return {
        "projects": projects,
        "metrics": metrics,
        "publications": publications,
        "capabilities": capabilities,
        "dependencies": dependencies,
    }


def prepare_docs(snapshot_date: str) -> None:
    PATHS.docs.mkdir(parents=True, exist_ok=True)
    target = PATHS.docs / "data"
    target.mkdir(parents=True, exist_ok=True)
    snapshot = PATHS.snapshot(snapshot_date)
    for source in snapshot.glob("*.csv"):
        shutil.copy2(source, target / source.name)
    shutil.copy2(snapshot / "manifest.json", target / "manifest.json")


def metric_lookup(metrics: list[dict[str, str]]) -> dict[tuple[str, str], float]:
    output = {}
    for item in metrics:
        if item["value"] != "":
            output[(item["project_id"], item["metric"])] = float(item["value"])
    return output


def project_map(projects: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {item["id"]: item for item in projects}


def metric_index(
    metrics: list[dict[str, str]],
) -> dict[tuple[str, str], dict[str, str]]:
    """Index whole metric rows so a reader can see the reason behind a blank."""
    return {(item["project_id"], item["metric"]): item for item in metrics}


def canonical_publications(
    publications: list[dict[str, str]],
) -> dict[str, dict[str, str]]:
    return {
        item["project_id"]: item for item in publications if item["role"] == "canonical"
    }


def _figure_html(figures: list[go.Figure]) -> str:
    parts = []
    for index, figure in enumerate(figures):
        figure.update_layout(
            template="plotly_white",
            colorway=["#087e8b", "#ff5a5f", "#f5b700", "#5c4d7d", "#4c956c"],
            font={"family": "system-ui, sans-serif", "color": "#13293d"},
            margin={"l": 55, "r": 25, "t": 65, "b": 55},
        )
        parts.append(
            '<section class="plot">'
            + to_html(
                figure,
                full_html=False,
                include_plotlyjs="inline" if index == 0 else False,
                config={"displaylogo": False, "responsive": True},
                # Plotly defaults to a random UUID per figure, which would make
                # an otherwise identical rebuild produce different bytes.
                div_id=f"figure-{index}",
            )
            + "</section>"
        )
    return "".join(parts)


def render_page(
    filename: str,
    *,
    title: str,
    heading: str,
    lede: str,
    snapshot_date: str,
    figures: list[go.Figure] | None = None,
    body: str = "",
) -> Path:
    figures_html = _figure_html(figures or [])
    environment = Environment(
        loader=BaseLoader(), autoescape=select_autoescape(default_for_string=True)
    )
    rendered = environment.from_string(PAGE_TEMPLATE).render(
        title=title,
        heading=heading,
        lede=lede,
        snapshot_date=snapshot_date,
        navigation=NAVIGATION,
        content=body + figures_html,
    )
    output = PATHS.docs / filename
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(rendered)
    return output


def overview_content(data: dict[str, Any]) -> tuple[str, list[go.Figure]]:
    projects = data["projects"]
    status = Counter(item["status"] for item in projects)
    categories = Counter(
        item["primary_category"] for item in projects if item["status"] == "included"
    )
    publications = sum(
        item["role"] == "canonical" and item["missing_reason"] == ""
        for item in data["publications"]
    )
    # Licensing is counted, not used as a filter, so this share describes the
    # ecosystem rather than describing the selection rule that built the list.
    in_scope = [item for item in projects if item["status"] != "excluded"]
    openness = Counter(item["license_class"] for item in in_scope)
    open_source = openness["osi-approved"]
    body = f"""
    <section class="cards">
      <div class="card"><strong>{status["included"]}</strong>included projects</div>
      <div class="card"><strong>{open_source} of {len(in_scope)}</strong>OSI-approved licenses</div>
      <div class="card"><strong>{len(categories)}</strong>primary categories</div>
      <div class="card"><strong>{publications}</strong>resolved canonical works</div>
    </section>
    <p class="note">Every reusable DAS code found is catalogued regardless of its license, so the open-source share above is a measurement rather than a consequence of the inclusion rule. Ownership is recorded too: the author of this study contributes to DASDAE, whose projects are counted here on the same terms as everyone else's and shown by owner below. Download the <a href="data/projects.csv">project catalog</a>, <a href="data/metrics.csv">tidy metrics</a>, or the complete files listed in the <a href="data/manifest.json">snapshot manifest</a>.</p>
    """
    figure = go.Figure(
        go.Bar(
            x=list(categories.values()),
            y=list(categories.keys()),
            orientation="h",
            text=list(categories.values()),
        )
    )
    figure.update_layout(
        title="Included projects by primary category",
        xaxis_title="Projects",
        height=_row_height(len(categories)),
    )
    labels = [
        ("osi-approved", "OSI-approved"),
        ("source-available", "Source-available"),
        ("unlicensed", "No license published"),
        ("unknown", "Terms unresolved"),
    ]
    present = [(label, openness[key]) for key, label in labels if openness[key]]
    license_figure = go.Figure(
        go.Bar(
            x=[count for _, count in present],
            y=[label for label, _ in present],
            orientation="h",
            text=[count for _, count in present],
        )
    )
    license_figure.update_layout(
        title="Reuse terms across every catalogued DAS code",
        xaxis_title="Projects",
    )
    return body, [figure, license_figure, _owner_figure(projects)]


def _owner_figure(projects: list[dict[str, str]]) -> go.Figure:
    """Chart who publishes the included projects, concentration included.

    A field where a handful of groups write most of the software is a
    different ecosystem from one with a long tail, and the difference is
    invisible if ownership is only ever printed one row at a time.
    """
    owners = Counter(item["owner"] for item in projects if item["status"] == "included")
    top = owners.most_common(12)
    remainder = sum(owners.values()) - sum(count for _, count in top)
    labels = [name for name, _ in top]
    counts = [count for _, count in top]
    if remainder:
        labels.append(f"{len(owners) - len(top)} owners with one project")
        counts.append(remainder)
    figure = go.Figure(go.Bar(x=counts, y=labels, orientation="h", text=counts))
    figure.update_layout(
        title="Included projects by publishing owner",
        xaxis_title="Projects",
        yaxis={"autorange": "reversed"},
        height=_row_height(len(labels)),
    )
    return figure


def _row_height(rows: int, *, per_row: int = 22, minimum: int = 420) -> int:
    """Height for a horizontal chart whose row count is not known in advance."""
    return max(minimum, per_row * rows + 160)


def landscape_figures(data: dict[str, Any]) -> list[go.Figure]:
    metrics = metric_lookup(data["metrics"])
    rows = [item for item in data["projects"] if item["status"] != "excluded"]
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        stars = metrics.get((row["id"], "repo_stars"))
        downloads = metrics.get((row["id"], "pypi_downloads_30d"))
        if stars is not None and downloads is not None:
            groups[row["primary_category"]].append(
                {"row": row, "stars": stars, "downloads": downloads}
            )
    scatter = go.Figure()
    for category, items in sorted(groups.items()):
        scatter.add_trace(
            go.Scatter(
                name=category,
                mode="markers+text",
                x=[item["stars"] for item in items],
                y=[item["downloads"] for item in items],
                text=[item["row"]["name"] for item in items],
                textposition="top center",
                customdata=[item["row"]["status"] for item in items],
                hovertemplate="%{text}<br>Stars: %{x:,.0f}<br>PyPI 30d: %{y:,.0f}<br>Status: %{customdata}<extra></extra>",
            )
        )
    scatter.update_layout(
        title="Repository attention and recent PyPI traffic",
        xaxis_title="Repository stars",
        yaxis_title="PyPI downloads, last 30 days (mirror-filtered)",
    )

    capabilities = sorted({item["capability"] for item in data["capabilities"]})
    included = [item for item in rows if item["status"] == "included"]
    present = {
        (item["project_id"], item["capability"])
        for item in data["capabilities"]
        if item["present"].lower() == "true"
    }
    heatmap = go.Figure(
        go.Heatmap(
            z=[
                [
                    1 if (project["id"], capability) in present else 0
                    for capability in capabilities
                ]
                for project in included
            ],
            x=capabilities,
            y=[item["name"] for item in included],
            colorscale=[[0, "#edf2f4"], [1, "#087e8b"]],
            showscale=False,
            hovertemplate="%{y}<br>%{x}<extra></extra>",
        )
    )
    heatmap.update_layout(
        title="Curated capability map",
        xaxis={"tickangle": -45},
        # The catalog grows; a fixed height would squeeze the rows until the
        # project labels became unreadable, which is a silent loss of the data.
        height=_row_height(len(included)),
    )
    return [scatter, heatmap]


def adoption_figures(data: dict[str, Any]) -> list[go.Figure]:
    metrics = metric_lookup(data["metrics"])
    projects = project_map(data["projects"])
    specs = (
        ("repo_stars", "Repository stars", "Point-in-time count, host-reported"),
        ("pypi_downloads_30d", "PyPI downloads", "Last 30 days, mirrors excluded"),
        ("conda_downloads_cumulative", "Conda downloads", "Cumulative artifact total"),
        ("canonical_citations", "Canonical-work citations", "OpenAlex snapshot"),
    )
    figures = []
    for metric, title, subtitle in specs:
        values = sorted(
            (
                (value, projects[project_id]["name"])
                for (project_id, name), value in metrics.items()
                if name == metric and projects[project_id]["status"] != "excluded"
            ),
            reverse=True,
        )
        figure = go.Figure(
            go.Bar(
                x=[value for value, _ in values],
                y=[name for _, name in values],
                orientation="h",
                text=[f"{value:,.0f}" for value, _ in values],
            )
        )
        figure.update_layout(
            title=f"{title}<br><sup>{subtitle}</sup>",
            xaxis_title=title,
            yaxis={"autorange": "reversed"},
            height=_row_height(len(values)),
        )
        figures.append(figure)
    return figures


def _signal_value(raw: str) -> int | None:
    """None leaves the heatmap cell empty: unobserved is not confirmed absence."""
    if raw == "":
        return None
    return 1 if raw.lower() == "true" else 0


def health_figures(data: dict[str, Any]) -> list[go.Figure]:
    projects = [item for item in data["projects"] if item["status"] == "included"]
    recency = sorted(
        (float(item["days_since_push"]), item["name"])
        for item in projects
        if item["days_since_push"] != ""
    )
    recency_figure = go.Figure(
        go.Bar(
            x=[value for value, _ in recency],
            y=[name for _, name in recency],
            orientation="h",
            text=[f"{value:,.0f} d" for value, _ in recency],
        )
    )
    recency_figure.update_layout(
        title="Time since the default branch was last pushed",
        xaxis_title="Days at snapshot date (lower is more recent)",
        yaxis={"autorange": "reversed"},
    )
    loc = sorted(
        (
            (float(item["lines_of_code_estimate"]), item["name"])
            for item in projects
            if item["lines_of_code_estimate"] != ""
        ),
        reverse=True,
    )
    loc_figure = go.Figure(
        go.Bar(
            x=[value for value, _ in loc],
            y=[name for _, name in loc],
            orientation="h",
            text=[f"{value:,.0f}" for value, _ in loc],
        )
    )
    loc_figure.update_layout(
        title=(
            "Estimated lines of source code"
            "<br><sup>Language bytes ÷ 32; notebooks excluded.</sup>"
        ),
        xaxis_title="Estimated lines",
        yaxis={"autorange": "reversed"},
        height=_row_height(len(loc)),
    )
    signal_names = ["has_docs", "has_tests", "has_ci"]
    signals = go.Figure(
        go.Heatmap(
            z=[
                [_signal_value(item[name]) for name in signal_names]
                for item in projects
            ],
            x=["Documentation tree", "Test tree", "CI configuration"],
            y=[item["name"] for item in projects],
            colorscale=[[0, "#edf2f4"], [1, "#4c956c"]],
            showscale=False,
            hovertemplate="%{y}<br>%{x}<extra></extra>",
        )
    )
    signals.update_layout(
        title=(
            "Observable repository signals"
            "<br><sup>Presence, not quality. An empty cell was never "
            "observed and is not the same as absent.</sup>"
        )
    )
    return [recency_figure, loc_figure, signals]


#: Human wording for the missingness reasons recorded in metrics.csv.
MISSING_LABELS = {
    "not_applicable": "not applicable",
    "not_published": "not published",
    "unavailable": "unavailable",
    "fetch_error": "not retrieved",
    "unknown": "unknown",
}


def _metric_cell(entry: dict[str, str] | None) -> str:
    """Render a metric as a count, or as the reason it is blank — never a zero."""
    if entry is None:
        return "<span class='meta'>not applicable</span>"
    if entry["value"] != "":
        return f"{float(entry['value']):,.0f}"
    reason = entry["missing_reason"]
    return (
        f"<span class='meta'>{html.escape(MISSING_LABELS.get(reason, reason))}</span>"
    )


def _publication_cell(entry: dict[str, str] | None) -> str:
    """Render the curated canonical work, or say plainly that there is none."""
    if entry is None:
        return "<span class='meta'>no canonical work recorded</span>"
    doi = html.escape(entry["doi"])
    if entry["missing_reason"] != "":
        return f"<span class='meta'>DOI {doi} not resolved</span>"
    label = html.escape(entry["title"] or entry["doi"])
    year = (
        f" ({html.escape(entry['publication_year'])})"
        if entry["publication_year"]
        else ""
    )
    return f"<a href='https://doi.org/{doi}'>{label}</a>{year}"


def catalog_html(data: dict[str, Any]) -> str:
    metrics = metric_index(data["metrics"])
    canonical = canonical_publications(data["publications"])
    rows = []
    for item in data["projects"]:
        project_id = item["id"]
        rows.append(
            "<tr "
            f"data-status='{html.escape(item['status'])}' "
            f"data-category='{html.escape(item['primary_category'])}'>"
            f"<td><a href='{html.escape(item['repository_url'])}'>{html.escape(item['name'])}</a>"
            f"<br><span class='meta'>{html.escape(item['repository'])}</span></td>"
            f"<td>{html.escape(item['status'])}</td>"
            f"<td>{html.escape(item['primary_category'])}</td>"
            f"<td>{html.escape(item['license_spdx'] or 'None published')}"
            f"<br><span class='meta'>{html.escape(item['license_class'])}</span></td>"
            f"<td>{_metric_cell(metrics.get((project_id, 'repo_stars')))}</td>"
            f"<td>{_metric_cell(metrics.get((project_id, 'pypi_downloads_30d')))}</td>"
            f"<td>{_metric_cell(metrics.get((project_id, 'canonical_citations')))}</td>"
            f"<td>{html.escape(item['capabilities'])}</td>"
            f"<td>{_publication_cell(canonical.get(project_id))}</td>"
            f"<td>{html.escape(item['decision_reason'])}</td>"
            "</tr>"
        )
    categories = sorted({item["primary_category"] for item in data["projects"]})
    options = "".join(
        f"<option value='{html.escape(value)}'>{html.escape(value)}</option>"
        for value in categories
    )
    return f"""
    <label>Search <input id="search" type="search" placeholder="Name, capability, license…"></label>
    <label>Status <select id="status"><option value="">All</option><option>included</option><option>watchlist</option><option>excluded</option></select></label>
    <label>Category <select id="category"><option value="">All</option>{options}</select></label>
    <p class="note">Counts are point-in-time evidence from different sources and are not comparable with one another. A blank cell states why the value is absent; none of them mean zero.</p>
    <div class="table-wrap"><table id="catalog"><thead><tr><th>Project</th><th>Status</th><th>Category</th><th>License</th><th>Stars</th><th>PyPI 30d</th><th>Citations</th><th>Capabilities</th><th>Canonical work</th><th>Decision</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>
    <script>
    const inputs = ['search', 'status', 'category'].map(id => document.getElementById(id));
    function filterRows() {{
      const query = inputs[0].value.toLowerCase();
      const status = inputs[1].value;
      const category = inputs[2].value;
      document.querySelectorAll('#catalog tbody tr').forEach(row => {{
        const show = row.innerText.toLowerCase().includes(query)
          && (!status || row.dataset.status === status)
          && (!category || row.dataset.category === category);
        row.hidden = !show;
      }});
    }}
    inputs.forEach(input => input.addEventListener('input', filterRows));
    </script>
    """
