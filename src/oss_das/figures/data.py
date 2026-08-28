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
    supporting: int
    other_fiber: int
    supporting_names: tuple[str, ...]
    other_fiber_names: tuple[str, ...]
    searched: tuple[str, ...]
    pending: tuple[str, ...]

    @property
    def accounted(self) -> int:
        """Everything discovered, whether it left by a stage or came out."""
        return (
            sum(n for _, n in self.stages)
            + self.in_scope
            + self.supporting
            + self.other_fiber
        )

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

    stages: list[tuple[str, int]] = [("Rejected", status["unreviewed"])]
    for label, keys in FUNNEL_GROUPS:
        stages.append((label, sum(reasons[k] for k in keys)))
    stages.append(("Out of scope", status["excluded"] + status["watchlist"]))

    built = Funnel(
        snapshot=snapshot_date,
        candidates=len(cand),
        stages=tuple(s for s in stages if s[1]),
        in_scope=status["included"],
        supporting=0,
        other_fiber=0,
        supporting_names=(),
        other_fiber_names=(),
        searched=SOURCES_SEARCHED,
        pending=SOURCES_PENDING,
    )
    # A funnel that does not balance is a bug, not a rounding difference.
    assert built.accounted == built.candidates, (
        f"funnel does not balance: {built.accounted} accounted for, "
        f"{built.candidates} discovered"
    )
    return built


def das_project_ids() -> set[str]:
    """The official DAS project set: DAS-native and not excluded.

    One definition, used by every figure that counts projects. Catalogue
    `status` answers "is this in the comparison"; `das_focus` answers "is this
    DAS". The census is about DAS software, so focus is the basis -- which
    keeps distributed-temperature packages and general seismology toolkits out
    of the headline while still counting DAS projects held on the watchlist.
    """
    from oss_das.figures import records

    return {
        pid
        for pid, record in records.curated().items()
        if record.get("status") != "excluded"
        and (record.get("das_focus") or "das-native") == "das-native"
    }


def totals_from_records() -> EcosystemTotals:
    """The four headline numbers, read from the markdown records."""
    from oss_das.figures import records

    git = records.measured("git")
    included = das_project_ids()
    lines = sum(git[i].get("lines_total") or 0 for i in included if i in git)

    commit_dir = records.data_dir() / "commits"
    rows: list[dict[str, str]] = []
    for pid in included:
        path = commit_dir / f"{pid}.csv"
        if path.exists():
            rows.extend(_read(path))
    human = [
        r
        for r in rows
        if not (BOT.search(r["author_name"]) or BOT.search(r["author_email"]))
    ]
    return EcosystemTotals(
        projects=len(included),
        contributors=unique_authors(rows),
        commits=len(human),
        lines=lines,
        unmirrored=tuple(sorted(i for i in included if i not in git)),
    )


