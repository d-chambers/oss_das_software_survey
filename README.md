# Open-source DAS ecosystem

This repository builds a dated, auditable dataset of reusable software for distributed acoustic sensing (DAS) and renders offline-capable interactive HTML pages for conference use.

Every reusable DAS code found is catalogued regardless of its license, and the reuse terms are recorded as a separate, countable property. Filtering the list down to OSI-approved projects first would make "what share of this ecosystem is open source" unanswerable from the result. Projects live on whichever host publishes them, so GitHub, GitLab, and Gitea instances are all first-class.

The comparison is deliberately faceted. Repository activity, scholarly citations, PyPI traffic, conda downloads, Julia registry membership, maintenance signals, and manually reviewed capabilities are shown separately because they have different meanings and collection windows.

## Quick start

```bash
uv sync
uv run python scripts/a000_run_all.py --snapshot-date 2026-08-03 --offline
```

To collect fresh public metadata, set `GITHUB_TOKEN` and, when required by OpenAlex, `OPENALEX_API_KEY`, then omit `--offline`:

```bash
uv run python scripts/a000_run_all.py --snapshot-date "$(date +%F)" --collect
```

Discovery is intentionally separate from inclusion. Run `a010_discover_projects.py`, review the resulting candidate list, and edit the `curated` block of the relevant file in `data/projects/`; automated discovery never silently promotes a repository into the main comparison.

Discovery pages every GitHub search rather than keeping only the first hundred hits, queries the physics and vendor vocabulary the acronym hides behind, walks the repository list of every organization already catalogued, and sweeps GitLab and Gitea hosts including institutional instances. Each probe writes a row to `discovery_coverage.csv` recording what it retrieved, what the host claimed to hold, and whether the answer was truncated — so a query that hit a cap is visible rather than silent.

## Pipeline

| Script | Output |
| --- | --- |
| `a010_discover_projects.py` | Multi-host candidates, plus per-probe discovery coverage |
| `a020_collect_github.py` | Repository, contributor, release, and project-signal snapshots from every host |
| `a030_collect_registries.py` | PyPI, PyPI Stats, conda, and Julia registry snapshots |
| `a040_collect_publications.py` | OpenAlex publication and citation snapshots |
| `a050_build_dataset.py` | Normalized public CSV dataset and manifest |
| `a060_validate_dataset.py` | Dataset contract validation |
| `a100`–`a150` | Interactive pages under `docs/`, including capability-overlap and direct-dependency networks |

Every collection value records its source and retrieval time. Missing metrics carry a reason such as `not_published`, `not_applicable`, `unavailable`, or `fetch_error`; missing values are never converted to zero.

Counts are not silently pooled across hosts. Contributor figures state whether they came from GitHub's linked accounts or GitLab's commit identities, continuous integration is probed per host, and a detected license records the vocabulary it was expressed in rather than being labelled SPDX regardless of origin.

## Presentation

`docs/presentation.qmd` is a Quarto reveal.js deck that reads the newest dated snapshot at render time, so its figures and quoted numbers cannot drift from the dataset.

```bash
uv run quarto render docs/presentation.qmd
```

Quarto and the `dev` dependency group are both required. The rendered `docs/presentation.html` inlines plotly and needs no conference internet access. Speaker view is `s`; a PDF fallback comes from appending `?print-pdf` to the URL and printing from the browser.

## Outputs

Each dated snapshot is stored under `data/snapshots/YYYY-MM-DD/`. Generated pages are written to `docs/`, with copies of the public CSV files under `docs/data/`. The pages embed Plotly locally and do not require conference internet access.

Code is MIT licensed. Original dataset and site content are CC BY 4.0; upstream source terms still apply.

## Talk Abstract

As in many scientific fields, seismologists have a long history of developing and distributing domain-specific software. Some of the earliest packages were written in C and Fortran and were primarily used via the command line or through shell scripting. The emergence of a new generation of programming languages, such as Python, R, MATLAB, and Julia, has led to a growing ecosystem of seismological software, lowering the barrier to conducting research and improving interoperability with the broader scientific community. Python, in particular, has become especially popular among seismologists, and several foundational DAS packages have emerged, each with distinct strengths and feature sets. However, compatibility between these packages is not guaranteed. In this talk, I compare the design and capabilities of the existing libraries and provide guidance for researchers and package developers to help reduce ecosystem fragmentation. I also highlight key gaps and opportunities for future contributions within the nascent open-source DAS ecosystem. Finally, I explore the implications of emerging, highly capable coding agents and how they may reshape seismic research and software development. To demonstrate, I present several new experimental projects that illustrate both the dramatic increase in development velocity and the enhanced capabilities enabled by this new generation of tools
