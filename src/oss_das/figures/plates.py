"""One function per figure. Each takes a measurement and returns SVG text.

A plate never computes a number. It is handed a frozen measurement from
`figures.data` and is responsible only for arrangement, so a figure and the
dataset it describes cannot drift apart.
"""

from __future__ import annotations

from collections.abc import Sequence
from itertools import pairwise
from pathlib import Path

from oss_das.figures import draw
from oss_das.figures.data import (
    LICENCE_ORDER,
    Composition,
    EcosystemTotals,
    Engineering,
    Funnel,
    Growth,
    LanguageLicence,
    LicenceMix,
    Maturity,
    PipelineFlow,
    RecordSection,
    SelectionFunnel,
    Trace,
)
from oss_das.figures.render import load_asset

#: Column centres for a four-up row on the standard canvas.
FOUR = (210, 630, 1050, 1470)
WIDTH = 1680


def _heading(c: draw.Canvas, y: float, text: str) -> None:
    c.text(840, y, text, size=draw.LABEL, fill=draw.INK, spacing=3.2, upper=True)


def pipeline_plate(flow: PipelineFlow) -> str:
    """How a query becomes a catalogued project.

    One row, not three. The probe counts and the per-project measurements are
    in the record; on a slide they are detail that costs the reader the one
    line that matters -- what came in, and what survived.
    """
    probes = (
        flow.github_searches
        + flow.gitlab_searches
        + flow.gitea_searches
        + flow.namespace_walks
    )
    c = draw.Canvas(
        width=WIDTH,
        height=260,
        title="From query to catalogue",
        desc=(
            f"Snapshot {flow.snapshot}: {probes} probes returned "
            f"{flow.candidates:,} candidates; {flow.reviewed:,} were reviewed and "
            f"{flow.included} are in scope."
        ),
    )
    came = [
        (f"{flow.candidates:,}", "Candidates", draw.INK),
        (f"{flow.reviewed:,}", "Reviewed", draw.INK),
        (f"{flow.catalogued}", "Catalogued", draw.INK),
        (f"{flow.included}", "In scope", draw.AMBER),
    ]
    for x, (number, label, colour) in zip(FOUR, came, strict=True):
        c.stat(x, 110, number, label, size=draw.BIG, colour=colour, gap=52)
    for a, b in pairwise(FOUR):
        c.arrow(a + 152, b - 152, 82)
    return c.to_svg()


def totals_plate(totals: EcosystemTotals, assets: Path) -> str:
    """The ecosystem in four numbers."""
    c = draw.Canvas(
        width=WIDTH,
        height=420,
        title="Open-source DAS software in numbers",
        desc=(
            f"{totals.projects} projects, {totals.contributors} contributors, "
            f"{totals.commits:,} commits, {totals.lines:,} lines of code."
        ),
    )
    for key in ("projects", "contributors", "commits", "lines"):
        c.parts.append(load_asset(f"icon_{key}", assets))
    c.spine(100, 1580, 228, list(FOUR))
    stats = [
        (f"{totals.projects:,}", "Projects"),
        (f"{totals.contributors:,}", "Contributors"),
        (f"{totals.commits:,}", "Commits"),
        (f"{totals.lines:,}", "Lines of code"),
    ]
    for x, (number, label) in zip(FOUR, stats, strict=True):
        c.stat(
            x,
            326,
            number,
            label,
            size=88,
            label_size=draw.LABEL,
            gap=46,
            sub_gap=38,
        )
    return c.to_svg()