def funnel_from_records() -> Funnel:
    """The funnel, read from the markdown records.

    Candidates carry no outcome field yet, so anything neither catalogued nor
    in the rejection ledger is counted as rejected in bulk. Those were never
    examined -- the count is honest about the arithmetic, not about the
    scrutiny each candidate received.
    """
    from oss_das.figures import records

    sources = records.candidate_sources()
    curated = records.curated()
    ledger = records.rejections()
    orphans = _orphan_curated()
    total = sum(sources.values()) + len(orphans)

    reasons: Counter[str] = Counter(
        entry.get("reason", "not-reusable") for entry in ledger.values()
    )

    # The funnel emits three kinds of project, not one. A general seismology
    # tool that reads DAS and a distributed-temperature package are both real
    # findings; burying them in "out of scope" loses them.
    def focus_of(record: dict[str, Any]) -> str:
        return record.get("das_focus") or "das-native"

    live = [r for r in curated.values() if r.get("status") != "excluded"]
    in_scope = sum(1 for r in live if focus_of(r) == "das-native")

    def named(records: list[dict[str, Any]], focus: str) -> tuple[str, ...]:
        return tuple(
            sorted(
                (r.get("name") or r.get("id", "?"))
                for r in records
                if focus_of(r) == focus
            )
        )

    fiber_names = named(live, "other-fiber")
    support_names = named(list(curated.values()), "das-supporting")
    other_fiber = len(fiber_names)
    supporting = len(support_names)

    # Whatever the three outlets do not carry leaves by the same named routes
    # the rejection ledger uses, classified from its own decision_reason. A
    # residual "out of scope" bucket would merge a duplicate, a repository
    # with no source, and a tutorial into one number that explains nothing.
    outlets = {
        r["id"] for r in live if focus_of(r) in ("das-native", "other-fiber")
    } | {r["id"] for r in curated.values() if focus_of(r) == "das-supporting"}
    for record in curated.values():
        if record["id"] in outlets:
            continue
        reasons[_classify_reason(record.get("decision_reason") or "")] += 1

    bulk = total - len(curated) - len(ledger)

    stages: list[tuple[str, int]] = []
    if bulk > 0:
        stages.append(("Rejected", bulk))
    for label, keys in FUNNEL_GROUPS:
        stages.append((label, sum(reasons[k] for k in keys)))

    # Self-hosted GitLab and Gitea instances are those forges, not a separate
    # kind of source; the label names the API dialect, not the hostname.
    name_map = {"github.com": "GitHub", "pypi": "Registries"}
    order = ("GitHub", "GitLab", "Gitea", "Registries")
    searched = []
    for host in sources:
        if host in name_map:
            label = name_map[host]
        elif "gitlab" in host or host in {
            "git.gfz-potsdam.de",
            "code.usgs.gov",
            "codebase.helmholtz.cloud",
        }:
            label = "GitLab"
        else:
            label = "Gitea"
        if label not in searched:
            searched.append(label)
    if orphans:
        searched.append("Literature")
    order = (*order, "Literature")
    searched.sort(key=lambda name: order.index(name) if name in order else len(order))

    built = Funnel(
        snapshot="working tree",
        candidates=total,
        stages=tuple(s for s in stages if s[1]),
        in_scope=in_scope,
        supporting=supporting,
        other_fiber=other_fiber,
        supporting_names=support_names,
        other_fiber_names=fiber_names,
        searched=tuple(searched),
        pending=(),
    )
    assert built.accounted == built.candidates, (
        f"funnel does not balance: {built.accounted} accounted for, "
        f"{built.candidates} discovered"
    )
    return built


def _orphan_curated() -> list[str]:
    """Catalogued projects that have no candidate record.

    Findings from the literature search are written straight to data/curated/
    without passing through discovery, so they exist in the catalogue but not
    in the candidate pool. Counting them here keeps the funnel's arithmetic
    true; giving them candidate records upstream would remove the need.
    """
    from oss_das.figures import records

    keys = set()
    for path in (records.data_dir() / "raw" / "candidates").rglob("*.md"):
        key = records.frontmatter(path).get("key")
        if key:
            keys.add(str(key).lower())
    orphans = []
    for pid, record in records.curated().items():
        host = (record.get("forge") or {}).get("host") or "github.com"
        if f"{host}/{record.get('repository', '')}".lower() not in keys:
            orphans.append(pid)
    return sorted(orphans)


def maturity_from_records():
    """Viewers against frameworks, from the per-project git measurements."""
    from datetime import date

    from oss_das.figures import records

    curated = records.curated()
    git = records.measured("git")
    das = das_project_ids()
    out = []
    for pid, record in curated.items():
        if pid not in das:
            continue
        measure = git.get(pid)
        if not measure or not measure.get("commits"):
            continue
        first, last = measure.get("first_commit_at"), measure.get("last_commit_at")
        try:
            days = (
                date.fromisoformat(str(last)[:10]) - date.fromisoformat(str(first)[:10])
            ).days
        except (TypeError, ValueError):
            days = 0
        category = record.get("primary_category")
        capabilities = record.get("capabilities") or []
        if category == "core-framework":
            role = "framework"
        elif (
            category == "visualization-annotation"
            or "desktop-application" in capabilities
        ):
            role = "viewer"
        else:
            role = "other"
        out.append(
            ProjectAge(
                project_id=pid,
                name=record.get("name", pid),
                role=role,
                commits=int(measure.get("commits") or 0),
                authors=int(measure.get("authors") or 0),
                days=days,
                lines=int(measure.get("lines_total") or 0),
            )
        )
    return Maturity(projects=tuple(sorted(out, key=lambda p: -p.commits)))


