"""Measurements behind each figure, read from the repository.

Every number a figure prints comes from here, so a figure cannot drift from the
data it claims to describe. Each measurement is a frozen dataclass with the
inputs it was computed from recorded on it, and each carries a `sidecar()` so
the published figures can ship a machine-checkable copy of their own numbers.
"""

from __future__ import annotations

import csv
import re
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from oss_das.core import PATHS, load_projects

#: Author identities that are automation. Counting them as contributors would
#: credit the ecosystem with people who do not exist.
BOT = re.compile(r"(\[bot\]|dependabot|github-action|pre-commit-ci|renovate)", re.I)


def _read(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def unique_authors(rows: list[dict[str, str]]) -> int:
    """Count distinct human authors across commit rows.

    Git identities fork: the same person commits as two names, or one name
    against several addresses. Names and addresses are therefore joined into
    one identity graph and the components counted, rather than taking distinct
    names (which merges two people who share a name) or distinct addresses
    (which splits one person across their laptop and their CI).
    """
    parent: dict[tuple[str, str], tuple[str, str]] = {}

    def find(node: tuple[str, str]) -> tuple[str, str]:
        parent.setdefault(node, node)
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node

    def union(a: tuple[str, str], b: tuple[str, str]) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    people = set()
    for row in rows:
        name, email = row["author_name"].strip(), row["author_email"].strip()
        if BOT.search(name) or BOT.search(email):
            continue
        union(("name", name.lower()), ("email", email.lower()))
    for row in rows:
        name, email = row["author_name"].strip(), row["author_email"].strip()
        if BOT.search(name) or BOT.search(email):
            continue
        people.add(find(("name", name.lower())))
    return len(people)


@dataclass(frozen=True)
class EcosystemTotals:
    """The four headline numbers, all over the same set of projects."""

    projects: int
    contributors: int
    commits: int
    lines: int
    unmirrored: tuple[str, ...]

    def sidecar(self) -> dict[str, Any]:
        return asdict(self)


def ecosystem_totals(data_dir: Path | None = None) -> EcosystemTotals:
    data_dir = data_dir or PATHS.root / "data"
    included = {p.id for p in load_projects() if p.status.value == "included"}
    commits = [
        r for r in _read(data_dir / "commits_all.csv") if r["project_id"] in included
    ]
    lines = sum(
        int(r["lines"])
        for r in _read(data_dir / "loc.csv")
        if r["project_id"] in included
    )
    mirrored = {r["project_id"] for r in _read(data_dir / "commits_all.csv")}
    human = [
        r
        for r in commits
        if not (BOT.search(r["author_name"]) or BOT.search(r["author_email"]))
    ]
    return EcosystemTotals(
        projects=len(included),
        contributors=unique_authors(commits),
        commits=len(human),
        lines=lines,
        unmirrored=tuple(sorted(included - mirrored)),
    )


@dataclass(frozen=True)
class PipelineFlow:
    """What each stage of the pipeline consumed and produced."""

    snapshot: str
    github_searches: int
    gitlab_searches: int
    gitea_searches: int
    namespace_walks: int
    probes_ok: int
    probes_failed: int
    failed_hosts: tuple[str, ...]
    rows_retrieved: int
    candidates: int
    unreviewed: int
    reviewed: int
    catalogued: int
    included: int
    metric_rows: int
    metric_hosts: tuple[str, ...]
    summarised: int
    summary_models: tuple[str, ...]

    def sidecar(self) -> dict[str, Any]:
        return asdict(self)


def pipeline_flow(snapshot_date: str) -> PipelineFlow:
    snap = PATHS.snapshot(snapshot_date)
    cov = _read(snap / "discovery_coverage.csv")
    cand = _read(snap / "candidates.csv")
    metrics = _read(snap / "metrics.csv")

    kinds = Counter((c["kind"], c["probe"]) for c in cov)
    failed = [c for c in cov if c["status"] != "ok"]
    status = Counter(c["catalog_status"] for c in cand)

    summaries = 0
    models: Counter[str] = Counter()
    import yaml

    for path in sorted((PATHS.curated).glob("*.md")):
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---"):
            continue
        block = (yaml.safe_load(text.split("---")[1]) or {}).get("summary")
        if not block:
            continue
        summaries += 1
        models.update(block.get("models") or [])

    catalogued = len(load_projects())
    return PipelineFlow(
        snapshot=snapshot_date,
        github_searches=kinds[("github", "search")],
        gitlab_searches=kinds[("gitlab", "search")],
        gitea_searches=kinds[("gitea", "search")],
        namespace_walks=sum(
            n for (_, probe), n in kinds.items() if probe == "namespace"
        ),
        probes_ok=len(cov) - len(failed),
        probes_failed=len(failed),
        failed_hosts=tuple(sorted({c["host"] for c in failed})),
        rows_retrieved=sum(int(c["retrieved"]) for c in cov if c["retrieved"]),
        candidates=len(cand),
        unreviewed=status["unreviewed"],
        reviewed=len(cand) - status["unreviewed"],
        catalogued=catalogued,
        included=status["included"],
        metric_rows=len(metrics),
        metric_hosts=tuple(
            sorted({m["source_url"].split("/")[2] for m in metrics if m["source_url"]})
        ),
        summarised=summaries,
        summary_models=tuple(sorted(models)),
    )


#: Keyword groupings over the human-written `decision_reason` on catalogued
#: projects. The catalogue records a sentence per project, not a category, so a
#: figure that counts reasons has to group them. The rules are listed here, in
#: order, rather than hidden in a plate: a reader can check the grouping, and a
#: reason matching nothing lands in "other" instead of being silently dropped.
HELD_BACK_RULES: tuple[tuple[str, str], ...] = (
    (
        "duplicate",
        r"\bduplicate\b|mirrors the already|upstream of the already|fork of the already",
    ),
    ("acronym-collision", r"acronym collision"),
    (
        "general-toolkit",
        r"general (seismolog|surface-wave|seismic)|added DAS support|mentions DAS in passing",
    ),
    (
        "other-fiber",
        r"distributed temperature|distributed strain|modality is|spans DTS",
    ),
    (
        "no-source",
        r"private and returns 404|no published source|only a README|publishes only|nothing to reuse",
    ),
    ("teaching", r"tutorial material|teaching"),
    ("not-reusable", r"demonstration scripts|no packaging|four demonstration"),
)


@dataclass(frozen=True)
class SelectionFunnel:
    """How the candidate pool narrows to the in-scope catalogue."""

    snapshot: str
    candidates: int
    reviewed: int
    in_scope: int
    unreviewed: int
    held_back: tuple[tuple[str, int], ...]

    @property
    def held_back_total(self) -> int:
        return sum(n for _, n in self.held_back)

    def sidecar(self) -> dict[str, Any]:
        return {**asdict(self), "held_back_total": self.held_back_total}


def _classify_reason(reason: str) -> str:
    for name, pattern in HELD_BACK_RULES:
        if re.search(pattern, reason, re.I):
            return name
    return "other"


def selection_funnel(
    snapshot_date: str, data_dir: Path | None = None
) -> SelectionFunnel:
    data_dir = data_dir or PATHS.root / "data"
    projects = load_projects()
    cand = _read(PATHS.snapshot(snapshot_date) / "candidates.csv")
    unreviewed = sum(1 for c in cand if c["catalog_status"] == "unreviewed")

    buckets: Counter[str] = Counter()
    for project in projects:
        if project.status.value == "included":
            continue
        buckets[_classify_reason(project.decision_reason)] += 1

    triage = data_dir / "candidate_triage.yml"
    if triage.exists():
        import yaml

        doc = yaml.safe_load(triage.read_text(encoding="utf-8")) or {}
        catalogued = {p.repository.lower() for p in projects}
        for key, entries in doc.items():
            if key == "counts" or not isinstance(entries, list):
                continue
            for entry in entries:
                decided = entry.get("decided", entry.get("proposed", ""))
                if decided in ("include", "undecided"):
                    continue
                if entry["repository"].lower() in catalogued:
                    continue  # already counted through its curated record
                buckets[decided.split(":")[-1]] += 1

    in_scope = sum(1 for p in projects if p.status.value == "included")
    held = tuple(sorted(buckets.items(), key=lambda kv: (-kv[1], kv[0])))
    return SelectionFunnel(
        snapshot=snapshot_date,
        candidates=len(cand),
        reviewed=len(cand) - unreviewed,
        in_scope=in_scope,
        unreviewed=unreviewed,
        held_back=held,
    )


@dataclass(frozen=True)
class ProjectAge:
    """One project's development history, for the maturity comparison."""

    project_id: str
    name: str
    role: str
    commits: int
    authors: int
    days: int
    lines: int


@dataclass(frozen=True)
class Maturity:
    """Viewers against frameworks, on sustained development."""

    projects: tuple[ProjectAge, ...]

    def by_role(self, role: str) -> tuple[ProjectAge, ...]:
        return tuple(p for p in self.projects if p.role == role)

    def sidecar(self) -> dict[str, Any]:
        return {"projects": [asdict(p) for p in self.projects]}


def _role(project: Any) -> str:
    if project.primary_category == "core-framework":
        return "framework"
    if (
        project.primary_category == "visualization-annotation"
        or "desktop-application" in project.capabilities
    ):
        return "viewer"
    return "other"


def maturity(data_dir: Path | None = None) -> Maturity:
    data_dir = data_dir or PATHS.root / "data"
    from datetime import date

    rows: dict[str, list[dict[str, str]]] = {}
    for row in _read(data_dir / "commits_all.csv"):
        rows.setdefault(row["project_id"], []).append(row)
    lines: Counter[str] = Counter()
    for row in _read(data_dir / "loc.csv"):
        lines[row["project_id"]] += int(row["lines"])

    out = []
    for project in load_projects():
        if project.status.value == "excluded":
            continue
        history = rows.get(project.id, [])
        if not history:
            continue
        dates = sorted(r["authored_at"][:10] for r in history)
        span = (date.fromisoformat(dates[-1]) - date.fromisoformat(dates[0])).days
        out.append(
            ProjectAge(
                project_id=project.id,
                name=project.name,
                role=_role(project),
                commits=len(history),
                authors=unique_authors(history),
                days=span,
                lines=lines[project.id],
            )
        )
    return Maturity(projects=tuple(sorted(out, key=lambda p: -p.commits)))


@dataclass(frozen=True)
class LicenceMix:
    """Reuse terms, counted by project and by line of code."""

    by_class: tuple[tuple[str, int], ...]
    lines_by_class: tuple[tuple[str, int], ...]
    projects: int
    lines: int

    def sidecar(self) -> dict[str, Any]:
        return asdict(self)


def licence_mix(data_dir: Path | None = None) -> LicenceMix:
    data_dir = data_dir or PATHS.root / "data"
    lines: Counter[str] = Counter()
    for row in _read(data_dir / "loc.csv"):
        lines[row["project_id"]] += int(row["lines"])
    counts: Counter[str] = Counter()
    line_counts: Counter[str] = Counter()
    total_projects = 0
    for project in load_projects():
        if project.status.value == "excluded":
            continue
        total_projects += 1
        counts[project.license_class.value] += 1
        line_counts[project.license_class.value] += lines[project.id]
    order = ("osi-approved", "source-available", "unlicensed", "unknown")
    key = lambda c: order.index(c[0]) if c[0] in order else len(order)  # noqa: E731
    return LicenceMix(
        by_class=tuple(sorted(counts.items(), key=key)),
        lines_by_class=tuple(sorted(line_counts.items(), key=key)),
        projects=total_projects,
        lines=sum(line_counts.values()),
    )


@dataclass(frozen=True)
class Composition:
    """What the corpus is written in, and how little of it is packaged."""

    languages: tuple[tuple[str, int], ...]
    total_lines: int
    projects: int
    with_pypi: int
    with_conda: int
    with_julia: int
    with_none: int

    def sidecar(self) -> dict[str, Any]:
        return asdict(self)


def composition(data_dir: Path | None = None) -> Composition:
    data_dir = data_dir or PATHS.root / "data"
    included = {p.id for p in load_projects() if p.status.value == "included"}
    langs: Counter[str] = Counter()
    for row in _read(data_dir / "loc.csv"):
        if row["project_id"] in included:
            langs[row["language"]] += int(row["lines"])
    catalogued = [p for p in load_projects() if p.status.value != "excluded"]
    return Composition(
        languages=tuple(langs.most_common()),
        total_lines=sum(langs.values()),
        projects=len(catalogued),
        with_pypi=sum(1 for p in catalogued if p.registries.pypi),
        with_conda=sum(1 for p in catalogued if p.registries.conda),
        with_julia=sum(1 for p in catalogued if p.registries.julia),
        with_none=sum(
            1
            for p in catalogued
            if not (p.registries.pypi or p.registries.conda or p.registries.julia)
        ),
    )


@dataclass(frozen=True)
class Growth:
    """Commits per year, split by how central DAS is to the project."""

    years: tuple[int, ...]
    by_class: tuple[tuple[str, tuple[int, ...]], ...]
    class_totals: tuple[tuple[str, int], ...]

    def sidecar(self) -> dict[str, Any]:
        return asdict(self)


def growth(data_dir: Path | None = None) -> Growth:
    data_dir = data_dir or PATHS.root / "data"
    import yaml

    focus_path = data_dir / "focus.yml"
    focus = {}
    if focus_path.exists():
        focus = (yaml.safe_load(focus_path.read_text(encoding="utf-8")) or {}).get(
            "projects", {}
        ) or {}
    counts: dict[str, Counter[int]] = {}
    for row in _read(data_dir / "commits_all.csv"):
        if row["status"] == "excluded":
            continue
        cls = focus.get(row["project_id"], "das-native")
        year = int(row["authored_at"][:4])
        counts.setdefault(cls, Counter())[year] += 1
    years = sorted({y for c in counts.values() for y in c})
    series = tuple(
        (cls, tuple(counts[cls].get(y, 0) for y in years))
        for cls in sorted(counts, key=lambda c: -sum(counts[c].values()))
    )
    totals = tuple((cls, sum(vals)) for cls, vals in series)
    return Growth(years=tuple(years), by_class=series, class_totals=totals)


#: The sources discovery actually reads, and the ones it does not yet. Drawn as
#: solid and dashed inflows: a source that has never run must not appear on a
#: methodology slide as though it had.
SOURCES_SEARCHED: tuple[str, ...] = (
    "GitHub",
    "GitLab",
    "Gitea",
    "Org sweeps",
    "Registries",
    "Literature",
)
SOURCES_PENDING: tuple[str, ...] = ()

#: How the rejection reasons are grouped for the funnel. Six reasons is more
#: outflows than a funnel can carry legibly, so near neighbours are merged --
#: but every candidate still leaves through exactly one of them.
FUNNEL_GROUPS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("Not reusable", ("not-reusable",)),
    ("Paper code", ("paper-code",)),
    ("Duplicate or collision", ("duplicate", "acronym-collision")),
    ("Teaching or no source", ("teaching", "no-source")),
)