def funnel_plate(funnel: SelectionFunnel) -> str:
    """How projects were selected, and why the rest were held back."""
    shown = funnel.held_back[:8]
    per_row = 4
    height = 720
    c = draw.Canvas(
        width=WIDTH,
        height=height,
        title="How projects were selected",
        desc=(
            f"{funnel.candidates:,} candidates, {funnel.reviewed:,} reviewed, "
            f"{funnel.in_scope} in scope; {funnel.held_back_total} held back."
        ),
    )
    stages = [
        (
            f"{funnel.candidates:,}",
            "Candidates",
            "Discovered by forge search",
            draw.INK,
        ),
        (f"{funnel.reviewed:,}", "Reviewed", "Read and ruled on by hand", draw.INK),
        (f"{funnel.in_scope}", "In scope", "Reusable, DAS-focused, public", draw.AMBER),
    ]
    thirds = (300, 840, 1380)
    for x, (number, label, sub, colour) in zip(thirds, stages, strict=True):
        c.stat(
            x,
            150,
            number,
            label,
            sub,
            size=draw.HERO,
            colour=colour,
            label_size=draw.LABEL,
            gap=50,
            sub_gap=38,
        )
    for a, b in pairwise(thirds):
        c.arrow(a + 190, b - 190, 118)
    c.spine(100, 1580, 292, list(thirds))

    _heading(c, 356, f"Why {funnel.held_back_total} are held back")
    label_of = {
        "not-reusable": ("Not reusable", "One-off analysis code"),
        "paper-code": ("Paper code", "Published alongside a paper"),
        "duplicate": ("Duplicate", "A mirror or fork already counted"),
        "acronym-collision": ("Acronym collision", "A different “DAS” entirely"),
        "other-fiber": ("Other fiber", "Temperature or strain"),
        "no-source": ("No public source", "Private, deleted, or README only"),
        "teaching": ("Teaching material", "Tutorials, workshops, link lists"),
        "general-toolkit": ("General toolkit", "Seismology tools that added DAS"),
        "other": ("Other", "Reason not grouped by the rules"),
    }
    for index, (key, count) in enumerate(shown):
        x = FOUR[index % per_row]
        y = 446 + (index // per_row) * 130
        name, gloss = label_of.get(key, (key.replace("-", " ").title(), ""))
        c.stat(
            x,
            y,
            f"{count}",
            name,
            gloss,
            size=draw.MID,
            colour=draw.SLATE,
            label_size=draw.LABEL_SM,
            gap=34,
            sub_gap=30,
        )
    return c.to_svg()


def licence_plate(mix: LicenceMix) -> str:
    """Reuse terms, by project and by line of code."""
    colours = {
        "osi-approved": draw.AMBER,
        "source-available": draw.CREAM,
        "unlicensed": draw.SLATE,
        "unknown": draw.GRAY,
    }
    names = {
        "osi-approved": "OSI-approved",
        "source-available": "Source-available",
        "unlicensed": "No licence",
        "unknown": "Unresolved",
    }
    c = draw.Canvas(
        width=WIDTH,
        height=420,
        title="What share of DAS software is open source",
        desc=(
            f"{mix.projects} catalogued projects and {mix.lines:,} lines, "
            "grouped by the reuse terms they publish."
        ),
    )
    _heading(c, 62, "What share is actually open source")

    for row, (title, series, total) in enumerate(
        [
            ("By project", mix.by_class, mix.projects),
            ("By line of code", mix.lines_by_class, mix.lines),
        ]
    ):
        y = 128 + row * 186
        c.text(
            140,
            y,
            title,
            size=draw.LABEL_SM,
            fill=draw.INK,
            anchor="start",
            spacing=2.4,
            upper=True,
        )
        segments = [(k, float(v), colours.get(k, draw.GRAY)) for k, v in series]
        spans = c.bar_stack(140, y + 26, 1400, 54, segments)
        for (key, start, span), (_, value) in zip(spans, series, strict=True):
            share = value / total * 100 if total else 0
            if span < 120:
                continue
            c.text(
                start + span / 2,
                y + 62,
                f"{share:.0f}%",
                size=draw.SUB,
                fill=draw.PAPER
                if colours.get(key) in (draw.AMBER, draw.SLATE)
                else draw.INK,
            )
        # One legend, under the first bar: both rows use the same four classes,
        # and a second copy would only repeat it. Swatches rather than a joined
        # string, because SVG collapses the spaces that separated the entries.
        if not row:
            step = 1400 / len(series)
            for index, (key, value) in enumerate(series):
                x = 140 + index * step
                c.rect(x, y + 100, 26, 18, fill=colours.get(key, draw.GRAY), rx=3)
                c.text(
                    x + 38,
                    y + 116,
                    f"{names.get(key, key)} {value:,}",
                    size=draw.SUB_SM,
                    fill=draw.INK,
                    anchor="start",
                )
    return c.to_svg()


def composition_plate(comp: Composition) -> str:
    """What the corpus is written in, and how little of it is packaged."""
    top = list(comp.languages[:8])
    rows, row_h = len(top), 44.0
    first = 168.0
    rule = first + rows * row_h + 4.0
    height = rule + 176.0
    c = draw.Canvas(
        width=WIDTH,
        height=height,
        title="Languages and packaging",
        desc=(
            f"{comp.total_lines:,} lines across {len(comp.languages)} languages; "
            f"{comp.with_none} of {comp.projects} DAS projects publish no package."
        ),
    )
    c.text(840, 76, "Languages and packaging", size=34, fill=draw.INK)

    # Bars run from a shared baseline so the language names form a clean right
    # edge and the eye can read the list without tracking across the bar.
    left, span = 430.0, 900.0
    widest = top[0][1] if top else 1
    for index, (language, count) in enumerate(top):
        y = first + index * row_h
        width = span * count / widest
        c.rect(
            left,
            y - 21,
            width,
            28,
            fill=draw.AMBER if not index else draw.CREAM,
            rx=3,
        )
        c.text(left - 22, y, language, size=draw.SUB, fill=draw.INK, anchor="end")
        c.text(
            left + width + 20,
            y,
            f"{count:,}  ·  {count / comp.total_lines * 100:.1f}%",
            size=draw.SUB_SM,
            fill=draw.MUTED,
            anchor="start",
        )

    c.line(180, rule, 1500, rule, stroke=draw.RULE, width=2)

    # A narrowing, not a partition: every project on PyPI carries a packaging
    # manifest, so the first two nest, and the last is the complement of the
    # second. conda is measured but not shown -- only three of the 78 are on
    # conda-forge and all three are on PyPI too, so it earns no column.
    stats = [
        (f"{comp.with_packaging}", "Set up as a package", ""),
        (f"{comp.with_pypi}", "Published on PyPI", ""),
        (f"{comp.with_none}", "No package at all", f"of {comp.projects} DAS projects"),
    ]
    for x, (number, label, sub) in zip((420, 840, 1260), stats, strict=True):
        c.stat(
            x,
            rule + 76,
            number,
            label,
            sub,
            size=draw.MID,
            label_size=draw.LABEL_SM,
            gap=32,
            sub_gap=28,
        )
    return c.to_svg()


def maturity_plate(mat: Maturity) -> str:
    """Viewers against frameworks, on sustained development."""
    import math

    interesting = [p for p in mat.projects if p.role in ("viewer", "framework")]
    if not interesting:
        interesting = list(mat.projects[:12])
    height = 800
    left, right, top, bottom = 220, 1560, 150, 520
    max_days = max((p.days for p in interesting), default=1) or 1
    max_commits = max((p.commits for p in interesting), default=1) or 1

    c = draw.Canvas(
        width=WIDTH,
        height=height,
        title="Viewers and frameworks",
        desc=(
            f"{len(mat.by_role('viewer'))} viewer projects against "
            f"{len(mat.by_role('framework'))} core frameworks, on commits and lifespan."
        ),
    )
    _heading(c, 62, "Viewers start; frameworks last")

    def sx(days: int) -> float:
        return left + (right - left) * math.sqrt(days / max_days)

    def sy(commits: int) -> float:
        return bottom - (bottom - top) * math.sqrt(commits / max_commits)

    c.line(left, bottom, right, bottom, stroke=draw.RULE, width=2)
    c.line(left, top, left, bottom, stroke=draw.RULE, width=2)
    for years in (1, 2, 3, 4):
        days = years * 365
        if days > max_days:
            break
        c.line(sx(days), bottom, sx(days), bottom + 9, stroke=draw.RULE, width=2)
        c.text(sx(days), bottom + 34, f"{years}y", size=draw.TINY, fill=draw.MUTED)
    for commits in (100, 500, 1000):
        if commits > max_commits:
            break
        c.line(left - 9, sy(commits), left, sy(commits), stroke=draw.RULE, width=2)
        c.text(
            left - 18,
            sy(commits) + 5,
            f"{commits:,}",
            size=draw.TINY,
            fill=draw.MUTED,
            anchor="end",
        )
    c.text(
        890,
        bottom + 66,
        "Days of development · both axes square-root scaled",
        size=draw.SUB_SM,
        fill=draw.MUTED,
        italic=True,
    )
    c.text(
        left - 76,
        (top + bottom) / 2,
        "Commits",
        size=draw.SUB_SM,
        fill=draw.MUTED,
        italic=True,
    )
    for index, (role, colour) in enumerate(
        (("Viewers", draw.AMBER), ("Frameworks", draw.SLATE))
    ):
        x = 300 + index * 190
        c.dot(x, top - 36, r=8, fill=colour)
        c.text(x + 16, top - 30, role, size=draw.SUB_SM, fill=draw.INK, anchor="start")

    for project in sorted(interesting, key=lambda p: p.commits):
        colour = draw.AMBER if project.role == "viewer" else draw.SLATE
        c.dot(sx(project.days), sy(project.commits), r=9, fill=colour)
        if project.commits > max_commits * 0.10 or project.days > max_days * 0.45:
            c.text(
                sx(project.days),
                sy(project.commits) - 20,
                project.name,
                size=draw.TINY,
                fill=draw.INK,
            )

    viewers = mat.by_role("viewer")
    frameworks = mat.by_role("framework")

    c.spine(100, 1580, 616, [])
    # Median authors is 1 for both groups, so it separates nothing. What does
    # separate them is how far the best of each group got.
    summary = [
        (
            420,
            f"{max((p.commits for p in viewers), default=0):,}",
            "Busiest viewer",
            "",
            draw.AMBER,
        ),
        (
            1260,
            f"{max((p.commits for p in frameworks), default=0):,}",
            "Busiest framework",
            "",
            draw.SLATE,
        ),
    ]
    for x, number, label, sub, colour in summary:
        c.stat(
            x,
            656,
            number,
            label,
            sub,
            size=draw.MID,
            colour=colour,
            label_size=draw.LABEL_SM,
            gap=32,
            sub_gap=28,
        )
    return c.to_svg()


def growth_plate(growth: Growth) -> str:
    """Commits per year, split by how central DAS is to the project."""
    colours = {
        "das-native": draw.AMBER,
        "other-fiber": draw.CREAM,
        "das-supporting": draw.SLATE,
        "not-das": draw.GRAY,
    }
    names = {
        "das-native": "DAS-native",
        "other-fiber": "Other fiber",
        "das-supporting": "DAS-supporting",
        "not-das": "Not DAS",
    }
    years = growth.years
    height = 620
    left, right, top, bottom = 180, 1580, 150, 460
    totals = [sum(vals[i] for _, vals in growth.by_class) for i in range(len(years))]
    peak = max(totals, default=1) or 1
    slot = (right - left) / max(len(years), 1)
    bar = min(slot * 0.62, 92)

    c = draw.Canvas(
        width=WIDTH,
        height=height,
        title="Commits per year",
        desc=(
            f"{sum(totals):,} commits between {years[0]} and {years[-1]}, "
            "split by how central DAS is to each project."
        ),
    )
    _heading(c, 62, "When the work happened")
    c.line(left, bottom, right, bottom, stroke=draw.RULE, width=2)
    for index, year in enumerate(years):
        centre = left + slot * (index + 0.5)
        cursor = bottom
        for cls, values in growth.by_class:
            share = values[index]
            if not share:
                continue
            span = (bottom - top) * share / peak
            cursor -= span
            c.rect(
                centre - bar / 2, cursor, bar, span, fill=colours.get(cls, draw.GRAY)
            )
        c.text(centre, bottom + 32, str(year), size=draw.SUB_SM, fill=draw.MUTED)
        if year == years[-1]:
            c.text(
                centre,
                bottom + 56,
                "part year",
                size=draw.TINY,
                fill=draw.FAINT,
                italic=True,
            )
        c.text(centre, cursor - 14, f"{totals[index]:,}", size=draw.TINY, fill=draw.INK)

    c.spine(100, 1580, 534, [])
    legend = list(growth.class_totals)
    step = 1680 / (len(legend) + 1)
    for index, (cls, total) in enumerate(legend):
        x = step * (index + 1)
        c.rect(x - 78, 574, 22, 22, fill=colours.get(cls, draw.GRAY), rx=3)
        c.text(
            x - 44,
            592,
            f"{names.get(cls, cls)}  {total:,}",
            size=draw.SUB_SM,
            fill=draw.INK,
            anchor="start",
        )
    return c.to_svg()


#: Discovery routes the census does not take. These are editorial claims about
#: method, not measurements, so they are stated here rather than derived -- but
#: each is checkable against the code: no module performs a web or literature
#: search, and a030/a040 both begin from `load_projects()`.
NOT_SEARCHED: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "The literature",
        (
            "No paper-to-software search.",
            "Citations were read only for",
            "projects already catalogued.",
        ),
    ),
    (
        "Source code",
        (
            "No scan of candidate source for",
            "interrogator format readers —",
            "TDMS, OptoDAS, PRODML.",
        ),
    ),
    (
        "Package registries",
        (
            "PyPI, conda and the Julia",
            "registry were queried only for",
            "packages already catalogued.",
        ),
    ),
    (
        "Other hosts",
        (
            "Institutional and private forges",
            "outside the seven, and any",
            "source published off-forge.",
        ),
    ),
)

