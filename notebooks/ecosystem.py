# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo",
#     "pandas",
#     "plotly",
# ]
# ///
"""The open-source DAS ecosystem: website and slide deck in one marimo notebook.

Reads `public/ecosystem.csv` and `public/commits.csv` next to this file through
`mo.notebook_location()`, so the same code runs from disk (`marimo run`) and
from the browser (`marimo export html-wasm`). Every number in the prose is
computed in the cell that prints it. Figures plot `included` projects only,
state their denominator, and never turn a missing value into a zero.
"""

import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium", layout_file="layouts/ecosystem.slides.json")


@app.cell
def _():
    from collections import Counter

    import marimo as mo
    import pandas as pd
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    return Counter, go, make_subplots, mo, pd


@app.cell
def _(mo, pd):
    _root = mo.notebook_location()
    assert _root is not None, "marimo could not determine the notebook location"

    def _read(name):
        # str() gives a filesystem path locally and an https URL in the WASM
        # export; pandas reads both (urllib is routed through the browser's
        # fetch by pyodide_http, which marimo installs at startup).
        return pd.read_csv(
            str(_root / "public" / name), dtype=str, keep_default_na=False
        )

    eco = _read("ecosystem.csv")
    commits = _read("commits.csv")

    included = eco[eco["status"] == "included"].reset_index(drop=True)
    watchlist = eco[eco["status"] == "watchlist"].reset_index(drop=True)
    N = len(included)

    _stamp_cols = ["reviewed_at"] + [
        c for c in eco.columns if c.endswith("_scanned_at")
    ]
    _stamps = pd.concat(
        [
            pd.to_datetime(
                eco[c].where(eco[c] != ""), utc=True, errors="coerce", format="ISO8601"
            )
            for c in _stamp_cols
        ]
    )
    SNAPSHOT_AT = _stamps.max()
    SNAPSHOT = SNAPSHOT_AT.date().isoformat()
    return N, SNAPSHOT, SNAPSHOT_AT, commits, eco, included, watchlist


@app.cell
def _(N, mo, pd):
    def num(frame, col):
        """Numeric column; blank stays missing (NaN), never zero."""
        series = frame[col]
        return pd.to_numeric(series.where(series != ""), errors="coerce")

    def flag(frame, col):
        """Boolean column; anything but 'True'/'False' stays missing."""
        return frame[col].map({"True": True, "False": False})

    def n_known(series):
        return int(series.notna().sum())

    def of(count, known=N, what="included"):
        return f"{count} of {known} {what}"

    def split_list(series):
        """Explode a ';'-joined column into one row per (index, item)."""
        return (
            series.str.split(";")
            .explode()
            .loc[lambda s: s.notna() & (s != "")]
            .str.strip()
        )

    def callout(text):
        return mo.callout(mo.md(text), kind="neutral")

    return callout, flag, n_known, num, of, split_list


