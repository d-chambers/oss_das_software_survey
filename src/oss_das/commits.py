"""Clone project repositories and extract per-commit history from git.

The catalog's commit signal comes from forge APIs, which publish a count and a
last-commit date but no history. Answering "how many commits over time" needs
the commits themselves, so this module keeps a bare mirror of every repository
and reads `git log --numstat` out of it.

Clones are bare on purpose. The destination is usually an external drive, and a
bare mirror has no working tree to check out: no symlinks, no executable bits,
and no case-colliding paths, all of which fail on exFAT. It also arrives as a
single packfile rather than thousands of loose files.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import time
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from oss_das.core import write_csv
from oss_das.models import ProjectRecord

#: Never prompt. A private or deleted repository would otherwise block an
#: unattended batch on a credential-helper prompt that nobody is there to answer.
GIT_ENV = {
    "GIT_TERMINAL_PROMPT": "0",
    "GIT_ASKPASS": "/bin/true",
    "SSH_ASKPASS": "/bin/true",
    "GCM_INTERACTIVE": "never",
}

#: Tried in order when a clone has no usable HEAD, newest convention first.
MAINLINE_REFS = ("main", "master", "dev", "develop", "trunk")

#: Record and field separators. Both are ASCII control characters that cannot
#: occur in a commit subject, so a subject containing tabs, commas, or pipes
#: still parses.
RECORD_SEP = "\x1e"
FIELD_SEP = "\x1f"

#: sha, parents, mailmapped author name/email, author date, committer date, subject.
LOG_FORMAT = "%x1e%H%x1f%P%x1f%aN%x1f%aE%x1f%aI%x1f%cI%x1f%s"

COMMIT_FIELDS = [
    "project_id",
    "status",
    "sha",
    "author_name",
    "author_email",
    "authored_at",
    "committed_at",
    "is_merge",
    "files_changed",
    "insertions",
    "deletions",
    "binary_files",
    "subject",
]

STATUS_FIELDS = [
    "project_id",
    "name",
    "status",
    "repository_url",
    "forge_kind",
    "forge_host",
    "clone_result",
    "ref",
    "commits",
    "first_commit_at",
    "last_commit_at",
    "repo_bytes",
    "duration_s",
    "error",
]


@dataclass(frozen=True)
class CommitStat:
    """One commit, with its diff totals when git reports any.

    The totals count text lines only. A merge has no diff of its own here, and
    a binary file has no line count at all, so both are recorded as absent
    rather than as zero -- see :func:`parse_git_log`.
    """

    sha: str
    parents: tuple[str, ...]
    author_name: str
    author_email: str
    authored_at: str
    committed_at: str
    subject: str
    files_changed: int | None = None
    insertions: int | None = None
    deletions: int | None = None
    binary_files: int | None = None

    @property
    def is_merge(self) -> bool:
        return len(self.parents) > 1

    def row(self, project: ProjectRecord) -> dict[str, Any]:
        return {
            "project_id": project.id,
            "status": project.status.value,
            "sha": self.sha,
            "author_name": self.author_name,
            "author_email": self.author_email,
            "authored_at": self.authored_at,
            "committed_at": self.committed_at,
            "is_merge": int(self.is_merge),
            "files_changed": self.files_changed,
            "insertions": self.insertions,
            "deletions": self.deletions,
            "binary_files": self.binary_files,
            "subject": self.subject,
        }


class GitError(RuntimeError):
    """A git subprocess failed, timed out, or git is not installed."""


def run_git(args: list[str], *, timeout: int) -> str:
    """Run git with prompting disabled and return stdout."""
    try:
        result = subprocess.run(
            ["git", *args],
            capture_output=True,
            timeout=timeout,
            env={**os.environ, **GIT_ENV},
        )
    except subprocess.TimeoutExpired as error:
        raise GitError(f"timed out after {timeout}s") from error
    except FileNotFoundError as error:
        raise GitError("git is not installed") from error
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", "replace").strip().splitlines()
        raise GitError(detail[-1] if detail else f"git exited {result.returncode}")
    return result.stdout.decode("utf-8", "replace")


def parse_git_log(text: str) -> list[CommitStat]:
    """Parse `git log --numstat` output written with :data:`LOG_FORMAT`.

    Merge commits carry no numstat rows. They are still real events on the
    timeline, so they are kept and flagged with ``is_merge``, but their diff
    columns are left empty rather than filled with zeros: git measured nothing
    here, and a zero would read as "this merge changed no lines".

    Binary files report ``-`` for both counts. They are tallied in
    ``binary_files`` and excluded from the line totals, because a binary change
    is not zero lines, it is unmeasurable in lines.
    """
    commits: list[CommitStat] = []
    for chunk in text.split(RECORD_SEP):
        if not chunk.strip():
            continue
        header, _, body = chunk.partition("\n")
        fields = header.split(FIELD_SEP)
        if len(fields) < 7:
            raise ValueError(f"malformed log header: {header!r}")
        sha, parents, name, email, authored, committed, subject = fields[:7]
        rows = [line for line in body.splitlines() if line.strip()]
        # Only a merge is unmeasured. A non-merge commit with no numstat rows
        # is an empty commit, which genuinely did change nothing.
        measured = len(parents.split()) < 2
        files = insertions = deletions = binary = 0
        for line in rows:
            added, _, rest = line.partition("\t")
            removed, _, _path = rest.partition("\t")
            files += 1
            if added == "-" or removed == "-":
                binary += 1
                continue
            insertions += int(added)
            deletions += int(removed)
        commits.append(
            CommitStat(
                sha=sha,
                parents=tuple(parents.split()),
                author_name=name,
                author_email=email,
                authored_at=authored,
                committed_at=committed,
                subject=subject,
                files_changed=files if measured else None,
                insertions=insertions if measured else None,
                deletions=deletions if measured else None,
                binary_files=binary if measured else None,
            )
        )
    return commits


def clone_or_update(url: str, repo: Path, *, update: bool, timeout: int) -> str:
    """Mirror ``url`` into ``repo``; return cloned, updated, or skipped.

    ``--mirror`` rather than ``--bare`` because it configures a fetch refspec,
    which is what makes a later ``--update`` run a cheap incremental fetch
    instead of a second full clone.
    """
    if repo.exists():
        if not update:
            return "skipped"
        run_git(["-C", str(repo), "fetch", "--prune", "--quiet"], timeout=timeout)
        return "updated"
    repo.parent.mkdir(parents=True, exist_ok=True)
    staging = repo.with_name(f"{repo.name}.partial")
    if staging.exists():
        shutil.rmtree(staging, ignore_errors=True)
    try:
        run_git(["clone", "--mirror", "--quiet", url, str(staging)], timeout=timeout)
    except GitError:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    staging.rename(repo)
    return "cloned"


def resolve_mainline(repo: Path, *, timeout: int = 900) -> str | None:
    """Return the mainline ref name, or None for a repository with no commits."""
    try:
        head = run_git(
            ["-C", str(repo), "symbolic-ref", "--short", "HEAD"], timeout=timeout
        ).strip()
    except GitError:
        head = ""
    candidates = [head, *MAINLINE_REFS] if head else list(MAINLINE_REFS)
    for name in candidates:
        if not name:
            continue
        try:
            run_git(
                [
                    "-C",
                    str(repo),
                    "rev-parse",
                    "--verify",
                    "--quiet",
                    f"{name}^{{commit}}",
                ],
                timeout=timeout,
            )
        except GitError:
            continue
        return name
    return None


def read_commits(repo: Path, ref: str, *, timeout: int = 900) -> list[CommitStat]:
    """Read every commit reachable from ``ref`` with its diff totals.

    ``--no-renames`` keeps each numstat row a literal path with literal counts;
    rename detection would zero out moved files and make churn depend on git's
    similarity heuristic.
    """
    text = run_git(
        [
            "-c",
            "core.quotePath=false",
            "-C",
            str(repo),
            "log",
            ref,
            "--numstat",
            "--no-renames",
            f"--pretty=tformat:{LOG_FORMAT}",
        ],
        timeout=timeout,
    )
    return parse_git_log(text)


def write_atomic_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    """Write via a temporary name so an interrupted run cannot leave a
    truncated CSV that later looks complete."""
    path.parent.mkdir(parents=True, exist_ok=True)
    staging = path.with_name(f"{path.name}.partial")
    write_csv(staging, rows, COMMIT_FIELDS)
    staging.replace(path)


def directory_bytes(path: Path) -> int:
    return sum(item.stat().st_size for item in path.rglob("*") if item.is_file())


@dataclass
class ProjectResult:
    """What one project's clone-and-extract attempt produced."""

    project: ProjectRecord
    clone_result: str
    ref: str | None = None
    error: str = ""
    repo_bytes: int | None = None
    duration_s: float = 0.0
    commits: list[CommitStat] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.error

    def status_row(self) -> dict[str, Any]:
        # Sorted as instants, not as strings: authored_at carries the author's
        # local UTC offset, so lexical order is wrong across timezones.
        dates = sorted(
            (commit.authored_at for commit in self.commits),
            key=datetime.fromisoformat,
        )
        return {
            "project_id": self.project.id,
            "name": self.project.name,
            "status": self.project.status.value,
            "repository_url": self.project.repository_url,
            "forge_kind": self.project.forge.kind.value,
            "forge_host": self.project.forge.host,
            "clone_result": self.clone_result,
            "ref": self.ref,
            # Left empty rather than zero when nothing was read: a failed clone
            # is a missing measurement, not a repository with no commits.
            "commits": len(self.commits) if self.ok else None,
            "first_commit_at": dates[0] if dates else None,
            "last_commit_at": dates[-1] if dates else None,
            "repo_bytes": self.repo_bytes,
            "duration_s": round(self.duration_s, 1),
            "error": self.error,
        }