#: What the forge queries actually ask, paired with a plain-language gloss.
QUERY_FAMILIES: tuple[tuple[str, str], ...] = (
    ("“distributed acoustic sensing”", "The phrase, and its variants"),
    ("Silixa · OptaSense · Febus · Terra15", "The interrogator vendors"),
    ("Repository topics", "Curated labels"),
    ("MATLAB · Julia · R", "Languages a Python search hides"),
)


def coverage_plate(flow: PipelineFlow) -> str:
    """Where the search reached, and where it could not."""
    searches = flow.github_searches + flow.gitlab_searches + flow.gitea_searches
    probes = searches + flow.namespace_walks
    c = draw.Canvas(
        width=WIDTH,
        height=520,
        title="How the search was run, and where it could not reach",
        desc=(
            f"{probes} probes produced {flow.candidates:,} candidates. "
            "Four discovery routes were not taken."
        ),
    )
    _heading(c, 64, "What was searched")
    asked = [
        (
            f"{flow.github_searches}",
            "GitHub queries",
            "Name, description, README, topic",
            draw.INK,
        ),
        (f"{flow.gitlab_searches}", "GitLab queries", "Across four hosts", draw.INK),
        (f"{flow.gitea_searches}", "Gitea queries", "Across two hosts", draw.INK),
        (
            f"{flow.namespace_walks}",
            "Namespace walks",
            "Organisations swept end to end",
            draw.AMBER,
        ),
    ]
    for x, (number, label, sub, colour) in zip(FOUR, asked, strict=True):
        c.stat(
            x,
            164,
            number,
            label,
            sub,
            size=draw.BIG,
            colour=colour,
            label_size=21,
            gap=38,
            sub_gap=32,
        )

    c.spine(100, 1580, 270, list(FOUR))
    failed = (
        f"{flow.rows_retrieved:,} results · {flow.candidates:,} distinct candidates · "
        f"{flow.probes_failed} of {probes} probes failed"
        if flow.probes_failed
        else f"{flow.rows_retrieved:,} results · {flow.candidates:,} distinct candidates"
    )
    c.text(840, 320, failed, size=draw.SUB_SM, fill=draw.MUTED, spacing=2.4, upper=True)

    _heading(c, 396, "What was not searched")
    for x, (title, _lines) in zip(FOUR, NOT_SEARCHED, strict=True):
        c.line(x - 102, 432, x + 102, 432, stroke=draw.RULE, width=2.5, dash="7 7")
        c.text(x + 1.3, 480, title, size=26, fill=draw.MUTED, spacing=2.6, upper=True)
    return c.to_svg()