@app.cell
def _(mo):
    # Palette from the dataviz reference instance; both modes validated with
    # scripts/validate_palette.js (adjacent pairs, all checks pass).
    _LIGHT = {
        "series": ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"],
        "sequential": [
            "#cde2fb",
            "#9ec5f4",
            "#6da7ec",
            "#3987e5",
            "#256abf",
            "#184f95",
            "#0d366b",
        ],
        "absent": "#c3c2b7",
        "unknown": "#e8e7e1",
        "ink": "#0b0b0b",
        "ink2": "#52514e",
        "muted": "#898781",
        "grid": "#e1e0d9",
        "baseline": "#c3c2b7",
        "surface": "#fcfcfb",
    }
    _DARK = {
        "series": ["#3987e5", "#d95926", "#199e70", "#c98500", "#d55181"],
        "sequential": [
            "#184f95",
            "#1c5cab",
            "#256abf",
            "#2a78d6",
            "#5598e7",
            "#86b6ef",
            "#b7d3f6",
        ],
        "absent": "#4a4a47",
        "unknown": "#2c2c2a",
        "ink": "#ffffff",
        "ink2": "#c3c2b7",
        "muted": "#898781",
        "grid": "#2c2c2a",
        "baseline": "#383835",
        "surface": "#1a1a19",
    }
    THEME = mo.app_meta().theme
    PAL = _DARK if THEME == "dark" else _LIGHT
    FONT = 'system-ui, -apple-system, "Segoe UI", sans-serif'

    def style(fig, height=460, note=None, legend=True, bottom=40):
        """House style: recessive chrome, hairline grid, note in muted ink.

        Margins are explicit because marimo's plotly view does not grow them
        for long category labels: the left margin is sized from the longest
        string on any y axis, and `bottom` is for rotated x labels.
        """
        labels = [
            value
            for trace in fig.data
            if getattr(trace, "y", None) is not None
            for value in trace.y
            if isinstance(value, str)
        ]
        longest = max((len(value) for value in labels), default=0)
        left = 7 * longest + 24 if longest else 56
        top = 46 if note else 16
        axis = {
            "automargin": True,
            "gridcolor": PAL["grid"],
            "gridwidth": 1,
            "zerolinecolor": PAL["baseline"],
            "linecolor": PAL["baseline"],
            "tickfont": {"color": PAL["ink2"]},
            "title": {"font": {"color": PAL["ink2"]}},
        }
        fig.update_layout(
            template=None,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={"family": FONT, "color": PAL["ink"], "size": 14},
            margin={"l": left, "r": 20, "t": top, "b": bottom},
            height=height,
            colorway=PAL["series"],
            hoverlabel={"font": {"family": FONT}},
            showlegend=legend,
            legend={
                "orientation": "h",
                "traceorder": "normal",
                "yanchor": "top",
                "y": -12 / (height - top - bottom),
                "x": 0,
                "font": {"color": PAL["ink2"]},
            },
        )
        fig.update_xaxes(**axis)
        fig.update_yaxes(**axis)
        if note:
            fig.add_annotation(
                text=note,
                xref="paper",
                yref="paper",
                x=0,
                y=1.0,
                yshift=28,
                xanchor="left",
                yanchor="bottom",
                showarrow=False,
                font={"color": PAL["muted"], "size": 12},
            )
        return fig

    return PAL, style


@app.cell
def _(N, SNAPSHOT, eco, mo, watchlist):
    mo.md(
        f"""
    # The open-source DAS ecosystem

    ### What exists, what is missing, and where it is going

    Derrick Chambers · Galileo Fiber Optic Conference · 2026

    *{len(eco)} projects reviewed, {N} included, {len(watchlist)} on a watchlist · snapshot {SNAPSHOT}*
    """
    )
    return


@app.cell
def _(Counter, N, included, mo):
    _owners = Counter(included["owner"])
    _dasdae = _owners["DASDAE"]
    _top_owner, _top_count = _owners.most_common(1)[0]
    mo.md(
        f"""
    ## Who is talking

    - Geophysical engineer working in mining
    - Architect of DASCore, and DASDAE publishes {_dasdae} of the {N} projects counted here{" — the largest share of any one owner" if _top_owner == "DASDAE" else f" ({_top_owner} publishes the most, {_top_count})"}
    - So I am not a neutral observer

    Everything here comes from a dated, public snapshot. The collection code, the inclusion decisions, and the raw responses are all in the open. Please check my work.
    """
    )
    return


@app.cell
def _(mo):
    mo.md("""
    ## Why care about tools?

    > New directions in science are launched by new tools much more often than by new concepts. The effect of a concept-driven revolution is to explain old things in new ways. The effect of a tool-driven revolution is to discover new things that have to be explained.
    >
    > — Freeman Dyson, *Imagined Worlds* (1997)

    We name whole eras after the tools that set their ceiling: stone, bronze, iron. This conference is named after a man who did not invent the telescope, but pointed a better one at the sky.

    Seismology's own version: C and Fortran driven from the shell, then Python, R, MATLAB and Julia, then shared formats, then shared libraries. ObsPy never discovered anything by itself. It lowered the barrier, and a generation of discoveries followed.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## DAS is earlier on that curve

    DAS gives us more channels than seismology has ever had, and far less shared infrastructure to handle them. Several foundational packages have appeared, each with real strengths, and no guarantee that any two of them fit together.

    **So: what already exists, and where does it fail to fit?**
    """)
    return


