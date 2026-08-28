# Repository instructions

- Add no AI/tool attribution or AI `Co-Authored-By` trailers to commits, PRs, or comments; write as the user.
- Do not hard-wrap Markdown prose; preserve normal blank-line separation.
- Use `AGENTS.md`, not `CLAUDE.md`, for repository-level instructions.
- Follow an applicable PR template when authoring a pull request.
- Do not use coverage pragmas without explicit permission. Prefer assertions for worthwhile defensive checks that should be unreachable.

## Definition of done

For substantive code, configuration, or documentation changes:

1. Run applicable tests and lint; all must pass.
2. Self-review for simpler approaches and duplicated methods or utilities.
3. Request a CLI review from Claude and save it temporarily under `.scratch/`; do not commit it.
4. Address actionable findings and rerun checks.
5. Report review status, exact checks and results, and anything not run.