def funnel_shape_plate(f: Funnel) -> str:
    """A literal funnel: every source in at the top, every exclusion out the side."""
    width, height = 1220, 850
    centre = width / 2
    mouth_y, throat_y = 126, 410
    mouth_l, mouth_r = centre - 190, centre + 190
    throat_l, throat_r = centre - 28, centre + 28
    # A cone alone reads as a triangle. The short parallel spout below it is
    # what makes the shape legible as a funnel at a glance.
    spout_y = throat_y + 48

    c = draw.Canvas(
        width=width,
        height=height,
        title="Every candidate, and how it left",
        desc=(
            f"{f.candidates:,} candidates discovered; {f.in_scope} in scope. "
            "Each stage is a count of candidates leaving by exactly one route."
        ),
    )

    def wall(y: float) -> tuple[float, float]:
        t = (y - mouth_y) / (throat_y - mouth_y)
        return (
            mouth_l + (throat_l - mouth_l) * t,
            mouth_r + (throat_r - mouth_r) * t,
        )

    def head(
        x: float, y: float, dx: float, dy: float, colour: str, size: float = 7
    ) -> None:
        """A small arrowhead at (x, y), pointing along the unit vector (dx, dy)."""
        px, py = -dy, dx
        c.parts.append(
            f'<path d="M {x:g},{y:g} '
            f"L {x - dx * size * 2 + px * size:g},{y - dy * size * 2 + py * size:g} "
            f'L {x - dx * size * 2 - px * size:g},{y - dy * size * 2 - py * size:g} Z" '
            f'fill="{colour}"/>'
        )

    # ---- sources feeding the mouth --------------------------------------
    # Kept close to the mouth: a long inflow spends canvas on empty space and
    # makes the funnel itself read as smaller than the arrows pointing at it.
    import math

    label_y = 66
    label_size = 21
    sources = list(f.searched) + list(f.pending)
    for index, name in enumerate(sources):
        # Each label sits above the point it enters, splayed out just enough to
        # keep the words apart, so its arrow drops from the centre of the word.
        target = mouth_l + (mouth_r - mouth_l) * (index + 0.5) / len(sources)
        x = centre + (target - centre) * 1.55
        c.text(x, label_y, name, size=label_size, fill=draw.INK)
        x0, y0 = x, label_y + 13
        x1, y1 = target, mouth_y - 6
        length = math.hypot(x1 - x0, y1 - y0) or 1
        dx, dy = (x1 - x0) / length, (y1 - y0) / length
        c.line(x0, y0, x1, y1, stroke=draw.SLATE, width=2)
        head(x1, y1, dx, dy, draw.SLATE)

    # ---- the funnel ------------------------------------------------------
    c.parts.append(
        f'<path d="M {mouth_l},{mouth_y} L {mouth_r},{mouth_y} '
        f"L {throat_r},{throat_y} L {throat_r},{spout_y} "
        f'L {throat_l},{spout_y} L {throat_l},{throat_y} Z" fill="{draw.PALE}"/>'
    )
    c.text(centre, mouth_y + 62, f"{f.candidates:,}", size=58, fill=draw.INK)
    c.text(
        centre,
        mouth_y + 92,
        "Candidates found",
        size=15,
        fill=draw.INK,
        spacing=2.2,
        upper=True,
    )

    # ---- what leaves, and where ------------------------------------------
    first, last = mouth_y + 112, throat_y - 16
    gap = (last - first) / max(len(f.stages) - 1, 1)
    for index, (label, count) in enumerate(f.stages):
        y = first + gap * index
        left, right = wall(y)
        rightward = index % 2 == 0
        edge = right if rightward else left
        tip = edge + (78 if rightward else -78)
        c.line(edge, y, tip, y, stroke=draw.RULE, width=2)
        head(tip, y, 1.0 if rightward else -1.0, 0.0, draw.RULE)
        anchor = "start" if rightward else "end"
        text_x = tip + (18 if rightward else -18)
        c.text(text_x, y + 1, f"{count:,}", size=26, fill=draw.SLATE, anchor=anchor)
        c.text(
            text_x,
            y + 19,
            label,
            size=13,
            fill=draw.MUTED,
            anchor=anchor,
            spacing=1.4,
            upper=True,
        )

    # ---- what comes out --------------------------------------------------
    # Below the spout, not inside it: what leaves the funnel has left it.
    # Three outcomes, not one -- a general seismology tool that reads DAS and a
    # distributed-temperature package are both real findings, and burying them
    # in "out of scope" loses them.
    c.line(centre, spout_y + 6, centre, spout_y + 30, stroke=draw.AMBER, width=3.5)
    head(centre, spout_y + 36, 0.0, 1.0, draw.AMBER, size=8)

    outputs = (
        (
            centre - 300,
            f"{f.supporting}",
            ("Seismology tools", "that also read DAS"),
            f.supporting_names,
            draw.SLATE,
            32,
        ),
        (centre, f"{f.in_scope}", ("DAS projects",), (), draw.AMBER, 58),
        (
            centre + 300,
            f"{f.other_fiber}",
            ("Other fibre sensing", "temperature or strain"),
            f.other_fiber_names,
            draw.SLATE,
            32,
        ),
    )
    for x, number, lines, names, colour, size in outputs:
        c.text(x, spout_y + 96, number, size=size, fill=colour)
        for offset, line in enumerate(lines):
            c.text(
                x,
                spout_y + 126 + offset * 21,
                line,
                size=15,
                fill=draw.INK if size > 40 else draw.MUTED,
                spacing=2.2,
                upper=offset == 0,
            )
        # Naming the flanking groups is the point of splitting them out: five
        # and seven are only interesting if a reader can see which projects.
        for offset, name in enumerate(names):
            c.text(
                x,
                spout_y + 126 + len(lines) * 21 + 14 + offset * 20,
                name,
                size=15,
                fill=draw.INK,
            )
    return c.to_svg()