def licence_from_records() -> LicenceMix:
    """Reuse terms by project and by line, from the curated and git records."""
    from oss_das.figures import records

    curated = records.curated()
    git = records.measured("git")
    das = das_project_ids()
    counts: Counter[str] = Counter()
    line_counts: Counter[str] = Counter()
    total = 0
    for pid, record in curated.items():
        if pid not in das:
            continue
        total += 1
        cls = record.get("license_class") or "unknown"
        counts[cls] += 1
        line_counts[cls] += int((git.get(pid) or {}).get("lines_total") or 0)
    order = ("osi-approved", "source-available", "unlicensed", "unknown")

    def rank(item: tuple[str, int]) -> int:
        return order.index(item[0]) if item[0] in order else len(order)

    return LicenceMix(
        by_class=tuple(sorted(counts.items(), key=rank)),
        lines_by_class=tuple(sorted(line_counts.items(), key=rank)),
        projects=total,
        lines=sum(line_counts.values()),
    )


def composition_from_records() -> Composition:
    """Languages and packaging, from the git measurements and curated records."""
    from oss_das.figures import records

    curated = records.curated()
    git = records.measured("git")
    included = das_project_ids()
    langs: Counter[str] = Counter()
    for pid in included:
        for language, count in (
            (git.get(pid) or {}).get("lines_by_language") or {}
        ).items():
            langs[language] += int(count)
    catalogued = [r for pid, r in curated.items() if pid in included]

    def registry(record: dict[str, Any], name: str) -> bool:
        return bool((record.get("registries") or {}).get(name))

    return Composition(
        languages=tuple(langs.most_common()),
        total_lines=sum(langs.values()),
        projects=len(catalogued),
        with_pypi=sum(1 for r in catalogued if registry(r, "pypi")),
        with_conda=sum(1 for r in catalogued if registry(r, "conda")),
        with_julia=sum(1 for r in catalogued if registry(r, "julia")),
        with_none=sum(
            1
            for r in catalogued
            if not any(registry(r, n) for n in ("pypi", "conda", "julia"))
        ),
    )


def growth_from_records() -> Growth:
    """Commits per year, over the same three groups the funnel emits.

    The funnel names five seismology tools that also read DAS; four are
    excluded from the catalogue as general toolkits, but their commits are the
    comparison this figure exists to make, so all five are counted. Bots are
    dropped as they are in the headline totals, so the DAS-native series equals
    the commit count on the totals figure.
    """
    from oss_das.figures import records

    curated = records.curated()
    das = das_project_ids()
    counts: dict[str, Counter[int]] = {}
    for pid, record in curated.items():
        cls = record.get("das_focus") or "das-native"
        if cls == "not-das":
            continue
        # DAS-native and other-fibre follow the catalogue; DAS-supporting is
        # counted whole, excluded members included.
        if cls == "das-native" and pid not in das:
            continue
        if cls == "other-fiber" and record.get("status") == "excluded":
            continue
        path = records.data_dir() / "commits" / f"{pid}.csv"
        if not path.exists():
            continue
        for row in _read(path):
            if BOT.search(row["author_name"]) or BOT.search(row["author_email"]):
                continue
            stamp = row.get("authored_at") or ""
            if len(stamp) >= 4 and stamp[:4].isdigit():
                counts.setdefault(cls, Counter())[int(stamp[:4])] += 1
    years = sorted({y for c in counts.values() for y in c})
    series = tuple(
        (cls, tuple(counts[cls].get(y, 0) for y in years))
        for cls in sorted(counts, key=lambda c: -sum(counts[c].values()))
    )
    return Growth(
        years=tuple(years),
        by_class=series,
        class_totals=tuple((cls, sum(vals)) for cls, vals in series),
    )


