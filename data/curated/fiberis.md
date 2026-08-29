---
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
  pypi:
  - fiberis
  conda: []
  julia: []
publications: []
das_focus: das-native
sources:
- github.com/shenyaojin/fiberis
reviewed_at: '2026-08-28'
provenance:
  agent: das-summarizer
  models:
  - claude-haiku-4-5-20251001
  - claude-sonnet-5
  ran_at: '2026-08-20T08:14:18+00:00'
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

## Summary

fibeRIS is a Python toolkit for analyzing, simulating, and managing data related to reservoir engineering, with a particular emphasis on distributed fiber optic sensing (DFOS). It provides typed data-handler classes for 1D time-series, 2D spatiotemporal, and 3D volumetric datasets, plus dedicated classes for wellbore geometry and tensor (stress/strain) data, alongside signal-processing utilities (filtering, spectral analysis, outlier removal) and visualization helpers. It also includes pressure-diffusion simulation code and integration with the MOOSE multiphysics framework. It would suit reservoir engineers and researchers who need to combine DAS waterfall data with pumping-curve and gauge-pressure records for a single well or field study, rather than a generic signal-processing library, since its class hierarchy is organized around oilfield-specific concepts (wellbore trajectories, pumping curves, gauge pressure) instead of sensor-agnostic array data.

## Details

- **Interface:** library (pip-installable Python package: `pip install fiberis`, or `pip install -e .` from source)
- **Data formats:** not stated (README references "DAS waterfall plots," "pumping curves," and "gauge pressure" data conceptually, but does not name specific file formats/extensions)
- **Key dependencies:** numpy, scipy, matplotlib, pandas; pytest for testing
- **Scope signals:** small research project — 2 stars, 1 fork, 313 commits on main; created by Shenyao Jin (shenyaojin@mines.edu) for research purposes; includes a pytest test suite and an examples directory; dual-licensed MIT/WTFPL
- **Source visible:** yes — repository contains `src/`, `tests/`, `examples/`, and `docs/` directories with actual code, not just a description
- **Sources read:** https://github.com/shenyaojin/fibeRIS, https://raw.githubusercontent.com/shenyaojin/fibeRIS/main/README.md