@app.cell
def _(N, eco, mo, watchlist):
    _excluded = int((eco["status"] == "excluded").sum())
    mo.md(
        f"""
    ## How the list was built

    - Candidates come from forge searches, package registries, and the DAS literature
    - Every candidate is reviewed by hand before inclusion; discovery never silently promotes a repository
    - Included means *reusable software*: a package, framework, or CLI. Not a paper's supplementary notebook
    - Every value records its source and retrieval time; a missing metric stays missing, never zero

    **{len(eco)} reviewed → {N} included**, {len(watchlist)} on a watchlist for scope or reusability questions, {_excluded} excluded after review.

    This is a floor on the ecosystem, not a census. If your package is missing, that is a backlog, not a judgement.
    """
    )
    return


@app.cell
def _(mo):
    mo.md("""
    TODO: discovery funnel (candidates probed → triaged → reviewed). The candidate and coverage ledgers live under `data/`, which the published notebook cannot reach; add the counts to a public table before plotting. Skipped in the slides layout.
    """)
    return


@app.cell
def _(included, mo, n_known):
    _lang = included["primary_language"].where(
        included["primary_language"] != "", included["language"]
    )
    mo.md(
        f"""
    ## The ecosystem is broader than it feels

    Primary category is a manual judgement; several projects span more than one. Language is the largest share of lines in the mirror, falling back to the forge's label ({n_known(_lang.where(_lang != ""))} of {len(included)} known).
    """
    )
    return


@app.cell
def _(PAL, go, included, n_known, style):
    _lang = included["primary_language"].where(
        included["primary_language"] != "", included["language"]
    )
    _lang_known = _lang.where(_lang != "")
    _counts = _lang_known.value_counts()
    _named = list(_counts.index[:3])
    _labels = {"Jupyter Notebook": "notebooks", "Jupyter": "notebooks"}

    def _bucket(value):
        if value == "":
            return "not reported"
        return value if value in _named else "other"

    _frame = included.assign(lang=_lang.map(_bucket))
    _order = _frame["primary_category"].value_counts().index[::-1]
    _series = [*_named, "other", "not reported"]
    _colors = [*PAL["series"][: len(_named)], PAL["absent"], PAL["unknown"]]

    _fig = go.Figure()
    for _name, _color in zip(_series, _colors, strict=True):
        _sub = _frame[_frame["lang"] == _name]
        if _sub.empty:
            continue
        _per = _sub["primary_category"].value_counts().reindex(_order, fill_value=0)
        _fig.add_bar(
            y=[c.replace("-", " ") for c in _order],
            x=_per.values,
            name=_labels.get(_name, _name),
            orientation="h",
            marker={"color": _color, "line": {"color": PAL["surface"], "width": 1}},
            hovertemplate="%{y}<br>%{x} project(s)<extra>%{fullData.name}</extra>",
        )
    _totals = _frame["primary_category"].value_counts().reindex(_order)
    for _cat, _total in _totals.items():
        _fig.add_annotation(
            x=_total,
            y=_cat.replace("-", " "),
            text=str(_total),
            showarrow=False,
            xanchor="left",
            xshift=6,
            font={"color": PAL["ink2"], "size": 12},
        )
    _fig.update_layout(
        barmode="stack",
        bargap=0.4,
        barcornerradius=4,
        xaxis={
            "showticklabels": False,
            "showgrid": False,
            "range": [0, _totals.max() * 1.08],
        },
        yaxis={"title": ""},
    )
    style(
        _fig,
        height=36 * len(_order) + 110,
        note=f"{len(included)} included projects · language known for {n_known(_lang_known)} of {len(included)}",
    )
    return


