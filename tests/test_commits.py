"""Tests for git history extraction."""

from __future__ import annotations

import shutil
import subprocess

import pytest

from oss_das.commits import (
    FIELD_SEP,
    RECORD_SEP,
    CommitStat,
    GitError,
    clone_or_update,
    collect_project,
    parse_git_log,
    read_commits,
    resolve_mainline,
)
from oss_das.core import read_csv
from oss_das.models import Forge, ProjectRecord

pytestmark = pytest.mark.skipif(shutil.which("git") is None, reason="git required")


def record(sha, parents, name, email, authored, committed, subject, numstat=()):
    """Build one raw log record the way LOG_FORMAT writes it."""
    header = FIELD_SEP.join([sha, parents, name, email, authored, committed, subject])
    body = "".join(f"\n{line}" for line in numstat)
    return f"{RECORD_SEP}{header}\n{body}"


class TestParseGitLog:
    """The parser is the whole substance of the module, so it is tested alone."""

    def test_empty_log(self):
        assert parse_git_log("") == []
        assert parse_git_log("\n") == []

    def test_single_commit_totals(self):
        text = record(
            "abc",
            "def",
            "Ada",
            "ada@example.com",
            "2024-01-02T03:04:05+00:00",
            "2024-01-02T03:04:06+00:00",
            "add things",
            ["10\t2\tsrc/a.py", "3\t0\tsrc/b.py"],
        )
        (commit,) = parse_git_log(text)
        assert commit.sha == "abc"
        assert commit.author_name == "Ada"
        assert commit.files_changed == 2
        assert commit.insertions == 13
        assert commit.deletions == 2
        assert commit.binary_files == 0
        assert not commit.is_merge

    def test_merge_is_kept_but_its_churn_is_missing_not_zero(self):
        text = record("m", "p1 p2", "Ada", "a@b.c", "t1", "t2", "Merge branch")
        (commit,) = parse_git_log(text)
        assert commit.is_merge
        # Missing, not zero: git measured no diff for this commit at all.
        assert commit.files_changed is None
        assert commit.insertions is None
        assert commit.deletions is None

    def test_empty_non_merge_commit_really_is_zero(self):
        text = record("e", "p1", "Ada", "a@b.c", "t1", "t2", "empty")
        (commit,) = parse_git_log(text)
        assert not commit.is_merge
        assert commit.files_changed == 0
        assert commit.insertions == 0

    def test_binary_files_are_counted_not_zeroed(self):
        text = record(
            "abc",
            "d",
            "Ada",
            "a@b.c",
            "t1",
            "t2",
            "add image",
            ["-\t-\tdocs/logo.png", "4\t1\tREADME.md"],
        )
        (commit,) = parse_git_log(text)
        assert commit.binary_files == 1
        assert commit.files_changed == 2
        assert commit.insertions == 4
        assert commit.deletions == 1

    def test_paths_with_spaces_and_subject_with_separators(self):
        text = record(
            "abc",
            "d",
            "Ada",
            "a@b.c",
            "t1",
            "t2",
            "fix: a, b | c\tand more",
            ["1\t1\tdocs/my notes.md"],
        )
        (commit,) = parse_git_log(text)
        assert commit.subject == "fix: a, b | c\tand more"
        assert commit.files_changed == 1

    def test_root_commit_has_no_parents(self):
        text = record("abc", "", "Ada", "a@b.c", "t1", "t2", "init", ["1\t0\ta"])
        (commit,) = parse_git_log(text)
        assert commit.parents == ()
        assert not commit.is_merge

    def test_multiple_commits(self):
        text = "".join(
            [
                record("a", "", "Ada", "a@b.c", "t1", "t2", "one", ["1\t0\tx"]),
                record("b", "a", "Bo", "b@b.c", "t3", "t4", "two", ["2\t1\tx"]),
            ]
        )
        assert [c.sha for c in parse_git_log(text)] == ["a", "b"]

    def test_malformed_header_rejected(self):
        with pytest.raises(ValueError, match="malformed log header"):
            parse_git_log(f"{RECORD_SEP}only{FIELD_SEP}two\n")


