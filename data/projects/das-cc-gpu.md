---
curated:
  id: das-cc-gpu
  name: DAS_CC_GPU
  repository: zhichaoshen40/DAS_CC_GPU
  repository_url: https://github.com/zhichaoshen40/DAS_CC_GPU
  homepage: null
  description: GPU cross-correlation and preprocessing programs for DAS ambient-noise workflows.
  status: included
  decision_reason: Reusable DAS-specific command-line toolchain in C and CUDA under GPL-3.0.
  primary_category: processing
  capabilities:
  - parallel-computing
  - processing
  - seismology
  license_spdx: GPL-3.0-only
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
  scanned_at: '2026-08-28T12:54:56+00:00'
  snapshot: '2026-08-28'
  visibility: public
  language: C
  stars: 10
  forks: 0
  contributors: 1
  releases: 1
  commits: 7
  last_commit_at: '2024-08-08T15:51:13Z'
  created_at: '2024-04-20T21:12:35Z'
  latest_release_at: '2024-07-02T02:58:04Z'
  archived: false
  lines_of_code_estimate: 5016
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
  ran_at: 2026-08-20 08:08:05+00:00
  duration_seconds: 26.5
  turns: 4
  input_tokens: 9302
  output_tokens: 1883
  cache_read_tokens: 143038
  cache_write_tokens: 8106
  total_tokens: 162329
  api_list_cost_usd: 0.1228
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

# DAS_CC_GPU

Source: [zhichaoshen40/DAS_CC_GPU](https://github.com/zhichaoshen40/DAS_CC_GPU)

## Summary

DAS_CC_GPU is a CUDA implementation for computing cross-correlations of distributed acoustic sensing (DAS) data on GPUs, intended for seismic ambient noise analysis workflows. It is organized as a four-step pipeline covering preprocessing, cross-correlation computation, SEGY-to-SAC format conversion, and optional stacking of cross-correlations. Researchers processing large-volume DAS records for ambient-noise seismology would use this to accelerate the correlation step, which is computationally expensive on CPU. What distinguishes it from a generic signal-processing toolkit is its narrow, task-specific scope: it is not a general DAS library but a purpose-built GPU pipeline for one processing stage, with a companion Python/CPU implementation referenced for users without GPU access. Documentation beyond the minimal README is provided as a PDF rather than inline markdown.

## Details

- **Interface:** CLI / compiled pipeline (staged CUDA programs run in sequence: STEP1–STEP4), not a library API
- **Data formats:** reads SEGY seismic data; writes SAC format (conversion is STEP3 of the pipeline)
- **Key dependencies:** CUDA (explicitly stated); no other libraries (e.g., cuFFT, MPI, OpenMP) are named in the README or file listing
- **Scope signals:** small research codebase — 10 stars, 0 forks, GPL-3.0 license, documentation split between a brief README.md and a separate Readme.pdf; README points to a Python/CPU equivalent project for non-GPU users, suggesting a narrow, specialist audience
- **Source visible:** yes — the repository contains actual source (four staged directories: STEP1_preprocessing, STEP2_xcorr, STEP3_segy2sac, STEP4_stackcc_optional) plus a params.h configuration header, not just a description
- **Sources read:** https://github.com/zhichaoshen40/DAS_CC_GPU