@app.cell
def _(mo):
    METRICS = {
        "GitHub stars": "stars",
        "Forks": "forks",
        "Contributors": "contributors",
        "Tagged releases": "releases",
        "Commits": "commits",
        "Lines of code": "lines_total",
        "PyPI downloads, last 180 days": "pypi_downloads_180d",
        "Conda downloads, all time": "conda_downloads_total",
        "Citations": "citations_total",
    }
    x_metric = mo.ui.dropdown(METRICS, value="GitHub stars", label="x")
    y_metric = mo.ui.dropdown(METRICS, value="PyPI downloads, last 180 days", label="y")
    mo.vstack(
        [
            mo.md(
                """
    ## And adoption thins out fast

    Registry counts include CI and mirror traffic, so read them as an upper bound on human use. The 30-day window is flattered by release spikes; 180 days is the honest one.
    """
            ),
            mo.hstack([x_metric, y_metric], justify="start", gap=2),
        ]
    )
    return x_metric, y_metric


@app.cell
def _(N, PAL, callout, go, included, num, style, x_metric, y_metric):
    def _figure():
        _x = num(included, x_metric.value)
        _y = num(included, y_metric.value)
        _xl = x_metric.selected_key
        _yl = y_metric.selected_key
        _both = _x.notna() & _y.notna()
        _pos = _both & (_x > 0) & (_y > 0)
        _zeros = int((_both & ~_pos).sum())

        if not _both.any():
            return callout(
                f"**{_xl}** and **{_yl}** are both reported for 0 of {N} included projects "
                f"({_xl}: {int(_x.notna().sum())}, {_yl}: {int(_y.notna().sum())}). "
                "Nothing to plot until the measurement lands."
            )
        else:
            _frame = included[_pos].assign(x=_x[_pos], y=_y[_pos])
            _label = _frame.nlargest(5, "y").index
            _fig = go.Figure(
                go.Scatter(
                    x=_frame["x"],
                    y=_frame["y"],
                    mode="markers+text",
                    text=[
                        name if idx in _label else ""
                        for idx, name in _frame["name"].items()
                    ],
                    textposition="top center",
                    textfont={"color": PAL["ink2"], "size": 12},
                    customdata=_frame["name"],
                    marker={
                        "size": 11,
                        "color": PAL["series"][0],
                        "line": {"color": PAL["surface"], "width": 2},
                    },
                    hovertemplate=(
                        "%{customdata}<br>"
                        + _xl
                        + ": %{x:,}<br>"
                        + _yl
                        + ": %{y:,}<extra></extra>"
                    ),
                )
            )
            _fig.update_layout(
                xaxis={"title": _xl, "type": "log", "dtick": 1, "exponentformat": "SI"},
                yaxis={"title": _yl, "type": "log", "dtick": 1, "exponentformat": "SI"},
            )
            _note = f"both reported for {int(_both.sum())} of {N} included"
            if _zeros:
                _note += f" · {_zeros} with a zero on either axis fall outside the log scales"
            return style(_fig, height=470, note=_note, legend=False)

    _figure()
    return


@app.cell
def _(included, mo, of):
    _osi = int((included["license_class"] == "osi-approved").sum())
    _copyleft = int(
        included["license_spdx"].str.startswith(("GPL", "LGPL", "AGPL")).sum()
    )
    _none = int((included["license_class"] == "unlicensed").sum())
    mo.md(
        f"""
    ## Most of it is research code, not infrastructure

    Signals are detected from repository structure, so they under-count projects that document or test somewhere unusual. Licensing is recorded, not required: {of(_osi)} carry an OSI-approved license, {of(_copyleft)} are copyleft, and {_none} publish source with no license at all, which grants nobody the right to reuse them.
    """
    )
    return