def pipeline_from_records() -> PipelineFlow:
    """The pipeline stages, from the coverage table and the markdown records."""
    from oss_das.figures import records

    coverage = _read(records.data_dir() / "raw" / "coverage.csv")
    kinds = Counter((c.get("kind", ""), c.get("probe", "")) for c in coverage)
    failed = [c for c in coverage if c.get("status") != "ok"]

    curated = records.curated()
    sources = records.candidate_sources()
    orphans = _orphan_curated()

    models: Counter[str] = Counter()
    summarised = 0
    for record in curated.values():
        provenance = record.get("provenance") or {}
        if provenance:
            summarised += 1
            models.update(provenance.get("models") or [])

    hosts = set()
    metric_rows = 0
    for kind in ("forge", "registry", "publications"):
        family = records.measured(kind)
        metric_rows += len(family)
        for record in family.values():
            url = record.get("source_url") or ""
            if "//" in url:
                hosts.add(url.split("/")[2])

    return PipelineFlow(
        snapshot="working tree",
        github_searches=kinds[("github", "search")],
        gitlab_searches=kinds[("gitlab", "search")],
        gitea_searches=kinds[("gitea", "search")],
        namespace_walks=sum(
            n for (_, probe), n in kinds.items() if probe == "namespace"
        ),
        probes_ok=len(coverage) - len(failed),
        probes_failed=len(failed),
        failed_hosts=tuple(sorted({c.get("host", "") for c in failed})),
        rows_retrieved=sum(
            int(c["retrieved"])
            for c in coverage
            if (c.get("retrieved") or "").isdigit()
        ),
        candidates=sum(sources.values()) + len(orphans),
        unreviewed=0,
        reviewed=len(curated) + len(records.rejections()),
        catalogued=len(curated),
        included=len(das_project_ids()),
        metric_rows=metric_rows,
        metric_hosts=tuple(sorted(hosts)),
        summarised=summarised,
        summary_models=tuple(sorted(models)),
    )


@dataclass(frozen=True)
class Trace:
    """One project's commit history, bucketed by quarter."""

    project_id: str
    name: str
    focus: str
    first_period: str
    periods: tuple[tuple[str, int], ...]

    @property
    def commits(self) -> int:
        return sum(n for _, n in self.periods)


@dataclass(frozen=True)
class RecordSection:
    """Every project's history, stacked and ordered by when it began.

    Named for the seismic record section it borrows from: one trace per
    source, stacked on a shared time axis, so the shape of the whole
    catalogue is legible at once rather than project by project.
    """

    traces: tuple[Trace, ...]
    periods: tuple[str, ...]
    peak_period: int

    @property
    def since_2020(self) -> int:
        return sum(1 for t in self.traces if t.first_period >= "2020")

    def sidecar(self) -> dict[str, Any]:
        return {
            "projects": len(self.traces),
            "periods": [self.periods[0], self.periods[-1]] if self.periods else [],
            "peak_period": self.peak_period,
            "since_2020": self.since_2020,
            "first_period": {t.project_id: t.first_period for t in self.traces},
        }


#: The record section shows distributed *acoustic* sensing only. Temperature
#: and strain projects are catalogued but are a different instrument, and they
#: happen to be the oldest entries -- leaving them in dates the field wrongly.
DAS_ONLY: tuple[str, ...] = ("das-native",)


def _quarter(stamp: str) -> str:
    """The calendar quarter a timestamp falls in, as its first month.

    Keyed by the quarter's opening month so the key still sorts and still
    places on a month-based time axis.
    """
    month = int(stamp[5:7])
    return f"{stamp[:4]}-{3 * ((month - 1) // 3) + 1:02d}"


