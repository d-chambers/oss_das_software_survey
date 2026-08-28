#!/usr/bin/env python3
"""Ask one agent per project to read its documentation and describe it.

The capability tags are a controlled vocabulary chosen by one reviewer, which
makes them comparable but thin. This stage adds prose: an agent reads what each
project actually publishes about itself and writes a paragraph, so the catalog
carries a description that did not come from the same person who wrote the tags.

Every record is attributed. The model identity, token counts, cost, and timing
are taken from the API response rather than from the agent's own account of
itself, because a model cannot observe its own token usage and would have to
invent the number.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path

import yaml

from oss_das.core import PATHS, load_projects, read_frontmatter
from oss_das.models import CatalogStatus

#: The name recorded in each file's provenance block.
AGENT_NAME = "das-summarizer"

#: Read-only tooling. The agent fetches published pages and nothing else.
ALLOWED_TOOLS = "WebFetch"

PROMPT = """You are documenting one open-source project for a research catalog \
of distributed acoustic sensing (DAS) software.

Project: {name}
Repository: {url}
{extra}
Read the repository landing page. If it is thin, also look at the documentation \
site or one or two source files. Use WebFetch; do not guess.

Write your answer as GitHub-flavoured markdown in exactly this shape:

## Summary

One paragraph of 100-150 words, in plain prose, describing what this software \
does, who would use it, and what makes it different from a generic toolkit. Be \
concrete and factual. Do not market it. Do not repeat the repository name in \
every sentence.

## Details

- **Interface:** library, CLI, GUI application, notebook collection, or service
- **Data formats:** the DAS or fiber formats it reads or writes, if stated
- **Key dependencies:** the handful of libraries it is built on
- **Scope signals:** anything indicating maturity, scale, or intended audience
- **Source visible:** whether the repository actually publishes source code, or \
only a description of it
- **Sources read:** the URLs you actually fetched