@app.cell
def _(N, PAL, SNAPSHOT_AT, flag, go, included, num, pd, style):
    _pushed = pd.to_datetime(
        included["pushed_at"].where(included["pushed_at"] != ""),
        utc=True,
        errors="coerce",
        format="ISO8601",
    )
    # Comparisons turn missing into False, so mask them back to missing.
    _recent = ((SNAPSHOT_AT - _pushed).dt.days <= 365).where(_pushed.notna())
    _releases = num(included, "releases")
    _rows = [
        ("Documentation", flag(included, "has_docs")),
        ("Tests", flag(included, "has_tests")),
        ("Continuous integration", flag(included, "has_ci")),
        ("Any tagged release", (_releases > 0).where(_releases.notna())),
        (
            "Published on PyPI or conda",
            (included["pypi"] != "") | (included["conda"] != ""),
        ),
        ("Pushed in the last year", _recent),
        ("OSI-approved license", included["license_class"] == "osi-approved"),
    ]

    _labels = [label for label, _ in _rows][::-1]
    _present = [int(s.eq(True).sum()) for _, s in _rows][::-1]
    _absent = [int(s.eq(False).sum()) for _, s in _rows][::-1]
    _unknown = [N - p - a for p, a in zip(_present, _absent, strict=True)]

    _fig = go.Figure()
    _line = {"color": PAL["surface"], "width": 1}
    _fig.add_bar(
        y=_labels,
        x=_present,
        name="present",
        orientation="h",
        marker={"color": PAL["series"][0], "line": _line},
        text=[f"{p} of {p + a}" for p, a in zip(_present, _absent, strict=True)],
        textposition="auto",
        textfont={"color": "#ffffff"},
        hovertemplate="%{y}: %{x} with<extra></extra>",
    )
    _fig.add_bar(
        y=_labels,
        x=_absent,
        name="absent",
        orientation="h",
        marker={"color": PAL["absent"], "line": _line},
        hovertemplate="%{y}: %{x} without<extra></extra>",
    )
    _fig.add_bar(
        y=_labels,
        x=_unknown,
        name="not reported",
        orientation="h",
        marker={"color": PAL["unknown"], "line": _line},
        hovertemplate="%{y}: %{x} not reported<extra></extra>",
    )
    _fig.update_layout(
        barmode="stack",
        bargap=0.4,
        barcornerradius=4,
        xaxis={"showticklabels": False, "showgrid": False, "range": [0, N]},
        yaxis={"title": ""},
    )
    style(
        _fig,
        height=36 * len(_rows) + 120,
        note=f"{N} included projects · labels read present of known · unknowns are the forge lookups that failed",
    )
    return


@app.cell
def _(Counter, included, mo, split_list):
    _present = Counter(split_list(included["capabilities"]))
    _singletons = sorted(name for name, count in _present.items() if count == 1)
    mo.md(
        f"""
    ## What everyone builds, and what nobody does

    **{len(_singletons)} of {len(_present)} capabilities have exactly one implementation:** {", ".join(s.replace("-", " ") for s in _singletons) or "none"}.

    Curated tags, not feature audits. If that one project stops, the capability leaves the ecosystem with it.
    """
    )
    return


@app.cell
def _(Counter, N, PAL, callout, go, included, mo, n_known, split_list, style):
    _present = Counter(split_list(included["capabilities"]))
    if not _present:
        mo.stop(
            True,
            callout(f"No capability tags are recorded for the {N} included projects."),
        )
    _ranked = _present.most_common()[::-1]
    _names = [name.replace("-", " ") for name, _ in _ranked]
    _values = [count for _, count in _ranked]

    _fig = go.Figure()
    for _label, _keep, _color in [
        ("two or more projects", lambda v: v > 1, PAL["series"][0]),
        ("one project", lambda v: v == 1, PAL["series"][1]),
    ]:
        _fig.add_bar(
            y=[n for n, v in zip(_names, _values, strict=True) if _keep(v)],
            x=[v for v in _values if _keep(v)],
            name=_label,
            orientation="h",
            marker={"color": _color},
            text=[str(v) for v in _values if _keep(v)],
            textposition="outside",
            textfont={"color": PAL["ink2"], "size": 11},
            cliponaxis=False,
            hovertemplate="%{y}<br>%{x} project(s)<extra>%{fullData.name}</extra>",
        )
    _fig.update_layout(
        barmode="overlay",
        bargap=0.35,
        barcornerradius=3,
        xaxis={
            "showticklabels": False,
            "showgrid": False,
            "range": [0, max(_values) * 1.1],
        },
        yaxis={
            "title": "",
            "tickfont": {"size": 11},
            "categoryorder": "array",
            "categoryarray": _names,
        },
    )
    style(
        _fig,
        height=20 * len(_ranked) + 120,
        note=f"capability tags known for {n_known(included['capabilities'].where(included['capabilities'] != ''))} of {N} included · {len(_ranked)} distinct tags",
    )
    return