#: Always named, whatever the data does. Pinning the whole set means the
#: figure keeps saying the same thing when the catalogue grows: a project that
#: is labelled today does not silently lose its label to a busier newcomer.
PINNED = (
    "dastools",
    "dascore",
    "xdas",
    "das4whales",
    "daspy",
    "fiberis",
    "fiberwatch-cli",
    "das-ani",
    "derzug",
    "dasexplorer",
    "das-processing-pipeline",
)

#: How many labels to aim for, and how many rows must separate two of them.
LABEL_BANDS = 10
LABEL_GAP = 4


def _label_rows(traces: Sequence[Trace]) -> set[int]:
    """Choose which rows to name: the pinned projects, then the busiest in
    each band of rows, skipping any that would crowd a label already chosen.

    Picking by band rather than by a fixed list keeps the labels spread down
    the plot as the catalogue grows, and picking the busiest within a band
    means the named project is one a reader is likely to recognise.
    """
    chosen = {i for i, t in enumerate(traces) if t.project_id in PINNED}
    total = len(traces)
    for band in range(LABEL_BANDS):
        lo = round(band * total / LABEL_BANDS)
        hi = round((band + 1) * total / LABEL_BANDS)
        rows = range(lo, min(hi, total))
        if not rows:
            continue
        row = max(rows, key=lambda i: traces[i].commits)
        if all(abs(row - taken) >= LABEL_GAP for taken in chosen):
            chosen.add(row)
    return chosen


#: Sequential ramp for commit counts, low to high, in the figure's own palette.
COMMIT_RAMP = ("#f4efe3", "#e4dccb", "#d9a63f", "#c98500", "#8a5f1c", "#5c3d0f")


def _ramp(t: float) -> str:
    """Colour for a normalised position on :data:`COMMIT_RAMP`."""
    t = min(max(t, 0.0), 1.0)
    span = len(COMMIT_RAMP) - 1
    lo = min(int(t * span), span - 1)
    frac = t * span - lo
    a, b = COMMIT_RAMP[lo], COMMIT_RAMP[lo + 1]
    parts = []
    for channel in (1, 3, 5):
        av = int(a[channel : channel + 2], 16)
        bv = int(b[channel : channel + 2], 16)
        parts.append(round(av + (bv - av) * frac))
    return "#" + "".join(f"{v:02x}" for v in parts)