def record_section(focus: tuple[str, ...] | None = DAS_ONLY) -> RecordSection:
    """Monthly commit counts per project, oldest first commit first.

    ``focus`` limits the traces to those DAS-focus classes; pass ``None`` for
    every catalogued project regardless of modality.
    """
    from oss_das.figures import records

    curated = records.curated()
    traces: list[Trace] = []
    for pid, record in curated.items():
        if record.get("status") == "excluded":
            continue
        if focus is not None and (record.get("das_focus") or "das-native") not in focus:
            continue
        path = records.data_dir() / "commits" / f"{pid}.csv"
        if not path.exists():
            continue
        buckets: Counter[str] = Counter()
        for row in _read(path):
            stamp = row.get("authored_at") or ""
            if len(stamp) >= 7 and stamp[:4].isdigit():
                buckets[_quarter(stamp)] += 1
        if not buckets:
            continue
        traces.append(
            Trace(
                project_id=pid,
                name=record.get("name", pid),
                focus=record.get("das_focus") or "das-native",
                first_period=min(buckets),
                periods=tuple(sorted(buckets.items())),
            )
        )
    traces.sort(key=lambda t: (t.first_period, -t.commits))
    every = sorted({p for t in traces for p, _ in t.periods})
    peak = max((n for t in traces for _, n in t.periods), default=1)
    return RecordSection(traces=tuple(traces), periods=tuple(every), peak_period=peak)


#: Reuse terms, most permissive first. The order is the figure's argument:
#: how much of the ecosystem can actually be reused, and on what terms.
LICENCE_ORDER = ("osi-approved", "source-available", "unlicensed", "unknown")


@dataclass(frozen=True)
class LanguageRow:
    """One language: how many projects, on what terms, and how much code."""

    language: str
    by_licence: tuple[tuple[str, int], ...]
    lines: int

    @property
    def projects(self) -> int:
        return sum(n for _, n in self.by_licence)


@dataclass(frozen=True)
class LanguageLicence:
    """What the ecosystem is written in, crossed with how it may be reused."""

    rows: tuple[LanguageRow, ...]
    projects: int
    lines: int
    licence_totals: tuple[tuple[str, int], ...]

    @property
    def osi(self) -> int:
        return dict(self.licence_totals).get("osi-approved", 0)

    def sidecar(self) -> dict[str, Any]:
        return {
            "projects": self.projects,
            "lines": self.lines,
            "osi_approved": self.osi,
            "licence_totals": dict(self.licence_totals),
            "languages": {
                r.language: {
                    "projects": r.projects,
                    "lines": r.lines,
                    "by_licence": dict(r.by_licence),
                }
                for r in self.rows
            },
        }


def language_licence() -> LanguageLicence:
    """Primary language against licence class, over the DAS project set."""
    from oss_das.figures import records

    curated = records.curated()
    git = records.measured("git")
    das = das_project_ids()

    grid: dict[str, Counter[str]] = {}
    lines: Counter[str] = Counter()
    totals: Counter[str] = Counter()
    for pid in das:
        measure = git.get(pid) or {}
        # A project with no counted source is a finding, not a gap: it is
        # catalogued, and it publishes nothing a reader could compile.
        language = measure.get("primary_language") or "No counted source"
        licence = curated[pid].get("license_class") or "unknown"
        grid.setdefault(language, Counter())[licence] += 1
        lines[language] += int(measure.get("lines_total") or 0)
        totals[licence] += 1

    rows = tuple(
        LanguageRow(
            language=language,
            by_licence=tuple(
                (licence, counts[licence])
                for licence in LICENCE_ORDER
                if counts[licence]
            ),
            lines=lines[language],
        )
        for language, counts in sorted(
            grid.items(), key=lambda kv: (-sum(kv[1].values()), kv[0])
        )
    )
    return LanguageLicence(
        rows=rows,
        projects=len(das),
        lines=sum(lines.values()),
        licence_totals=tuple(
            (licence, totals[licence]) for licence in LICENCE_ORDER if totals[licence]
        ),
    )