@app.cell
def _(Counter, included, mo, split_list):
    _present = Counter(split_list(included["capabilities"]))
    _common = [name for name, count in _present.most_common() if count >= 3]
    mo.md(
        f"""
    ## Which capabilities travel together

    Projects tagged with both capabilities, for the {len(_common)} tags carried by at least three included projects. The diagonal is the tag's own count.
    """
    )
    return


@app.cell
def _(Counter, N, PAL, callout, go, included, mo, pd, split_list, style):
    _tags = split_list(included["capabilities"])
    _present = Counter(_tags)
    _common = [name for name, count in _present.most_common() if count >= 3]
    if not _common:
        mo.stop(
            True,
            callout(
                f"No capability tag is carried by three or more of the {N} included projects."
            ),
        )
    _matrix = pd.crosstab(_tags.index, _tags).reindex(columns=_common, fill_value=0)
    _co = _matrix.T @ _matrix
    _labels = [name.replace("-", " ") for name in _common]
    _fig = go.Figure(
        go.Heatmap(
            z=_co.values,
            x=_labels,
            y=_labels,
            colorscale=[
                [i / (len(PAL["sequential"]) - 1), c]
                for i, c in enumerate(PAL["sequential"])
            ],
            zmin=0,
            xgap=2,
            ygap=2,
            hovertemplate="%{y} + %{x}<br>%{z} project(s)<extra></extra>",
            colorbar={
                "thickness": 10,
                "title": "projects",
                "tickfont": {"color": PAL["ink2"]},
            },
        )
    )
    _fig.update_layout(
        xaxis={"tickangle": -45, "tickfont": {"size": 11}, "showgrid": False},
        yaxis={"autorange": "reversed", "tickfont": {"size": 11}, "showgrid": False},
    )
    style(
        _fig,
        height=26 * len(_common) + 200,
        note=f"{N} included projects · {len(_common)} of {len(_present)} tags shown",
        legend=False,
        bottom=5 * max(len(label) for label in _labels) + 40,
    )
    return


@app.cell
def _(mo):
    mo.md("""
    ## The gaps that actually hurt

    - **Interoperability**: every library invented its own data model. The fix is conversion between them, not consolidation into one
    - **Metadata**: there is a standard proposal, and almost no tooling that enforces it
    - **GPU acceleration**: DAS volumes outgrew single-threaded NumPy years ago
    - **Large-scale visualization**: nobody can look at a full survey interactively
    """)
    return


@app.cell
def _(N, SNAPSHOT_AT, commits, included, mo):
    _mine = commits[commits["project_id"].isin(included["id"])]
    mo.md(
        f"""
    ## How the code base grew

    Commit history from bare mirrors of {_mine["project_id"].nunique()} of {N} included repositories: {len(_mine):,} commits by {_mine["author_email"].str.lower().nunique()} distinct author emails. {SNAPSHOT_AT.year} is a partial year.
    """
    )
    return