def record_section_plate(section: RecordSection) -> str:
    """One bar per project, ordered by first commit and shaded by commit count.

    Sized 16:9 for a slide. A bar spans the project's first commit to its last,
    so the diagonal front of onsets is the shape; colour carries how much work
    went in, on a log scale because the busiest repository has three orders of
    magnitude more commits than the quietest.
    """
    import math

    width, height = 1680, 945
    top, bottom = 236.0, 762.0
    left, right = 150.0, 1560.0
    rows = len(section.traces)
    row_h = (bottom - top) / max(rows - 1, 1)
    periods = section.periods
    step = (right - left) / max(len(periods) - 1, 1)
    index_of = {period: i for i, period in enumerate(periods)}
    # Colour is the commits in each month, not the project's lifetime total,
    # so a bar shows when the work happened rather than only how much.
    lo, hi = 0.0, math.log10(max(section.peak_period, 2))

    def shade(commits: int) -> str:
        return _ramp((math.log10(max(commits, 1)) - lo) / (hi - lo or 1))

    c = draw.Canvas(
        width=width,
        height=height,
        title="The DAS record section",
        desc=(
            f"{rows} projects, one bar each, ordered by first commit from "
            f"{periods[0]} to {periods[-1]}, shaded by commit count. "
            f"{section.since_2020} began in 2020 or later."
        ),
    )

    # colour bar
    bar_x, bar_y, bar_w, bar_h = 620.0, 166.0, 440.0, 14.0
    slices = 120
    for i in range(slices):
        c.rect(
            bar_x + bar_w * i / slices,
            bar_y,
            bar_w / slices + 0.6,
            bar_h,
            fill=_ramp(i / (slices - 1)),
        )
    for value in (1, 10, 100):
        if not lo <= math.log10(value) <= hi:
            continue
        x = bar_x + bar_w * (math.log10(value) - lo) / (hi - lo)
        c.line(x, bar_y + bar_h, x, bar_y + bar_h + 6, stroke=draw.RULE, width=1.5)
        c.text(x, bar_y + bar_h + 26, f"{value:,}", size=16, fill=draw.MUTED)
    c.text(
        bar_x - 16,
        bar_y + 12,
        "commits / quarter",
        size=18,
        fill=draw.INK,
        anchor="end",
    )

    for i, period in enumerate(periods):
        if period.endswith("-01"):
            x = left + step * i
            c.line(x, top - 22, x, bottom + 20, stroke=draw.PALE, width=1.5)
            c.text(x, bottom + 60, period[:4], size=22, fill=draw.MUTED)

    named = _label_rows(section.traces)
    thickness = max(row_h - 1.6, 2.4)
    for row, trace in enumerate(section.traces):
        y = top + row * row_h - thickness / 2
        x0 = left + step * index_of[trace.first_period]
        x1 = left + step * index_of[trace.periods[-1][0]]
        # The pale underlay carries the lifespan, including silent months; the
        # cells above it carry the months that saw work.
        c.rect(x0, y, max(x1 - x0, 2.0), thickness, fill=draw.PALE)
        for period, commits in trace.periods:
            c.rect(
                left + step * index_of[period],
                y,
                max(step, 1.6),
                thickness,
                fill=shade(commits),
            )
        if row in named:
            # Centred on the bar, not hung from its lower edge: the type is
            # several times the bar's height.
            c.text(
                x0 - 14,
                y + thickness / 2 + 6.5,
                trace.name,
                size=19,
                fill=draw.INK,
                anchor="end",
            )

    c.text(
        840,
        884,
        f"{section.since_2020} of {rows} projects began in 2020 or later",
        size=28,
        fill=draw.FAINT,
        italic=True,
    )
    return c.to_svg()


#: Licence colours, shared with the licence figure so a reader who has seen one
#: reads the other without relearning.
LICENCE_COLOUR = {
    "osi-approved": draw.AMBER,
    "source-available": draw.CREAM,
    "unlicensed": draw.SLATE,
    "unknown": draw.GRAY,
}
LICENCE_NAME = {
    "osi-approved": "OSI-approved",
    "source-available": "Source-available",
    "unlicensed": "No licence",
    "unknown": "Unresolved",
}


def language_licence_plate(d: LanguageLicence) -> str:
    """What the ecosystem is written in, and on what terms it may be reused."""
    width, height = 1680, 800
    left, right = 330.0, 1250.0
    top = 236.0
    row_h = 58.0
    widest = max((r.projects for r in d.rows), default=1)
    scale = (right - left) / widest

    c = draw.Canvas(
        width=width,
        height=height,
        title="Language and licence",
        desc=(
            f"{d.projects} DAS projects by primary language, split by reuse terms. "
            f"{d.osi} are OSI-approved; {d.lines:,} lines of source."
        ),
    )
    c.text(
        840,
        88,
        "What it is written in, and how it may be reused",
        size=36,
        fill=draw.INK,
    )

    cursor = 330.0
    for licence, count in d.licence_totals:
        c.rect(cursor, 166, 26, 12, fill=LICENCE_COLOUR.get(licence, draw.GRAY), rx=2)
        label = f"{LICENCE_NAME.get(licence, licence)}  {count}"
        c.text(cursor + 36, 178, label, size=17, fill=draw.INK, anchor="start")
        cursor += 36 + len(label) * 8.4 + 46

    for index, row in enumerate(d.rows):
        y = top + index * row_h
        c.text(left - 22, y + 8, row.language, size=22, fill=draw.INK, anchor="end")
        segments = [
            (licence, float(count), LICENCE_COLOUR.get(licence, draw.GRAY))
            for licence, count in row.by_licence
        ]
        c.bar_stack(left, y - 15, row.projects * scale, 30, segments, min_visible=0.0)
        for licence, count in row.by_licence:
            offset = sum(
                n
                for lic, n in row.by_licence
                if LICENCE_ORDER.index(lic) < LICENCE_ORDER.index(licence)
            )
            span = count * scale
            if span < 26:
                continue
            c.text(
                left + offset * scale + span / 2,
                y + 8,
                f"{count}",
                size=19,
                fill=draw.PAPER
                if licence in ("osi-approved", "unlicensed")
                else draw.INK,
            )
        tail = f"{row.lines:,} lines" if row.lines else "no source published"
        c.text(
            left + row.projects * scale + 22,
            y + 7,
            tail,
            size=18,
            fill=draw.MUTED,
            anchor="start",
            italic=True,
        )

    return c.to_svg()


