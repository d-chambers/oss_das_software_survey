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
from urllib.parse import urlparse

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
    """The five headline numbers, all over the same set of projects."""

    projects: int
    contributors: int
    commits: int
    lines: int
    unmirrored: tuple[str, ...]
    #: Citations of the software, summed over every linked DOI. Books are left
    #: out upstream: they measure interest in a subject, not use of a tool.
    citations: int = 0
    #: How many projects contribute to that sum. Most have no linked
    #: publication at all, so the total is a floor.
    cited_projects: int = 0

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
        r"private and returns 404|no p(ublished|ublic) source|only a README|publishes only"
        r"|nothing to reuse|no software here",
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
    #: Projects on at least one registry. Not the sum of the three above:
    #: a project can be on PyPI and conda both.
    packaged: int = 0
    #: Projects carrying a packaging manifest, published or not.
    with_packaging: int = 0

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
    """The five headline numbers, read from the markdown records."""
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
    publications = records.measured("publications")
    cited = {
        pid: (publications.get(pid) or {}).get("citations_total") or 0
        for pid in included
    }
    return EcosystemTotals(
        projects=len(included),
        contributors=unique_authors(rows),
        commits=len(human),
        lines=lines,
        unmirrored=tuple(sorted(i for i in included if i not in git)),
        citations=sum(cited.values()),
        cited_projects=sum(1 for count in cited.values() if count),
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
    unclassified: list[str] = []
    for record in curated.values():
        if record["id"] in outlets:
            continue
        name = _classify_reason(record.get("decision_reason") or "")
        if name == "other":
            unclassified.append(record["id"])
        reasons[name] += 1
    # FUNNEL_GROUPS names every bucket the figure draws, and "other" is not
    # among them, so an unmatched reason would leave the record out of the
    # funnel entirely. Fail here, naming it, rather than downstream on an
    # arithmetic mismatch that says only that a number moved by one.
    assert not unclassified, (
        "no HELD_BACK_RULES pattern matches the decision_reason of: "
        f"{', '.join(sorted(unclassified))}"
    )

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


#: The registries the scan looks in, in the order a reader meets them.
REGISTRY_HOSTS = ("pypi", "conda", "julia")


def _published(rows: Any, host: str) -> list[str]:
    """Package names the registry scan actually resolved on one host.

    Each host answers a different question, so each has its own proof of
    publication: PyPI reports a version, conda answers at all, and the Julia
    General registry says outright whether a name is registered.
    """
    proven = {
        "pypi": lambda row: row.get("version") is not None,
        "conda": lambda row: not row.get("error"),
        "julia": lambda row: row.get("registered") is True,
    }[host]
    return [
        row["name"]
        for row in (rows or ())
        if isinstance(row, dict) and row.get("name") and proven(row)
    ]


def composition_from_records() -> Composition:
    """Languages and packaging, from the git and registry measurements.

    Packaging is counted from the registry scan, never from the curated
    record's ``registries`` field. That field is a list of names to go and
    look for, proposed by an agent, and it is wrong in both directions: it
    claimed a PyPI release for a project that has never published one, a
    conda-forge feedstock that does not exist, and a Julia registration the
    scan had already recorded as ``registered: false``, while saying nothing
    at all about six projects that are on PyPI under their own name. A name
    only counts once the scan has resolved it.
    """
    from oss_das.figures import records

    curated = records.curated()
    git = records.measured("git")
    scan = records.measured("registry")
    included = das_project_ids()
    langs: Counter[str] = Counter()
    for pid in included:
        for language, count in (
            (git.get(pid) or {}).get("lines_by_language") or {}
        ).items():
            langs[language] += int(count)
    catalogued = sorted(pid for pid in curated if pid in included)

    def on(pid: str, host: str) -> bool:
        return bool(_published((scan.get(pid) or {}).get(host), host))

    packaged = {pid for pid in catalogued if any(on(pid, h) for h in REGISTRY_HOSTS)}
    practices = records.measured("practices")

    def configured(pid: str) -> bool:
        return bool(
            ((practices.get(pid) or {}).get("practices") or {}).get("packaging")
        )

    composition = Composition(
        languages=tuple(langs.most_common()),
        total_lines=sum(langs.values()),
        projects=len(catalogued),
        with_pypi=sum(1 for pid in catalogued if on(pid, "pypi")),
        with_conda=sum(1 for pid in catalogued if on(pid, "conda")),
        with_julia=sum(1 for pid in catalogued if on(pid, "julia")),
        with_none=len(catalogued) - len(packaged),
        packaged=len(packaged),
        with_packaging=sum(1 for pid in catalogued if configured(pid)),
    )
    # The figure reads as a narrowing: set up as a package, then published.
    # That is only honest while publication implies configuration.
    assert all(configured(pid) for pid in packaged), (
        "a project is published without a packaging manifest, so the figure's "
        "funnel from configured to published no longer nests"
    )
    # The figure prints PyPI beside "no package at all" and invites the reader
    # to add them up. That only works while PyPI is the sole way in; a project
    # packaged for conda or Julia alone would leave the two short of the total
    # with nothing on the plate to explain the gap.
    assert composition.with_pypi == composition.packaged, (
        f"{composition.packaged - composition.with_pypi} project(s) are packaged "
        "somewhere other than PyPI; composition_plate must show that host too"
    )
    return composition


def growth_from_records(exclude: frozenset[str] = frozenset()) -> Growth:
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
        if pid in exclude:
            continue
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
        # Bars are project counts, but each row is annotated with its line
        # count, so ties break on size rather than alphabetically: otherwise
        # the annotations read as unsorted next to bars that are not.
        for language, counts in sorted(
            grid.items(), key=lambda kv: (-sum(kv[1].values()), -lines[kv[0]], kv[0])
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


#: A catalogued project whose source could not be counted. It is a finding
#: rather than a gap -- the project is real and publishes nothing a reader
#: could compile -- so it gets a row, and the row sorts last because it is not
#: a language and should not sit between two that are.
NO_LANGUAGE = "n/a"


@dataclass(frozen=True)
class PlatformRow:
    """One language: how many projects, and which forges they live on."""

    language: str
    by_host: tuple[tuple[str, int], ...]

    @property
    def projects(self) -> int:
        return sum(n for _, n in self.by_host)


@dataclass(frozen=True)
class LanguagePlatform:
    """What the ecosystem is written in, and where its source is hosted."""

    rows: tuple[PlatformRow, ...]
    projects: int
    #: Forge totals, most-used first. This is the order every row stacks in,
    #: so a host sits at the same depth in every bar and the eye can follow it
    #: down the figure.
    hosts: tuple[tuple[str, int], ...]

    def sidecar(self) -> dict[str, Any]:
        # The two shares the talk says out loud, rounded here rather than on a
        # slide: a percentage typed into the deck goes stale the next time a
        # project is added or excluded, and nothing catches it.
        top_language = max(self.rows, key=lambda r: r.projects, default=None)
        top_host = max(self.hosts, key=lambda h: h[1], default=None)
        return {
            "projects": self.projects,
            "hosts": dict(self.hosts),
            "languages": {
                r.language: {"projects": r.projects, "by_host": dict(r.by_host)}
                for r in self.rows
            },
            "top_language": top_language.language if top_language else None,
            "top_language_pct": (
                round(top_language.projects / self.projects * 100)
                if top_language and self.projects
                else None
            ),
            "top_host": top_host[0] if top_host else None,
            "top_host_pct": (
                round(top_host[1] / self.projects * 100)
                if top_host and self.projects
                else None
            ),
        }


def language_platform() -> LanguagePlatform:
    """Primary language against the forge the source is hosted on.

    The forge is read from the mirror record's ``repository_url``, which is
    the URL that was actually cloned, rather than from the curated ``forge``
    block, which only says where the clone was expected to be.
    """
    from oss_das.figures import records

    git = records.measured("git")
    mirror = records.measured("mirror")
    das = das_project_ids()

    grid: dict[str, Counter[str]] = {}
    totals: Counter[str] = Counter()
    for pid in das:
        language = (git.get(pid) or {}).get("primary_language") or NO_LANGUAGE
        url = (mirror.get(pid) or {}).get("repository_url") or ""
        # A project with no mirror is named rather than dropped: it would
        # otherwise leave the host totals short of the project count with
        # nothing on the plate to explain the gap.
        host = urlparse(url).netloc.lower() or "unmirrored"
        grid.setdefault(language, Counter())[host] += 1
        totals[host] += 1

    order = tuple(sorted(totals, key=lambda host: (-totals[host], host)))
    rows = tuple(
        PlatformRow(
            language=language,
            by_host=tuple((host, counts[host]) for host in order if counts[host]),
        )
        for language, counts in sorted(
            grid.items(),
            key=lambda kv: (-sum(kv[1].values()), kv[0] == NO_LANGUAGE, kv[0]),
        )
    )
    mix = LanguagePlatform(
        rows=rows,
        projects=len(das),
        hosts=tuple((host, totals[host]) for host in order),
    )
    # Each bar is built from its segments and annotated with its own total,
    # and the legend invites the reader to add the hosts up to the same
    # number. All three have to agree or the figure prints a lie.
    assert sum(r.projects for r in mix.rows) == mix.projects, (
        "the language rows do not sum to the project total"
    )
    assert sum(n for _, n in mix.hosts) == mix.projects, (
        "the forge hosts do not sum to the project total"
    )
    return mix


#: Ten catalogue categories is more than a stacked bar can carry, so near
#: neighbours are folded together. The grouping is listed here rather than
#: hidden in a plate, and a category matching nothing lands in the last bucket.
CATEGORY_GROUPS: dict[str, str] = {
    "core-framework": "Core frameworks",
    "data-management": "Data and I/O",
    "interoperability": "Data and I/O",
    "compression-storage": "Data and I/O",
    "processing": "Processing",
    "application-domain": "Applied domains",
    "machine-learning-detection": "Machine learning",
}
CATEGORY_FALLBACK = "Modelling, viz, other"


def _commit_years(pid: str) -> Counter[int]:
    """A project's human commits, counted by the year they were authored."""
    from oss_das.figures import records

    years: Counter[int] = Counter()
    for row in _read(records.data_dir() / "commits" / f"{pid}.csv"):
        if BOT.search(row["author_name"]) or BOT.search(row["author_email"]):
            continue
        stamp = row.get("authored_at") or ""
        if len(stamp) >= 4 and stamp[:4].isdigit():
            years[int(stamp[:4])] += 1
    return years


def _growth_over(group_of: Any, order: Any = None) -> Growth:
    """Commits per year for the DAS project set, grouped by ``group_of``."""
    counts: dict[str, Counter[int]] = {}
    for pid in das_project_ids():
        key = group_of(pid)
        if key is None:
            continue
        counts.setdefault(key, Counter()).update(_commit_years(pid))
    years = sorted({y for c in counts.values() for y in c})
    keys = (
        sorted(counts, key=order)
        if order
        else sorted(counts, key=lambda k: -sum(counts[k].values()))
    )
    series = tuple((k, tuple(counts[k].get(y, 0) for y in years)) for k in keys)
    return Growth(
        years=tuple(years),
        by_class=series,
        class_totals=tuple((k, sum(v)) for k, v in series),
    )


def growth_by_category() -> Growth:
    """What kind of software the work went into, year by year."""
    from oss_das.figures import records

    curated = records.curated()

    def group_of(pid: str) -> str:
        category = curated[pid].get("primary_category")
        return CATEGORY_GROUPS.get(category, CATEGORY_FALLBACK)

    return _growth_over(group_of)


def growth_by_cohort() -> Growth:
    """Which arrival cohort the work came from, year by year.

    Answers the question a growth curve otherwise begs: is the field growing
    because new projects keep arriving, or because existing ones deepen?
    """
    from oss_das.figures import records

    git = records.measured("git")

    def group_of(pid: str) -> str | None:
        first = (git.get(pid) or {}).get("first_commit_at")
        return f"Started {str(first)[:4]}" if first else None

    return _growth_over(group_of, order=lambda k: k)


@dataclass(frozen=True)
class Practice:
    """One engineering practice, and how much of the ecosystem shows it."""

    key: str
    label: str
    gate: str
    note: str
    projects: int


@dataclass(frozen=True)
class Engineering:
    """What the ecosystem does that makes its software usable by someone else.

    Grouped into the four questions a reader asks before depending on
    something: can I get it, can I trust it, can I learn it, will it last.
    """

    practices: tuple[Practice, ...]
    projects: int
    gates: tuple[str, ...]

    def by_gate(self, gate: str) -> tuple[Practice, ...]:
        return tuple(p for p in self.practices if p.gate == gate)

    def sidecar(self) -> dict[str, Any]:
        return {
            "projects": self.projects,
            "practices": [asdict(p) for p in self.practices],
        }


#: The practices the figure reports, in reading order, with the gate each one
#: answers. The list is short on purpose: every column here is something that
#: stops a stranger from using the software if it is missing, which is why
#: linting, typing and release notes are measured but not shown -- their
#: absence is a style, not an obstacle.
PRACTICE_COLUMNS: tuple[tuple[str, str, str, str], ...] = (
    # Labels are read from the back of a room, so they are as short as they can
    # be and still be unambiguous. The note beside each one is what the
    # presenter says out loud; it is not drawn.
    ("packaged", "Packaged", "Can I get it?", "on PyPI, conda or Julia"),
    ("licence", "Licence", "Can I get it?", "OSI-approved, legally reusable"),
    ("tests", "Tests", "Can I trust it?", "a test suite in the repo"),
    ("ci", "CI", "Can I trust it?", "a workflow runs"),
    ("docs", "Docs", "Can I learn it?", "beyond the README"),
    ("examples", "Examples", "Can I learn it?", "tutorials or notebooks"),
    ("authors", "Authors > 1", "Will it last?", "more than one person"),
    ("active", "Active", "Will it last?", "a commit in the last 12 months"),
)

#: How long since the last commit a project may be and still count as active.
ACTIVE_DAYS = 365


def engineering_from_records() -> Engineering:
    """Count each practice over the DAS projects, from the markdown records.

    Read from the practices measurement rather than a forge's own flags: a
    forge reports what it can see about repositories it hosts, and the
    catalogue spans four hosts, so only the mirrors give every project the
    same test.
    """
    from datetime import date

    from oss_das.figures import records

    curated = records.curated()
    practices = records.measured("practices")
    registry = records.measured("registry")
    git = records.measured("git")
    ids = sorted(das_project_ids())
    today = date.today()
    # Every bar is a share of the same denominator, so a project the scan
    # could not read would be counted as failing each practice rather than
    # being absent from it. Records carry a reason instead of a zero
    # everywhere else in this repository; refusing is the same rule.
    unmeasured = sorted(
        pid
        for pid in ids
        if not ((practices.get(pid) or {}).get("practices"))
        or pid not in git
        or pid not in registry
    )
    assert not unmeasured, (
        "no practices, git or registry measurement for "
        f"{', '.join(unmeasured)}; re-run b011, b013 and b015 rather than "
        "publishing a figure that reads their silence as a failed practice"
    )

    def has(pid: str, key: str) -> bool:
        record = practices.get(pid) or {}
        tree = record.get("practices") or {}
        if key in ("tests", "ci", "docs", "examples"):
            return bool(tree.get(key))
        if key == "licence":
            return curated[pid].get("license_class") == "osi-approved"
        if key == "packaged":
            reg = registry.get(pid) or {}
            # A result row is a name the scan went and looked for, not proof
            # it found one: PyPI answers with `version: null` for a name that
            # was never published, and the Julia registry says
            # `registered: false` outright. `_published` holds the one
            # definition of publication this deck uses, so the packaging
            # figure and this one cannot report different totals.
            return any(_published(reg.get(host), host) for host in REGISTRY_HOSTS)
        if key == "authors":
            return ((git.get(pid) or {}).get("authors") or 0) > 1
        # A project whose mirror carries no commit date is not counted active:
        # unknown is not the same claim as recent.
        last = str((git.get(pid) or {}).get("last_commit_at") or "")[:10]
        if not last:
            return False
        return (today - date.fromisoformat(last)).days <= ACTIVE_DAYS

    counted = tuple(
        Practice(
            key=key,
            label=label,
            gate=gate,
            note=note,
            projects=sum(1 for pid in ids if has(pid, key)),
        )
        for key, label, gate, note in PRACTICE_COLUMNS
    )
    gates: list[str] = []
    for practice in counted:
        if practice.gate not in gates:
            gates.append(practice.gate)
    return Engineering(practices=counted, projects=len(ids), gates=tuple(gates))


#: Packages that arrive in a dependency list without anyone choosing them: the
#: transitive closure of matplotlib and Jupyter, from the handful of projects
#: that commit a `pip freeze`, plus the notebook and documentation machinery
#: every scientific repository carries. Counting them would report this field
#: as collectively founded on a font parser. Listed here, in the open, because
#: it is a judgement about what "built on" means rather than a measurement.
NOT_A_FOUNDATION = frozenset(
    """
    contourpy cycler fonttools kiwisolver pyparsing six pytz platformdirs
    typing_extensions packaging python-dateutil pygments pyzmq decorator psutil
    traitlets jinja2 markupsafe attrs certifi charset-normalizer idna urllib3
    zipp importlib-metadata conda-forge defaults wheel hdf5 libgcc wcwidth
    ipython ipykernel jupyter jupyterlab notebook nbformat ipywidgets
    sphinx nbsphinx myst-parser furo pydata-sphinx-theme
    """.split()
)


@dataclass(frozen=True)
class Dependency:
    """One package, and how much of the ecosystem is built on it."""

    name: str
    projects: int


@dataclass(frozen=True)
class DependencyMix:
    """What the ecosystem's Python is built on, most-used first."""

    rows: tuple[Dependency, ...]
    python_projects: int
    other_projects: int
    #: How many of the Python projects also ship a dependency manifest. Not
    #: this figure's gate -- it counts imports too, and for a project with no
    #: manifest an import is the only evidence there is -- but recorded so the
    #: deck can say why this denominator and the ecosystem graph's differ
    #: without either slide hard-coding the other's number.
    manifest_projects: int = 0

    def sidecar(self) -> dict[str, Any]:
        return {
            "python_projects": self.python_projects,
            "other_projects": self.other_projects,
            "manifest_projects": self.manifest_projects,
            "rows": [asdict(r) for r in self.rows],
        }


def dependency_mix_from_records(top: int = 10) -> DependencyMix:
    """The packages most of the ecosystem's Python is built on.

    Counted over DAS projects that ship Python, because every name here is a
    Python distribution: a MATLAB or Julia project cannot depend on one, and
    including it in the denominator reports it as failing to use NumPy when it
    was never in a position to. Development-only dependencies are left out --
    a linter is not something a project is built on -- and so is every
    catalogued DAS package: this figure is about the ground the field stands
    on, and a DAS package on the chart would be measuring the field against
    itself. What the field builds on itself is the dependency graph's job.
    """
    from oss_das.figures import records

    curated = records.curated()
    measured = records.measured("dependencies")
    das = das_project_ids()
    python = sorted(pid for pid in das if (measured.get(pid) or {}).get("has_python"))

    #: Every name a catalogued project answers to, so a dependency on it is
    #: counted against the project rather than a bare distribution name.
    catalogued: dict[str, str] = {}
    for pid, record in curated.items():
        for key in (pid, record.get("name") or pid):
            catalogued[key.lower()] = pid
        for host in ("pypi", "conda", "julia"):
            for name in (record.get("registries") or {}).get(host) or []:
                catalogued[str(name).lower()] = pid

    counts: Counter[str] = Counter()
    for pid in python:
        record = measured[pid]
        counts.update(
            {
                name
                for name in list(record.get("required") or ())
                + list(record.get("optional") or ())
                if name not in NOT_A_FOUNDATION and name not in catalogued
            }
        )

    # Ties at the cut are broken alphabetically, so two packages on the same
    # count can decide the last place between them on their names alone.
    rows = tuple(
        Dependency(name=name, projects=n)
        for name, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:top]
    )
    mix = DependencyMix(
        rows=rows,
        python_projects=len(python),
        other_projects=len(das) - len(python),
        manifest_projects=sum(
            1 for pid in python if (measured.get(pid) or {}).get("manifests")
        ),
    )
    # The figure prints a share of the same denominator beside every bar, so a
    # count above it would be printing a percentage over one hundred, and an
    # empty denominator would divide by zero rather than draw nothing.
    assert mix.rows, "no dependency is shared by any catalogued project"
    assert mix.python_projects > 0, "no catalogued DAS project ships Python"
    assert all(r.projects <= mix.python_projects for r in mix.rows), (
        "a package is depended on by more projects than there are projects"
    )
    return mix


@dataclass(frozen=True)
class Link:
    """One catalogued project depending on another."""

    source: str
    target: str
    kind: str


@dataclass(frozen=True)
class Network:
    """Which catalogued DAS projects build on each other."""

    links: tuple[Link, ...]
    #: (id, name, how many catalogued projects depend on it), most depended first.
    providers: tuple[tuple[str, str, int], ...]
    #: (id, name) for each project that depends on another, most edges first.
    consumers: tuple[tuple[str, str], ...]
    projects: int
    connected: int

    @property
    def isolated(self) -> int:
        return self.projects - self.connected

    def sidecar(self) -> dict[str, Any]:
        hub = self.providers[0] if self.providers else ("", "", 0)
        return {
            "links": [asdict(link) for link in self.links],
            "providers": [list(p) for p in self.providers],
            "projects": self.projects,
            "connected": self.connected,
            "isolated": self.isolated,
            # Named, because a slide quotes these and "providers.0.2" is not a
            # citation anyone can read or a path every consumer can resolve.
            "hub": hub[1],
            "hub_dependents": hub[2],
        }


#: Strongest relation first. A package named in two lists is counted once, by
#: the strongest claim: needing something at runtime is not the same as
#: naming it in a test extra.
_LINK_RANK = ("required", "optional", "development")


def network_from_records() -> Network:
    """The dependency graph among catalogued DAS projects.

    Edges come from the manifests each project publishes, not from imports, so
    this is what a project *declares* it builds on. A name is resolved to a
    project through every name it could be installed under -- its id, its
    catalogue name, and any PyPI distribution the registry scan confirmed --
    because a project is rarely imported under the name we file it by.

    Counted over projects that ship a manifest, on the same bar the ecosystem
    comparison uses. A project that declares nothing would otherwise sit in the
    figure with no edges, and read as a finding when it is only a silence --
    and the two figures are adjacent in the deck, so measuring the same hub two
    ways puts two numbers for it on consecutive slides. The dependency bars
    deliberately do not narrow this way: they ask what a project is built on,
    where an import is the better evidence and the only evidence some projects
    offer.
    """
    from oss_das.figures import records

    curated = records.curated()
    registry = records.measured("registry")
    measured = records.measured("dependencies")
    included = {
        pid for pid in das_project_ids() if (measured.get(pid) or {}).get("manifests")
    }

    alias: dict[str, str] = {}
    for pid in included:
        names = {pid, (curated[pid].get("name") or "").lower()}
        names.update(
            row["name"].lower()
            for row in ((registry.get(pid) or {}).get("pypi") or [])
            if row.get("name")
        )
        for name in names:
            if name:
                alias[name.replace("_", "-")] = pid

    strongest: dict[tuple[str, str], str] = {}
    for pid in sorted(included):
        # `declared` is the manifest alone. The merged required/optional lists
        # fold imports in, which is what made this figure report a different
        # count for the same hub than the ecosystem comparison beside it.
        for name, kind in ((measured.get(pid) or {}).get("declared") or {}).items():
            target = alias.get(str(name).lower().replace("_", "-"))
            if target is None or target == pid:
                continue
            held = strongest.get((pid, target))
            if held is None or _LINK_RANK.index(kind) < _LINK_RANK.index(held):
                strongest[(pid, target)] = kind

    links = tuple(
        Link(source, target, kind)
        for (source, target), kind in sorted(strongest.items())
    )
    incoming: Counter[str] = Counter(link.target for link in links)
    outgoing: Counter[str] = Counter(link.source for link in links)
    name = lambda pid: curated[pid].get("name") or pid  # noqa: E731

    # Providers rank by how many depend on them. Consumers then follow the
    # providers they point at, so the figure's threads run mostly parallel
    # instead of crossing the full width to reach a row picked alphabetically.
    order = {pid: i for i, (pid, _) in enumerate(incoming.most_common())}
    targets: dict[str, list[int]] = {}
    for link in links:
        targets.setdefault(link.source, []).append(order[link.target])
    consumers = sorted(
        outgoing,
        key=lambda pid: (sum(targets[pid]) / len(targets[pid]), name(pid).lower()),
    )
    return Network(
        links=links,
        providers=tuple(
            (pid, name(pid), count) for pid, count in incoming.most_common()
        ),
        consumers=tuple((pid, name(pid)) for pid in consumers),
        projects=len(included),
        connected=len(set(incoming) | set(outgoing)),
    )


@dataclass(frozen=True)
class EcosystemGraph:
    """One ecosystem's internal dependency graph, on the manifest bar."""

    name: str
    #: (id, display name, how many in-ecosystem projects depend on it).
    providers: tuple[tuple[str, str, int], ...]
    #: Projects that ship a dependency manifest. Anything else declares
    #: nothing, so its absence of edges would be a silence rather than a
    #: finding. Deliberately NOT the composition figure's "Packaged": that
    #: counts root packaging files, and ten projects here declare their
    #: dependencies in a requirements.txt without being installable at all.
    projects: int
    #: Projects with at least one edge, in either direction.
    connected: int
    #: How many depend on another project in the same ecosystem.
    consumers: int
    edges: int

    @property
    def share(self) -> float:
        return self.consumers / self.projects if self.projects else 0.0

    def sidecar(self) -> dict[str, Any]:
        hub = self.providers[0] if self.providers else ("", "", 0)
        return {
            "name": self.name,
            "providers": [list(p) for p in self.providers],
            "projects": self.projects,
            "connected": self.connected,
            "consumers": self.consumers,
            "edges": self.edges,
            "hub": hub[1],
            "hub_dependents": hub[2],
            "share_percent": round(100 * self.share),
        }


def _graph(
    name: str,
    declared: dict[str, dict[str, str]],
    alias: dict[str, str],
    display: dict[str, str],
) -> EcosystemGraph:
    """Fold declared dependencies into one ecosystem's internal graph."""
    incoming: Counter[str] = Counter()
    outgoing: Counter[str] = Counter()
    edges: set[tuple[str, str]] = set()
    for pid, names in declared.items():
        for raw in names:
            target = alias.get(str(raw).lower().replace("_", "-"))
            if target is None or target == pid or (pid, target) in edges:
                continue
            edges.add((pid, target))
            incoming[target] += 1
            outgoing[pid] += 1
    return EcosystemGraph(
        name=name,
        providers=tuple(
            (pid, display.get(pid, pid), count) for pid, count in incoming.most_common()
        ),
        projects=len(declared),
        connected=len(set(incoming) | set(outgoing)),
        consumers=len(outgoing),
        edges=len(edges),
    )


def das_graph() -> EcosystemGraph:
    """The catalogue's internal graph, on the manifest bar."""
    from oss_das.figures import records

    curated = records.curated()
    registry = records.measured("registry")
    measured = records.measured("dependencies")
    included = das_project_ids()

    alias: dict[str, str] = {}
    display: dict[str, str] = {}
    declared: dict[str, dict[str, str]] = {}
    for pid in sorted(included):
        record = measured.get(pid) or {}
        if not record.get("manifests"):
            continue
        declared[pid] = record.get("declared") or {}
        display[pid] = curated[pid].get("name") or pid
        names = {pid, (curated[pid].get("name") or "").lower()}
        names.update(
            row["name"].lower()
            for row in ((registry.get(pid) or {}).get("pypi") or [])
            if row.get("name")
        )
        for name in names:
            if name:
                alias[name.replace("_", "-")] = pid
    return _graph("DAS", declared, alias, display)


def reference_graph(ecosystem: str = "seismology") -> EcosystemGraph:
    """A reference ecosystem's internal graph, read from data/comparison.

    Catalogued DAS projects are held out. Six of them carry the seismology
    topic, so leaving them in put the same project in both panels with
    different counts -- DASCore reads eight dependents against the catalogue
    and two against the topic, because seven of its dependents never set the
    topic. That gap is a difference of population, not of measurement, and it
    is not worth explaining from a podium. Seismology tools that merely read
    DAS, such as Pyrocko, are not DAS-native and stay.
    """
    from oss_das.figures import records

    curated = records.curated()
    das_repos = {
        (curated[pid].get("repository") or "").lower()
        for pid in das_project_ids()
        if curated[pid].get("repository")
    }
    corpus = records.comparison(ecosystem)
    alias: dict[str, str] = {}
    display: dict[str, str] = {}
    declared: dict[str, dict[str, str]] = {}
    for key, record in sorted(corpus.items()):
        if not record.get("manifests"):
            continue
        if str(record.get("repository") or "").lower() in das_repos:
            continue
        declared[key] = record.get("declared") or {}
        display[key] = record.get("name") or key
        # A repository is depended on by the name on its distribution, which is
        # often not the name of the repository -- daspy ships as daspy-toolbox.
        names = {
            str(record.get("name") or "").lower(),
            str(record.get("distribution") or "").lower(),
        }
        for name in names:
            if name:
                alias[name.replace("_", "-")] = key
    return _graph(ecosystem.capitalize(), declared, alias, display)


def ecosystems(ecosystem: str = "seismology") -> tuple[EcosystemGraph, EcosystemGraph]:
    """The DAS graph beside a reference one, measured identically.

    Both sides read the ``declared`` field and both apply the manifest bar. The
    catalogue's own measurement also scans imports, which needs a clone and so
    cannot be run against a few hundred reference repositories; comparing the
    two halves would credit DAS with edges the other side could not have shown.
    """
    das, reference = das_graph(), reference_graph(ecosystem)
    assert das.projects and reference.projects, (
        "one ecosystem has no project with a manifest; run b016_dependencies "
        "and s010_seismology_corpus before drawing the comparison"
    )
    return das, reference


@dataclass(frozen=True)
class ArchiveAbstraction:
    """One project's released multi-file abstraction and logo palette."""

    project: str
    version: str
    files: str
    logical: str
    memory: str
    palette: tuple[str, ...]
    logo_source: str

    def sidecar(self) -> dict[str, Any]:
        return asdict(self)


def archive_abstractions() -> tuple[ArchiveAbstraction, ArchiveAbstraction]:
    """Released archive models and exact dominant colours from their logos."""
    dascore = ArchiveAbstraction(
        project="DASCore",
        version="0.1.21",
        files="Files",
        logical="Spool index",
        memory="Patch",
        palette=("#002868", "#D0002A", "#FFC934"),
        logo_source=(
            "https://github.com/DASDAE/dascore/blob/v0.1.21/docs/_static/logo.png"
        ),
    )
    xdas = ArchiveAbstraction(
        project="Xdas",
        version="0.2.8",
        files="Files",
        logical="Virtual DataArray",
        memory="Chunk",
        palette=("#2F007E",),
        logo_source=(
            "https://github.com/xdas-dev/xdas/blob/0.2.8/docs/_static/logo-light.png"
        ),
    )
    assert len(dascore.palette) == 3 and len(xdas.palette) == 1
    assert all(
        colour.startswith("#") and len(colour) == 7 for colour in dascore.palette
    )
    assert all(colour.startswith("#") and len(colour) == 7 for colour in xdas.palette)
    return dascore, xdas
