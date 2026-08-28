---
curated:
  id: sigrecover
  name: sigrecover
  repository: TCCS-CODES/sigrecover
  repository_url: https://github.com/TCCS-CODES/sigrecover
  homepage: null
  description: MATLAB dictionary-learning routines for recovering weak signals from DAS noise.
  status: included
  decision_reason: Reusable MATLAB subroutine library under BSD-3-Clause, shipped with runnable examples
    rather than figure scripts alone.
  primary_category: processing
  capabilities:
  - denoising
  - processing
  - visualization
  license_spdx: BSD-3-Clause
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
  scanned_at: '2026-08-28T12:57:17+00:00'
  snapshot: '2026-08-28'
  visibility: public
  language: MATLAB
  stars: 10
  forks: 4
  contributors: 1
  releases: 0
  commits: 9
  last_commit_at: '2024-07-31T22:50:17Z'
  created_at: '2024-07-31T21:02:30Z'
  archived: false
  lines_of_code_estimate: 2349
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
  ran_at: 2026-08-20 08:16:59+00:00
  duration_seconds: 27.6
  turns: 4
  input_tokens: 8350
  output_tokens: 1844
  cache_read_tokens: 143056
  cache_write_tokens: 8171
  total_tokens: 161421
  api_list_cost_usd: 0.1209
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

# sigrecover

Source: [TCCS-CODES/sigrecover](https://github.com/TCCS-CODES/sigrecover)

## Summary

sigrecover is a MATLAB code package accompanying the 2024 Seismological Research Letters paper "SigRecover: Recovering signal from noise in distributed acoustic sensing data processing" by Yangkang Chen. It implements methods for recovering weak signals buried in noise within DAS data, packaged as a set of reproducible research scripts rather than a general-purpose processing toolkit. Each `test_figNO.m` script in the `main/` directory regenerates a specific figure from the paper, drawing on shared routines in a `subroutines/` directory. It would be used by researchers reproducing or extending the published denoising/signal-recovery method, or comparing it against other DAS processing algorithms, rather than by practitioners needing an end-to-end acquisition-to-interpretation pipeline. What distinguishes it from a generic signal-processing toolkit is its tight coupling to one published method and paper, with reproducibility of exact figures as the explicit design goal.

## Details

- **Interface:** library (MATLAB scripts/functions, no CLI or GUI)
- **Data formats:** not stated
- **Key dependencies:** MATLAB (2022b or later noted for consistent font rendering); no external package dependencies mentioned
- **Scope signals:** small, single-paper research codebase (repository reports 9 commits, 10 stars, 4 forks); README states "future versions may also support Python and be optimized regarding computational efficiency," indicating current MATLAB-only, early-stage status; BSD-3-Clause license
- **Source visible:** yes, source code (main scripts and subroutines) is published in the repository, not just a description
- **Sources read:** https://github.com/TCCS-CODES/sigrecover, https://raw.githubusercontent.com/TCCS-CODES/sigrecover/main/README.md