#: A categorical sequence in the figure family's palette, ordered so adjacent
#: entries stay distinguishable when stacked directly against each other.
#: A ramp for orderings, dark to light. It deliberately never reaches the page
#: colour: the first stop has to be visible against white, which is why the
#: commit ramp -- which starts almost at paper -- cannot be reused here.
SEQUENTIAL_RAMP = (
    "#e0cba4",
    "#d2a951",
    "#c48200",
    "#a06a10",
    "#7a5218",
    "#573c14",
    "#33230b",
)


def _sequential(t: float) -> str:
    """Colour for a normalised position on :data:`SEQUENTIAL_RAMP`."""
    t = min(max(t, 0.0), 1.0)
    span = len(SEQUENTIAL_RAMP) - 1
    lo = min(int(t * span), span - 1)
    frac = t * span - lo
    a, b = SEQUENTIAL_RAMP[lo], SEQUENTIAL_RAMP[lo + 1]
    parts = []
    for channel in (1, 3, 5):
        av = int(a[channel : channel + 2], 16)
        bv = int(b[channel : channel + 2], 16)
        parts.append(round(av + (bv - av) * frac))
    return "#" + "".join(f"{v:02x}" for v in parts)


CATEGORY_PALETTE = (
    "#c98500",
    "#4b4b50",
    "#d9a63f",
    "#8a5f1c",
    "#b8b0a0",
    "#e4dccb",
    "#5c3d0f",
    "#a3825a",
)


def stacked_years_plate(
    growth: Growth,
    title: str,
    standfirst: str,
    closing: str = "",
    sequential: bool = False,
) -> str:
    """Commits per year, stacked by an arbitrary grouping.

    The generic form behind the category and cohort figures: `growth_plate`
    hard-codes the three DAS-focus classes and their colours, which is right
    for that figure and wrong for any other grouping.
    """
    years = growth.years
    # An ordered grouping gets a colour bar instead of a swatch legend, which
    # frees the foot of the figure and says "these categories are a sequence".
    width = 1680
    # Vertical rhythm is derived, not tabulated: dropping the standfirst or the
    # closing line pulls everything below it up, so a figure that carries
    # neither does not sit above a band of empty paper.
    head = 114.0 if standfirst else 74.0
    if sequential:
        bar_y = head + 36.0
        top = bar_y + 86.0
        bottom = top + 330.0
        height = bottom + 70.0 + (56.0 if closing else 12.0)
    else:
        top, bottom = 170.0, 500.0
        height = 720.0
    # A narrower band than the full canvas. Eight bars spread over 1,400pt read
    # as eight separate charts; closing the gaps makes them one series.
    left, right = 300.0, 1380.0
    totals = [sum(vals[i] for _, vals in growth.by_class) for i in range(len(years))]
    peak = max(totals, default=1) or 1
    slot = (right - left) / max(len(years), 1)
    bar = min(slot * 0.80, 110)
    # A grouping that is itself ordered -- cohorts by year -- reads as strata
    # only if the colours run with it. A categorical palette makes the same
    # stack look like unrelated blocks.
    groups = len(growth.by_class)
    colour_of = {
        key: (
            _sequential(i / max(groups - 1, 1))
            if sequential
            else CATEGORY_PALETTE[i % len(CATEGORY_PALETTE)]
        )
        for i, (key, _) in enumerate(growth.by_class)
    }

    c = draw.Canvas(
        width=width,
        height=height,
        title=title,
        desc=(
            f"{sum(totals):,} commits between {years[0]} and {years[-1]}, "
            f"in {len(growth.by_class)} groups."
        ),
    )
    c.text(840, 76, title, size=34, fill=draw.INK)
    if standfirst:
        c.text(840, 114, standfirst, size=21, fill=draw.MUTED, italic=True)
    c.line(left, bottom, right, bottom, stroke=draw.RULE, width=2)

    for index, year in enumerate(years):
        centre = left + slot * (index + 0.5)
        cursor = bottom
        for key, values in growth.by_class:
            share = values[index]
            if not share:
                continue
            span = (bottom - top) * share / peak
            cursor -= span
            # A hairline of page colour between bands: adjacent stops on a
            # ramp are close by construction, and without a gap two cohorts
            # read as one.
            c.rect(
                centre - bar / 2,
                cursor,
                bar,
                max(span - 1.4, 0.9),
                fill=colour_of[key],
            )
        c.text(centre, bottom + 32, str(year), size=draw.SUB_SM, fill=draw.MUTED)
        if year == years[-1]:
            c.text(
                centre,
                bottom + 56,
                "part year",
                size=draw.TINY,
                fill=draw.FAINT,
                italic=True,
            )
        c.text(centre, cursor - 14, f"{totals[index]:,}", size=draw.TINY, fill=draw.INK)

    if sequential:
        # An ordered grouping gets a colour bar, not eight swatches: the bar
        # says the categories are a sequence, and it frees the foot of the
        # figure that three rows of legend used to take.
        bar_x, bar_w, bar_h = 620.0, 460.0, 15.0
        slices = 140
        for i in range(slices):
            c.rect(
                bar_x + bar_w * i / slices,
                bar_y,
                bar_w / slices + 0.7,
                bar_h,
                fill=_sequential(i / (slices - 1)),
            )
        keys = [key for key, _ in growth.by_class]
        for index, key in enumerate(keys):
            # Both ends, then every other stop -- but never one adjacent to the
            # final tick, which would print two labels on top of each other.
            last = len(keys) - 1
            if index not in (0, last) and (index % 2 or index >= last - 1):
                continue
            x = bar_x + bar_w * (index + 0.5) / len(keys)
            c.line(x, bar_y + bar_h, x, bar_y + bar_h + 6, stroke=draw.RULE, width=1.5)
            c.text(
                x,
                bar_y + bar_h + 26,
                key.replace("Started ", ""),
                size=16,
                fill=draw.MUTED,
            )
        c.text(
            bar_x - 18,
            bar_y + 13,
            "project started",
            size=18,
            fill=draw.INK,
            anchor="end",
        )
    else:
        c.spine(100, 1580, 580, [])
        per_row = 3
        for index, (key, total) in enumerate(growth.class_totals):
            column, row = index % per_row, index // per_row
            x = 300.0 + column * 430
            y = 618.0 + row * 34
            c.rect(x, y - 12, 22, 12, fill=colour_of[key], rx=2)
            c.text(
                x + 32,
                y,
                f"{key}  {total:,}",
                size=draw.SUB_SM,
                fill=draw.INK,
                anchor="start",
            )
    if closing:
        c.text(840, height - 26, closing, size=draw.SUB, fill=draw.FAINT, italic=True)
    return c.to_svg()


