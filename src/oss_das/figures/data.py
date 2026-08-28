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