@dataclass(frozen=True)
class Funnel:
    """Every discovered candidate, leaving by exactly one route.

    The stages partition the candidate pool: they sum to the total by
    construction, because each is a count of a mutually exclusive
    `catalog_status` in the snapshot rather than a separately gathered figure.
    A funnel drawn from numbers that do not add up is a lie about a subtraction.
    """

    snapshot: str
    candidates: int
    stages: tuple[tuple[str, int], ...]
    in_scope: int
    searched: tuple[str, ...]
    pending: tuple[str, ...]

    @property
    def accounted(self) -> int:
        return sum(n for _, n in self.stages) + self.in_scope

    def sidecar(self) -> dict[str, Any]:
        return {**asdict(self), "accounted": self.accounted}


def funnel(snapshot_date: str, data_dir: Path | None = None) -> Funnel:
    data_dir = data_dir or PATHS.root / "data"
    import yaml

    cand = _read(PATHS.snapshot(snapshot_date) / "candidates.csv")
    status = Counter(c["catalog_status"] for c in cand)

    ledger: dict[str, dict[str, str]] = {}
    path = data_dir / "rejected.yml"
    if path.exists():
        ledger = (yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get(
            "rejections", {}
        ) or {}

    reasons: Counter[str] = Counter()
    for row in cand:
        if row["catalog_status"] != "rejected":
            continue
        key = f"{row['forge_host']}/{row['repository']}".lower()
        entry = ledger.get(key)
        reasons[entry["reason"] if entry else "not-reusable"] += 1

    stages: list[tuple[str, int]] = [("Awaiting review", status["unreviewed"])]
    for label, keys in FUNNEL_GROUPS:
        stages.append((label, sum(reasons[k] for k in keys)))
    stages.append(("Out of scope", status["excluded"] + status["watchlist"]))

    built = Funnel(
        snapshot=snapshot_date,
        candidates=len(cand),
        stages=tuple(s for s in stages if s[1]),
        in_scope=status["included"],
        searched=SOURCES_SEARCHED,
        pending=SOURCES_PENDING,
    )
    # A funnel that does not balance is a bug, not a rounding difference.
    assert built.accounted == built.candidates, (
        f"funnel does not balance: {built.accounted} accounted for, "
        f"{built.candidates} discovered"
    )
    return built
