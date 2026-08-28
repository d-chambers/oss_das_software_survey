---
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
das_focus: das-native
sources:
- github.com/tccs-codes/sigrecover
reviewed_at: '2026-08-28'
provenance:
  agent: das-summarizer
  models:
  - claude-haiku-4-5-20251001
  - claude-sonnet-5
  ran_at: '2026-08-20T08:16:59+00:00'
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

## Summary

sigrecover is a MATLAB code package accompanying the 2024 Seismological Research Letters paper "SigRecover: Recovering signal from noise in distributed acoustic sensing data processing" by Yangkang Chen. It implements methods for recovering weak signals buried in noise within DAS data, packaged as a set of reproducible research scripts rather than a general-purpose processing toolkit. Each `test_figNO.m` script in the `main/` directory regenerates a specific figure from the paper, drawing on shared routines in a `subroutines/` directory. It would be used by researchers reproducing or extending the published denoising/signal-recovery method, or comparing it against other DAS processing algorithms, rather than by practitioners needing an end-to-end acquisition-to-interpretation pipeline. What distinguishes it from a generic signal-processing toolkit is its tight coupling to one published method and paper, with reproducibility of exact figures as the explicit design goal.

## Details

- **Interface:** library (MATLAB scripts/functions, no CLI or GUI)
- **Data formats:** not stated
- **Key dependencies:** MATLAB (2022b or later noted for consistent font rendering); no external package dependencies mentioned
- **Scope signals:** small, single-paper research codebase (repository reports 9 commits, 10 stars, 4 forks); README states "future versions may also support Python and be optimized regarding computational efficiency," indicating current MATLAB-only, early-stage status; BSD-3-Clause license
- **Source visible:** yes, source code (main scripts and subroutines) is published in the repository, not just a description
- **Sources read:** https://github.com/TCCS-CODES/sigrecover, https://raw.githubusercontent.com/TCCS-CODES/sigrecover/main/README.md
