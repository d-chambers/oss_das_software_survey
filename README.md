# Open-source DAS ecosystem

A catalogue of reusable software for distributed acoustic sensing (DAS), measured from public sources. 

## Shape

- **A — curate.** Discover → cheap-model triage → agent proposal → human decision. Ends at `data/curated/`.
- **B — measure.** Git, forge, registry, and publication metrics for each curated project. Ends at `data/measured/`.
- **C — present.** Two tables, one marimo notebook (the website).
- **V — figures.** Static figures from the same tables.

```
data/
  raw/candidates/<source>/<key>.md  A  write-once
  raw/coverage.csv                  A  append-only: every probe
  triage.csv                        A  append-only: verdicts, same-project links
  enriched/<id>.md                  A  agent proposal
  curated/<id>.md                   A  human decision; only review.py or an editor writes here
  rejected.yml                      A  never re-proposed
  repos/<id>.git                    B  bare mirrors (gitignored)
  commits/<id>.csv                  B  overwritten
  measured/<source>/<id>.md         B  overwritten
notebooks/
  review.py                         A  local marimo app
  ecosystem.py                      C  published notebook, slides layout
  public/*.csv                      C  tables; marimo ships public/ with the export
figures/<name>.svg, .pdf, figures.json V  one per script; the sidecar holds their numbers
scripts/                               docstrings say what each reads and writes
```

## Rules

- Records are Markdown with YAML frontmatter. Git history is the audit trail.
- Missing values carry a reason, never zero.
- Ledgers are append-only; last row wins. A `model: human` row overrides triage.
- `status` is scope; `license_class` is reuse terms. Rejection means "not a reusable DAS project".
- `sources:` maps candidate keys to `id`. Agent provenance comes from the API response.
- C010 refuses missing or week-old measurements unless `--allow-stale`.

## Run

`scripts/run_all.sh` runs A (without the model layer unless `RUN_MODELS=1`), B, and C in order, stopping at the first failure. Step by step:

```bash
uv sync && export GITHUB_TOKEN=... ANTHROPIC_API_KEY=...
uv run python scripts/a010_discover_forges.py      # then a011, a020, a021
uv run marimo edit notebooks/review.py
uv run python scripts/b010_mirror.py               # then b011–b014
uv run python scripts/c010_build_tables.py
uv run marimo run notebooks/ecosystem.py           # offline talk
uv run marimo export html-wasm notebooks/ecosystem.py -o site/   # GitHub Pages
uv run python scripts/v000_build_all.py           # or any v0NN script alone
```

Code MIT; dataset and site content CC BY 4.0.

## Talk Abstract

As in many scientific fields, seismologists have a long history of developing and distributing domain-specific software. Some of the earliest packages were written in C and Fortran and were primarily used via the command line or through shell scripting. The emergence of a new generation of programming languages, such as Python, R, MATLAB, and Julia, has led to a growing ecosystem of seismological software, lowering the barrier to conducting research and improving interoperability with the broader scientific community. Python, in particular, has become especially popular among seismologists, and several foundational DAS packages have emerged, each with distinct strengths and feature sets. However, compatibility between these packages is not guaranteed. In this talk, I compare the design and capabilities of the existing libraries and provide guidance for researchers and package developers to help reduce ecosystem fragmentation. I also highlight key gaps and opportunities for future contributions within the nascent open-source DAS ecosystem. Finally, I explore the implications of emerging, highly capable coding agents and how they may reshape seismic research and software development. To demonstrate, I present several new experimental projects that illustrate both the dramatic increase in development velocity and the enhanced capabilities enabled by this new generation of tools
