---
id: a1das
name: a1das
repository: olivier.coutant/a1das-v2
repository_url: https://gitlab.in2p3.fr/olivier.coutant/a1das-v2
homepage: null
description: Python reader and processing routines for Febus Optics DAS data.
status: included
decision_reason: Reusable Python reader for Febus DAS data. The GitHub repository is a tombstone whose
  only file redirects to the GitLab instance the project moved to in December 2023; that repository is
  the one measured here.
primary_category: data-management
capabilities:
- conversion
- io
- processing
license_spdx: null
license_class: unlicensed
forge:
  kind: gitlab
  host: gitlab.in2p3.fr
registries:
  pypi: []
  conda: []
  julia: []
publications: []
das_focus: das-native
sources:
- github.com/coutanto/a1das
- gitlab.in2p3.fr/olivier.coutant/a1das-v2
reviewed_at: '2026-08-28'
provenance:
  agent: das-summarizer
  models:
  - claude-haiku-4-5-20251001
  - claude-sonnet-5
  ran_at: '2026-08-20T08:07:39+00:00'
  duration_seconds: 43.7
  turns: 10
  input_tokens: 5637
  output_tokens: 3080
  cache_read_tokens: 334742
  cache_write_tokens: 16262
  total_tokens: 359721
  api_list_cost_usd: 0.242
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

## Summary

a1das is a Python library for reading and processing Distributed Acoustic Sensing (DAS) data files produced by Febus Optics interrogator hardware (up to firmware version 2.3.5). It targets researchers and practitioners who need to load and manipulate raw Febus DAS acquisitions in Python rather than the manufacturer's own software. The project is maintained by an individual researcher (Olivier Coutant) rather than by Febus Optics itself, and is explicitly scoped to one vendor's file format rather than being a general-purpose DAS toolkit. It ships optional companion modules for cross-correlation computation and GPU-accelerated seismic display, and includes a Fortran extension (compiled via f2py/gfortran) with a pure-Python fallback to `scipy.signal`, indicating it targets both performance and portability. Development has since moved from GitHub to a GitLab instance under a new "v2" repository.

## Details

- **Interface:** library (Python package installed via pip; no CLI or GUI described in what was read)
- **Data formats:** reads Febus Optics DAS files (proprietary interrogator output, up to version 2.3.5); output format not stated
- **Key dependencies:** `scipy.signal` (fallback for the compiled Fortran module); a Fortran extension built with `f2py`/`gfortran`; optional companion modules "A1-XCORPY" (cross-correlation) and "APlot" (GPU-accelerated visualization) — no other dependencies stated
- **Scope signals:** single-maintainer project; original GitHub repo had 52 commits, 3 stars, 2 watchers, 1 fork, 1 open issue; development moved to a GitLab repo ("a1das-v2") with 178 commits across 4 branches and no tagged releases; documentation provided as HTML (online and downloadable) and PDF, suggesting a research-tool audience rather than a broad user base
- **Source visible:** yes — source is published, both in the original (now-archived, moved) GitHub repository and the active GitLab repository
- **Sources read:** https://github.com/coutanto/a1das, https://gitlab.in2p3.fr/olivier.coutant/a1das-v2, https://gitlab.in2p3.fr/olivier.coutant/a1das-v2/-/raw/main/README.md