@app.cell
def _(
    N,
    PAL,
    SNAPSHOT_AT,
    callout,
    commits,
    included,
    make_subplots,
    pd,
    style,
):
    def _figure():
        _mine = commits[commits["project_id"].isin(included["id"])].copy()
        if _mine.empty:
            return callout(
                f"No commit history is available yet for any of the {N} included projects."
            )
        else:
            _mine["year"] = pd.to_datetime(
                _mine["authored_at"], utc=True, errors="coerce", format="ISO8601"
            ).dt.year
            _mine = _mine[_mine["year"].notna()]
            _years = list(range(int(_mine["year"].min()), int(_mine["year"].max()) + 1))
            _by_year = _mine.groupby("year")
            _commits = _by_year.size().reindex(_years, fill_value=0)
            _cumulative = _commits.cumsum()
            _projects = _by_year["project_id"].nunique().reindex(_years, fill_value=0)
            _authors = (
                _mine.assign(email=_mine["author_email"].str.lower())
                .groupby("year")["email"]
                .nunique()
                .reindex(_years, fill_value=0)
            )
            _fig = make_subplots(
                rows=1,
                cols=3,
                subplot_titles=(
                    "Cumulative commits",
                    "Projects with a commit",
                    "Authors with a commit",
                ),
                horizontal_spacing=0.08,
            )
            _blue = PAL["series"][0]
            _wash = "rgba(42,120,214,0.10)"
            _common = {
                "mode": "lines+markers",
                "line": {"color": _blue, "width": 2},
                "marker": {
                    "size": 8,
                    "color": _blue,
                    "line": {"color": PAL["surface"], "width": 2},
                },
                "showlegend": False,
            }
            _fig.add_scatter(
                x=_years,
                y=_cumulative.values,
                fill="tozeroy",
                fillcolor=_wash,
                hovertemplate="%{x}: %{y:,} commits<extra></extra>",
                row=1,
                col=1,
                **_common,
            )
            _fig.add_scatter(
                x=_years,
                y=_projects.values,
                hovertemplate="%{x}: %{y} projects<extra></extra>",
                row=1,
                col=2,
                **_common,
            )
            _fig.add_scatter(
                x=_years,
                y=_authors.values,
                hovertemplate="%{x}: %{y} authors<extra></extra>",
                row=1,
                col=3,
                **_common,
            )
            _fig.update_xaxes(dtick=2, tickformat="d")
            _fig.update_annotations(font={"color": PAL["ink2"], "size": 13})
            _partial = (
                f" · {SNAPSHOT_AT.year} is partial"
                if _years[-1] == SNAPSHOT_AT.year
                else ""
            )
            return style(
                _fig,
                height=380,
                note=f"commit history for {_mine['project_id'].nunique()} of {N} included · {len(_mine):,} commits{_partial}",
                legend=False,
            )

    _figure()
    return


@app.cell
def _(included, mo, split_list):
    _tags = sorted(split_list(included["capabilities"]).unique())
    status_filter = mo.ui.radio(
        options=["included", "included + watchlist"],
        value="included",
        inline=True,
        label="status",
    )
    capability_filter = mo.ui.multiselect(
        options=_tags, label="capabilities (all selected must apply)"
    )
    mo.vstack(
        [
            mo.md(
                "## The catalogue\n\nSearch, sort, and follow the links. Blank cells are values that were not reported, not zeros."
            ),
            mo.hstack([status_filter, capability_filter], justify="start", gap=2),
        ]
    )
    return capability_filter, status_filter