def git(repo, *args, **env):
    subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        env={
            "PATH": "/usr/bin:/bin",
            "HOME": str(repo),
            "GIT_AUTHOR_NAME": "Ada",
            "GIT_AUTHOR_EMAIL": "ada@example.com",
            "GIT_COMMITTER_NAME": "Ada",
            "GIT_COMMITTER_EMAIL": "ada@example.com",
            "GIT_AUTHOR_DATE": "2024-01-02T03:04:05+00:00",
            "GIT_COMMITTER_DATE": "2024-01-02T03:04:05+00:00",
            **env,
        },
    )


@pytest.fixture
def source_repo(tmp_path):
    """A tiny repository on branch `trunk` with two commits."""
    repo = tmp_path / "source"
    repo.mkdir()
    git(repo, "init", "--quiet", "--initial-branch", "trunk")
    (repo / "a.py").write_text("one\ntwo\n")
    git(repo, "add", "a.py")
    git(repo, "commit", "--quiet", "-m", "first")
    (repo / "a.py").write_text("one\ntwo\nthree\n")
    git(repo, "add", "a.py")
    git(
        repo,
        "commit",
        "--quiet",
        "-m",
        "second",
        GIT_AUTHOR_DATE="2024-02-03T00:00:00+00:00",
    )
    return repo


@pytest.fixture
def project():
    return ProjectRecord(
        id="demo",
        name="Demo",
        repository="acme/demo",
        description="A demo project.",
        status="included",
        decision_reason="Fixture.",
        primary_category="library",
        forge=Forge(kind="github"),
    )


class TestAgainstRealRepositories:
    def test_clone_then_skip_then_update(self, tmp_path, source_repo):
        mirror = tmp_path / "mirror.git"
        assert (
            clone_or_update(str(source_repo), mirror, update=False, timeout=60)
            == "cloned"
        )
        assert mirror.exists()
        assert (
            clone_or_update(str(source_repo), mirror, update=False, timeout=60)
            == "skipped"
        )
        assert (
            clone_or_update(str(source_repo), mirror, update=True, timeout=60)
            == "updated"
        )

    def test_failed_clone_leaves_no_directory(self, tmp_path):
        mirror = tmp_path / "missing.git"
        with pytest.raises(GitError):
            clone_or_update(str(tmp_path / "nope"), mirror, update=False, timeout=60)
        assert not mirror.exists()
        assert not mirror.with_name(f"{mirror.name}.partial").exists()

    def test_resolve_mainline_follows_head(self, tmp_path, source_repo):
        mirror = tmp_path / "mirror.git"
        clone_or_update(str(source_repo), mirror, update=False, timeout=60)
        assert resolve_mainline(mirror) == "trunk"

    def test_resolve_mainline_is_none_for_empty_repo(self, tmp_path):
        empty = tmp_path / "empty.git"
        subprocess.run(
            ["git", "init", "--quiet", "--bare", str(empty)],
            check=True,
            capture_output=True,
        )
        assert resolve_mainline(empty) is None

    def test_read_commits_reports_real_line_counts(self, tmp_path, source_repo):
        mirror = tmp_path / "mirror.git"
        clone_or_update(str(source_repo), mirror, update=False, timeout=60)
        commits = read_commits(mirror, "trunk")
        assert len(commits) == 2
        # git log is newest first.
        newest, oldest = commits
        assert newest.subject == "second"
        assert (newest.insertions, newest.deletions) == (1, 0)
        assert (oldest.insertions, oldest.deletions) == (2, 0)
        assert oldest.author_name == "Ada"
        assert newest.authored_at.startswith("2024-02-03")

    def test_collect_project_writes_csv_and_status(
        self, tmp_path, source_repo, project
    ):
        dest = tmp_path / "dest"
        dest.mkdir()
        local = project.model_copy(update={"repository_url": str(source_repo)})
        result = collect_project(local, dest, timeout=60)
        assert result.ok
        assert result.clone_result == "cloned"
        rows = read_csv(dest / "commits" / "demo.csv")
        assert len(rows) == 2
        assert rows[0]["project_id"] == "demo"
        assert rows[0]["status"] == "included"
        assert {row["author_email"] for row in rows} == {"ada@example.com"}
        status = result.status_row()
        assert status["commits"] == 2
        assert status["ref"] == "trunk"
        assert status["first_commit_at"].startswith("2024-01-02")
        assert status["last_commit_at"].startswith("2024-02-03")
        assert status["repo_bytes"] > 0

    def test_unreachable_repository_records_a_reason_not_a_zero(
        self, tmp_path, project
    ):
        dest = tmp_path / "dest"
        dest.mkdir()
        local = project.model_copy(update={"repository_url": str(tmp_path / "nope")})
        result = collect_project(local, dest, timeout=60)
        assert not result.ok
        assert result.clone_result == "failed"
        # Missing, not zero: a failed clone is an unmeasured repository.
        assert result.status_row()["commits"] is None
        assert result.status_row()["error"]