Rules that matter more than completeness:
- If you could not reach the repository, write exactly `UNAVAILABLE` under \
Summary and explain what failed. Do not describe the project from prior \
knowledge.
- If a detail is not stated in what you read, write `not stated`. Never infer a \
file format or dependency that you did not see.
- Some repositories advertise features without shipping code. Describe what the \
project claims, but say so plainly in Scope signals when you saw no source.
"""


def build_prompt(project) -> str:
    extra = ""
    if project.homepage:
        extra = f"Documentation: {project.homepage}\n"
    return PROMPT.format(name=project.name, url=project.repository_url, extra=extra)


def run_agent(project, *, model: str, timeout: int) -> dict:
    """Run one headless agent and return its payload plus measured provenance."""
    started = datetime.now(UTC).replace(microsecond=0)
    command = [
        "claude",
        "-p",
        build_prompt(project),
        "--output-format",
        "json",
        "--model",
        model,
        "--allowedTools",
        ALLOWED_TOOLS,
    ]
    try:
        completed = subprocess.run(
            command, capture_output=True, text=True, timeout=timeout
        )
    except subprocess.TimeoutExpired:
        return {"project": project, "error": f"timed out after {timeout}s"}
    if completed.returncode != 0:
        return {"project": project, "error": completed.stderr.strip()[:400]}
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return {"project": project, "error": "agent did not return JSON"}
    if payload.get("is_error"):
        return {"project": project, "error": str(payload.get("result"))[:400]}
    return {"project": project, "payload": payload, "started": started}


def usage_totals(payload: dict) -> dict:
    """Sum token counts across every model the run actually used."""
    models = payload.get("modelUsage") or {}
    totals = {"input": 0, "output": 0, "cache_read": 0, "cache_write": 0}
    for usage in models.values():
        totals["input"] += usage.get("inputTokens", 0)
        totals["output"] += usage.get("outputTokens", 0)
        totals["cache_read"] += usage.get("cacheReadInputTokens", 0)
        totals["cache_write"] += usage.get("cacheCreationInputTokens", 0)
    return totals


def _body(raw: str) -> str:
    """Drop any narration the agent wrote before its actual answer.

    Headless runs sometimes prefix the result with a line of thinking-aloud
    ("Now I have enough information to..."), which is about the agent rather
    than about the project and does not belong in a catalog record.
    """
    marker = "## Summary"
    index = raw.find(marker)
    return (raw[index:] if index != -1 else raw).strip()


def render(result: dict, existing: str) -> str:
    """Rewrite a project file's summary block and body, keeping the rest.

    The curated and collected blocks belong to other processes, so this stage
    reads them back out of the file and returns them untouched.
    """
    project = result["project"]
    payload = result["payload"]
    totals = usage_totals(payload)
    models = sorted(payload.get("modelUsage") or {})
    body = _body(str(payload.get("result", "")))
    document = read_frontmatter(Path(existing)) if Path(existing).exists() else {}
    document.pop("summary", None)
    preserved = yaml.safe_dump(document, sort_keys=False, allow_unicode=True, width=100)
    lines = [
        "---",
        preserved.rstrip("\n"),
        "summary:",
        f"  agent: {AGENT_NAME}",
        f"  models: [{', '.join(models)}]",
        f"  ran_at: {result['started'].isoformat()}",
        f"  duration_seconds: {round(payload.get('duration_ms', 0) / 1000, 1)}",
        f"  turns: {payload.get('num_turns')}",
        f"  input_tokens: {totals['input']}",
        f"  output_tokens: {totals['output']}",
        f"  cache_read_tokens: {totals['cache_read']}",
        f"  cache_write_tokens: {totals['cache_write']}",
        f"  total_tokens: {sum(totals.values())}",
        f"  api_list_cost_usd: {round(payload.get('total_cost_usd', 0.0), 4)}",
        "  provenance: token counts and model identity come from the API"
        " response, not from the agent's self-report",
        "---",
        "",
        f"# {project.name}",
        "",
        f"Source: [{project.repository}]({project.repository_url})",
        "",
        body,
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="sonnet")
    parser.add_argument("--workers", type=int, default=4, help="Concurrent agents.")
    parser.add_argument("--limit", type=int, help="Only process the first N projects.")
    parser.add_argument("--only", nargs="*", help="Restrict to these project ids.")
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument(
        "--force", action="store_true", help="Rewrite summaries that already exist."
    )
    args = parser.parse_args()

    output = PATHS.curated
    # Excluded projects are out of scope by review, so paying an agent to
    # describe a robotics data-acquisition system would buy nothing.
    projects = [
        project
        for project in load_projects()
        if project.status != CatalogStatus.EXCLUDED
        and (not args.only or project.id in args.only)
    ]
    if not args.force:
        # A file always exists; what marks a project as done is prose in it.
        projects = [
            project
            for project in projects
            if "## Summary" not in (output / f"{project.id}.md").read_text()
        ]
    if args.limit:
        projects = projects[: args.limit]
    if not projects:
        print("nothing to do; pass --force to rewrite existing summaries")
        return

    print(f"summarizing {len(projects)} projects with {args.model}", file=sys.stderr)
    failures = []
    spend = 0.0
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for result in pool.map(
            lambda project: run_agent(project, model=args.model, timeout=args.timeout),
            projects,
        ):
            project = result["project"]
            if "error" in result:
                failures.append((project.id, result["error"]))
                print(f"  FAIL {project.id}: {result['error'][:90]}", file=sys.stderr)
                continue
            target = output / f"{project.id}.md"
            target.write_text(render(result, str(target)))
            spend += result["payload"].get("total_cost_usd", 0.0)
            print(f"  ok   {project.id}", file=sys.stderr)

    print(
        f"wrote {len(projects) - len(failures)} summaries, ${spend:.2f}",
        file=sys.stderr,
    )
    if failures:
        print(f"{len(failures)} failed; rerun to retry them", file=sys.stderr)


if __name__ == "__main__":
    main()
