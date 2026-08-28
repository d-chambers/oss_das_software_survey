---
curated:
  id: opendas-stream
  name: OpenDAS-Stream
  repository: Xinxin-He/OpenDAS-Stream
  repository_url: https://github.com/Xinxin-He/OpenDAS-Stream
  homepage: null
  description: GPU-accelerated streaming analytics for terabyte-scale DAS archives.
  status: watchlist
  decision_reason: MIT licensed and DAS-specific, but the repository holds four demonstration scripts
    with no packaging, tests, or documented interface, so its reusability is unresolved.
  primary_category: processing
  capabilities:
  - parallel-computing
  - processing
  - streaming
  license_spdx: MIT
  license_class: osi-approved
  forge:
    kind: github
    host: github.com
  registries:
    pypi: []
    conda: []
    julia: []
  publications: []
collected:
  scanned_at: '2026-08-28T12:57:03+00:00'
  snapshot: '2026-08-28'
  visibility: public
  language: Python
  stars: 0
  forks: 0
  contributors: 1
  releases: 0
  commits: 17
  last_commit_at: '2026-03-03T23:09:00Z'
  created_at: '2026-03-03T22:30:40Z'
  archived: false
  lines_of_code_estimate: 3184
  loc_basis: language bytes / 32, notebooks excluded
  dependencies: []
  has_docs: false
  has_tests: false
  has_ci: false
  unavailable:
    pypi_downloads_total: no free source publishes all-time PyPI totals
    conda_downloads_180d: anaconda.org publishes a cumulative count only, with no time series
summary:
  agent: das-summarizer
  models:
  - claude-haiku-4-5-20251001
  - claude-sonnet-5
  ran_at: 2026-08-20 08:16:58+00:00
  duration_seconds: 29.5
  turns: 5
  input_tokens: 7058
  output_tokens: 2218
  cache_read_tokens: 149118
  cache_write_tokens: 2735
  total_tokens: 161129
  api_list_cost_usd: 0.0954
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

# OpenDAS-Stream

Source: [Xinxin-He/OpenDAS-Stream](https://github.com/Xinxin-He/OpenDAS-Stream)

## Summary

OpenDAS-Stream is a Python framework for processing very large distributed acoustic sensing (DAS) datasets, aimed at geohazard and subsurface-monitoring research. It targets fiber-optic sensor data at "100-terabyte scale" and uses an overlap-save chunking scheme to run continuous or streaming analysis rather than one-off batch jobs. It implements a small set of named geophysical algorithms — LFDAS (low-frequency strain extraction), F-K analysis (wavefield separation), and FBE-RMS (energy mapping) — and relies on GPU acceleration (CUDA via CuPy) with a CPU fallback (SciPy) to make that scale tractable. It is presented as a research tool, developed under an ICDS Rising Researcher initiative, and is intended for researchers doing GPU-accelerated signal processing on DAS/fiber-optic data rather than general-purpose signal-processing users.

## Details

- **Interface:** Python library, orchestrated through a `main.py` entry point; no documented CLI flags or usage beyond a minimal Python snippet
- **Data formats:** not stated (README does not name specific input/output file formats such as HDF5, TDMS, SEG-Y, or MiniSEED)
- **Key dependencies:** Python 3.8+, CuPy (CUDA GPU backend), SciPy (CPU fallback)
- **Scope signals:** described as a research/experimental tool (ICDS Rising Researcher project) rather than production software; claims processing of 4.5 TB of continuous DAS data in 15 minutes as a demonstrated capability; 0 stars, 0 forks, MIT license
- **Source visible:** yes — repository contains actual source files (17 commits, multiple directories), including `filter_core.py`, `compute_core.py`, and `plotters.py`
- **Sources read:** https://github.com/Xinxin-He/OpenDAS-Stream, https://raw.githubusercontent.com/Xinxin-He/OpenDAS-Stream/main/README.md