class TestRerunSafety:
    def test_corrupt_mirror_is_an_error_not_an_empty_project(
        self, tmp_path, source_repo, project
    ):
        """A cached mirror that no longer resolves must not report zero commits."""
        dest = tmp_path / "dest"
        dest.mkdir()
        local = project.model_copy(update={"repository_url": str(source_repo)})
        assert collect_project(local, dest, timeout=60).ok
        # Wreck the mirror the way an interrupted write would.
        for ref in (dest / "repos" / "demo.git").rglob("packed-refs"):
            ref.unlink()
        shutil.rmtree(dest / "repos" / "demo.git" / "refs", ignore_errors=True)
        result = collect_project(local, dest, timeout=60)
        assert not result.ok
        assert result.status_row()["commits"] is None

    def test_no_partial_csv_is_left_behind(self, tmp_path, source_repo, project):
        dest = tmp_path / "dest"
        dest.mkdir()
        local = project.model_copy(update={"repository_url": str(source_repo)})
        collect_project(local, dest, timeout=60)
        assert not list((dest / "commits").glob("*.partial"))


class TestRealMergeAndBinary:
    def test_real_merge_and_binary_commit(self, tmp_path, source_repo, project):
        git(source_repo, "checkout", "--quiet", "-b", "side")
        (source_repo / "b.py").write_text("side\n")
        git(source_repo, "add", "b.py")
        git(source_repo, "commit", "--quiet", "-m", "side work")
        git(source_repo, "checkout", "--quiet", "trunk")
        (source_repo / "logo.png").write_bytes(bytes(range(256)) * 4)
        git(source_repo, "add", "logo.png")
        git(source_repo, "commit", "--quiet", "-m", "add binary")
        git(source_repo, "merge", "--quiet", "--no-ff", "-m", "Merge side", "side")

        mirror = tmp_path / "mirror.git"
        clone_or_update(str(source_repo), mirror, update=False, timeout=60)
        commits = {c.subject: c for c in read_commits(mirror, "trunk")}

        merge = commits["Merge side"]
        assert merge.is_merge
        assert merge.insertions is None

        binary = commits["add binary"]
        assert binary.binary_files == 1
        assert binary.files_changed == 1
        # The binary file contributes no lines, so the text totals stay zero.
        assert binary.insertions == 0


def test_commit_stat_row_shape(project):
    commit = CommitStat(
        sha="abc",
        parents=("p1", "p2"),
        author_name="Ada",
        author_email="ada@example.com",
        authored_at="2024-01-01T00:00:00+00:00",
        committed_at="2024-01-01T00:00:00+00:00",
        subject="merge",
    )
    row = commit.row(project)
    assert row["is_merge"] == 1
    assert row["project_id"] == "demo"
    assert row["insertions"] is None