#: One colour per gate, taken in order from the shared categorical palette so
#: this figure sits in the same family as the growth plates. The gate headings
#: name each group directly, so no reader has to hold a legend in mind, and
#: every bar carries its own count -- the pale amber does not clear 3:1 against
#: paper, and a bar that faint has to say its number rather than be measured.
GATE_COLOUR = dict(
    zip(
        (
            "Can I get it?",
            "Can I trust it?",
            "Can I learn it?",
            "Will it last?",
        ),
        CATEGORY_PALETTE,
        strict=False,
    )
)


def _wrap(text: str, limit: int) -> list[str]:
    """Greedily break text into lines of at most ``limit`` characters.

    A column of this figure is narrower than several of its labels, and SVG
    does not wrap. Counting characters is crude but the type is one size and
    one face, so it is close enough to keep two neighbouring notes apart.
    """
    lines: list[str] = []
    for word in text.split():
        if lines and len(lines[-1]) + 1 + len(word) <= limit:
            lines[-1] += f" {word}"
        else:
            lines.append(word)
    return lines or [text]


def engineering_plate(eng: Engineering) -> str:
    """What the ecosystem does that lets a stranger depend on its software.

    One bar per practice, coloured by the question it answers. The bars are
    shares of the same denominator -- every catalogued DAS project -- so their
    heights are directly comparable, which is the whole reason for putting
    seven unrelated practices on one axis.
    """
    width, height = WIDTH, 620
    baseline, full = 470.0, 380.0
    bar_w, inner_gap, gate_gap = 122.0, 24.0, 68.0
    assert eng.projects and eng.practices, "an empty catalogue has no bars to draw"

    groups = [(gate, eng.by_gate(gate)) for gate in eng.gates]
    span = sum(
        len(members) * bar_w + (len(members) - 1) * inner_gap for _, members in groups
    ) + gate_gap * (len(groups) - 1)
    left = (width - span) / 2

    c = draw.Canvas(
        width=width,
        height=height,
        title="Can this be depended on?",
        desc=(
            f"{len(eng.practices)} engineering practices across "
            f"{eng.projects} DAS projects: "
            + ", ".join(
                f"{p.label.lower()} {round(100 * p.projects / eng.projects)}%"
                for p in eng.practices
            )
            + "."
        ),
    )
    # Gridlines first, so every bar sits on top of them rather than being cut.
    for share in (0.25, 0.50, 0.75, 1.00):
        y = baseline - full * share
        c.line(left - 20, y, left + span + 20, y, stroke=draw.PALE, width=1.5)

    cursor = left
    for gate, members in groups:
        colour = GATE_COLOUR.get(gate, draw.GRAY)
        group_w = len(members) * bar_w + (len(members) - 1) * inner_gap
        c.line(cursor, 62, cursor + group_w, 62, stroke=colour, width=3)
        c.text(
            cursor + group_w / 2,
            44,
            gate,
            size=draw.SUB,
            fill=draw.INK,
            italic=True,
        )
        for practice in members:
            share = practice.projects / eng.projects
            bar_h = full * share
            c.rect(cursor, baseline - bar_h, bar_w, bar_h, fill=colour, rx=3)
            c.text(
                cursor + bar_w / 2,
                baseline - bar_h - 46,
                f"{round(share * 100)}%",
                size=draw.MID,
                fill=draw.INK,
            )
            c.text(
                cursor + bar_w / 2,
                baseline - bar_h - 18,
                f"{practice.projects} of {eng.projects}",
                size=draw.TINY,
                fill=draw.MUTED,
            )
            y = baseline + 36
            for line in _wrap(practice.label, 14):
                c.text(cursor + bar_w / 2, y, line, size=draw.SUB_SM, fill=draw.INK)
                y += 26
            cursor += bar_w + inner_gap
        cursor += gate_gap - inner_gap

    c.line(left - 20, baseline, left + span + 20, baseline, stroke=draw.RULE, width=2)
    return c.to_svg()
