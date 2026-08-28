---
curated:
  id: fiberis
  name: fibeRIS
  repository: shenyaojin/fibeRIS
  repository_url: https://github.com/shenyaojin/fibeRIS
  homepage: null
  description: Analysis, simulation, and data management across fiber-optic sensing modalities.
  status: watchlist
  decision_reason: OSI-licensed and actively developed, but it spans DTS, DSS, and gauge data rather than
    targeting DAS, so its scope overlap is still under review.
  primary_category: core-framework
  capabilities:
  - data-management
  - data-model
  - io
  - modeling
  - processing
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
  scanned_at: '2026-08-28T12:56:37+00:00'
  snapshot: '2026-08-28'
  visibility: public
  language: Python
  stars: 2
  forks: 1
  contributors: 3
  releases: 0
  commits: 313
  last_commit_at: '2026-07-21T15:47:10Z'
  created_at: '2025-02-01T00:56:41Z'
  archived: false
  lines_of_code_estimate: 28588
  loc_basis: language bytes / 32, notebooks excluded
  dependencies: []
  has_docs: true
  has_tests: true
  has_ci: true
  unavailable:
    pypi_downloads_total: no free source publishes all-time PyPI totals
    conda_downloads_180d: anaconda.org publishes a cumulative count only, with no time series
summary:
  agent: das-summarizer
  models:
  - claude-haiku-4-5-20251001
  - claude-sonnet-5
  ran_at: 2026-08-20 08:14:18+00:00
  duration_seconds: 25.2
  turns: 4
  input_tokens: 6821
  output_tokens: 1957
  cache_read_tokens: 143116
  cache_write_tokens: 8265
  total_tokens: 160159
  api_list_cost_usd: 0.1213
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

# fibeRIS

Source: [shenyaojin/fibeRIS](https://github.com/shenyaojin/fibeRIS)

## Summary

fibeRIS is a Python toolkit for analyzing, simulating, and managing data related to reservoir engineering, with a particular emphasis on distributed fiber optic sensing (DFOS). It provides typed data-handler classes for 1D time-series, 2D spatiotemporal, and 3D volumetric datasets, plus dedicated classes for wellbore geometry and tensor (stress/strain) data, alongside signal-processing utilities (filtering, spectral analysis, outlier removal) and visualization helpers. It also includes pressure-diffusion simulation code and integration with the MOOSE multiphysics framework. It would suit reservoir engineers and researchers who need to combine DAS waterfall data with pumping-curve and gauge-pressure records for a single well or field study, rather than a generic signal-processing library, since its class hierarchy is organized around oilfield-specific concepts (wellbore trajectories, pumping curves, gauge pressure) instead of sensor-agnostic array data.

## Details

- **Interface:** library (pip-installable Python package: `pip install fiberis`, or `pip install -e .` from source)
- **Data formats:** not stated (README references "DAS waterfall plots," "pumping curves," and "gauge pressure" data conceptually, but does not name specific file formats/extensions)
- **Key dependencies:** numpy, scipy, matplotlib, pandas; pytest for testing
- **Scope signals:** small research project — 2 stars, 1 fork, 313 commits on main; created by Shenyao Jin (shenyaojin@mines.edu) for research purposes; includes a pytest test suite and an examples directory; dual-licensed MIT/WTFPL
- **Source visible:** yes — repository contains `src/`, `tests/`, `examples/`, and `docs/` directories with actual code, not just a description
- **Sources read:** https://github.com/shenyaojin/fibeRIS, https://raw.githubusercontent.com/shenyaojin/fibeRIS/main/README.md