def collect_project(
    project: ProjectRecord,
    dest: Path,
    *,
    update: bool = False,
    timeout: int = 1800,
    force: bool = False,
) -> ProjectResult:
    """Clone or refresh one project and write its per-commit CSV."""
    started = time.monotonic()
    repo = dest / "repos" / f"{project.id}.git"
    csv_path = dest / "commits" / f"{project.id}.csv"
    url = project.repository_url or project.derived_url
    try:
        clone_result = clone_or_update(url, repo, update=update, timeout=timeout)
    except GitError as error:
        return ProjectResult(
            project=project,
            clone_result="failed",
            error=str(error),
            duration_s=time.monotonic() - started,
        )
    result = ProjectResult(
        project=project,
        clone_result=clone_result,
        repo_bytes=directory_bytes(repo),
    )
    try:
        result.ref = resolve_mainline(repo, timeout=timeout)
        if result.ref is None:
            # A mirror with no branch is either an empty repository or a broken
            # cache. Either way nothing was measured, so it is an error with a
            # reason rather than a project that honestly has no commits.
            result.error = "no mainline ref"
            return result
        result.commits = read_commits(repo, result.ref, timeout=timeout)
    except GitError as error:
        result.error = str(error)
        return result
    finally:
        result.duration_s = time.monotonic() - started
    # An existing CSV is still rewritten unless the mirror was left untouched,
    # so a run interrupted mid-write repairs itself on the next --force pass.
    if clone_result != "skipped" or not csv_path.exists() or force:
        write_atomic_csv(csv_path, [c.row(project) for c in result.commits])
    result.duration_s = time.monotonic() - started
    return result


def iter_rows(results: Iterable[ProjectResult]) -> Iterator[dict[str, Any]]:
    for result in results:
        for commit in result.commits:
            yield commit.row(result.project)