@app.cell
def _(capability_filter, eco, mo, pd, status_filter):
    _statuses = (
        ["included"] if status_filter.value == "included" else ["included", "watchlist"]
    )
    _scope = eco[eco["status"].isin(_statuses)]
    _rows = _scope
    for _tag in capability_filter.value:
        _rows = _rows[
            _rows["capabilities"].str.split(";").map(lambda tags, t=_tag: t in tags)
        ]

    _columns = {
        "name": "name",
        "status": "status",
        "repository_url": "repository",
        "primary_category": "category",
        "capabilities": "capabilities",
        "das_focus": "DAS focus",
        "primary_language": "language",
        "license_spdx": "license",
        "stars": "stars",
        "contributors": "contributors",
        "releases": "releases",
        "pypi": "PyPI",
        "pushed_at": "last push",
        "description": "description",
    }
    _table = _rows[list(_columns)].rename(columns=_columns)
    # Same index as _rows here, so the forge label lines up row for row.
    _table["language"] = _table["language"].where(
        _table["language"] != "", _rows["language"]
    )
    _table = _table.reset_index(drop=True)
    for _col in ["stars", "contributors", "releases"]:
        _table[_col] = pd.to_numeric(
            _table[_col].where(_table[_col] != ""), errors="coerce"
        ).astype("Int64")
    _table["last push"] = _table["last push"].str.slice(0, 10)
    _table["capabilities"] = _table["capabilities"].str.replace(";", ", ")
    mo.vstack(
        [
            mo.md(
                f"*{len(_table)} of {len(_scope)} {' + '.join(_statuses)} projects shown*"
            ),
            mo.ui.table(
                _table,
                selection=None,
                page_size=12,
                show_column_summaries=False,
                show_data_types=False,
                wrapped_columns=["description", "capabilities"],
            ),
        ]
    )
    return


@app.cell
def _(mo, watchlist):
    mo.md(
        f"""
    ## The watchlist

    {len(watchlist)} projects are in scope but not yet reusable as published: an empty default branch, a single notebook, an archived repository. They are tracked, not counted, and appear in no figure above.
    """
    )
    return


@app.cell
def _(mo, watchlist):
    mo.ui.table(
        watchlist[
            ["name", "repository_url", "primary_category", "decision_reason"]
        ].rename(
            columns={
                "repository_url": "repository",
                "primary_category": "category",
                "decision_reason": "why it waits",
            }
        ),
        selection=None,
        page_size=12,
        show_column_summaries=False,
        show_data_types=False,
        wrapped_columns=["why it waits"],
    )
    return


@app.cell
def _(N, mo):
    mo.md(
        f"""
    ## Build library {N + 1}, if you want to

    A second implementation is not the problem. Competition is how a better data model, a faster reader, or a nicer API actually arrives, and the earlier charts show a field that is *under*-built, not over-built.

    What costs us is work nobody else can pick up: no license, no docs, no release, a data model nothing can read. That is not fragmentation, it is evaporation.

    **If you use these tools:** cite the software, report the bugs, send the patch.

    **If you write them:** publish to a registry, choose a license deliberately, and treat your data structures as a public interface. A converter can only reach what it can see.

    **The bar is not "don't build it." The bar is "build it so someone else can use it."**
    """
    )
    return


@app.cell
def _(mo):
    mo.md("""
    ## Coding agents change the arithmetic

    - The cost of *writing* a DAS library just fell through the floor
    - More tools is fine. More **unmaintained** tools is the risk
    - Agents write against whatever they can read: clear APIs, real docstrings, honest error messages
    - The libraries that are legible to an agent are about to get used far more than the ones that are not

    **Documentation is no longer only for humans.**
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Four experiments

    Each of these started as a gap on the earlier slide. All are recent, and all were built far faster than I could have built them three years ago.

    - **unidas**: convert between the data structures of the major libraries, so the choice of library stops being a lock-in
    - **Inventory**: shared metadata handling that matches the emerging standard
    - **DASJax**: GPU and autodiff-capable processing
    - **DerZug**: large-scale visualization for data you cannot fit on a screen

    None of these needs to be built by me. I would rather be out-competed than be the only option.
    """)
    return


@app.cell
def _(SNAPSHOT, mo):
    mo.md(
        f"""
    ## Takeaways

    1. There are more DAS tools than you think, and fewer than you need
    2. The ecosystem is one library deep in most niches, and zero deep in some
    3. The gap is not algorithms. It is the boring infrastructure between them
    4. Agents make building cheap, which makes *finishing* the hard part

    **Build the thing. Publish the tool, not just the paper.**

    *Data, methodology, and this notebook: github.com/DASDAE/oss_das_software_survey · snapshot {SNAPSHOT} · code MIT, data CC BY 4.0*
    """
    )
    return


if __name__ == "__main__":
    app.run()
