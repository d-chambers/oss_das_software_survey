---
curated:
  id: remi-das
  name: ReMi-DAS
  repository: Shihao-Yuan/ReMi-DAS
  repository_url: https://github.com/Shihao-Yuan/ReMi-DAS
  homepage: null
  description: Refraction microtremor analysis specialized for DAS recordings.
  status: included
  decision_reason: Reusable DAS-specific processing toolkit with GPL-3.0 licensing.
  primary_category: processing
  capabilities:
  - processing
  - surface-waves
  - visualization
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
  scanned_at: '2026-08-18T06:39:04+00:00'
  snapshot: '2026-08-17'
  visibility: public
  language: Jupyter Notebook
  stars: 4
  forks: 2
  contributors: 1
  releases: 0
  commits: 15
  last_commit_at: '2026-01-08T20:34:23Z'
  created_at: '2025-07-08T16:17:36Z'
  archived: false
  lines_of_code_estimate: 540
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
  ran_at: 2026-08-20 08:16:31+00:00
  duration_seconds: 26.2
  turns: 4
  input_tokens: 6817
  output_tokens: 1913
  cache_read_tokens: 143091
  cache_write_tokens: 8173
  total_tokens: 159994
  api_list_cost_usd: 0.1208
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

# ReMi-DAS

Source: [Shihao-Yuan/ReMi-DAS](https://github.com/Shihao-Yuan/ReMi-DAS)

## Summary

ReMi-DAS is an open-source toolkit for applying Refraction Microtremor (ReMi) analysis to Distributed Acoustic Sensing (DAS) data, producing shear-wave velocity profiles from passive ambient-noise recordings. It converts DAS strain-rate measurements into slowness-frequency images and dispersion curves, the standard ReMi workflow output, adapted to work with fiber-optic sensing arrays rather than conventional geophone lines. The intended users are seismologists and geophysicists doing near-surface characterization, particularly in urban or infrastructure-constrained settings where deploying traditional seismic arrays is difficult but fiber is already present. What distinguishes it from a generic seismic-processing toolkit is its narrow focus on one specific method (ReMi) applied specifically to DAS strain-rate data, built directly on the DASCore data model, plus an included synthetic-data notebook that simulates traffic noise as a Poisson process of vehicle pass-bys to test processing parameters before applying them to field data.

## Details

- **Interface:** library of modular Python scripts plus Jupyter notebooks demonstrating the workflow; no CLI or GUI
- **Data formats:** input is DAS data compatible with DASCore `Patch` objects; output is dispersion curves and slowness-frequency images; no specific file format (e.g. HDF5/TDMS/SEG-Y) stated
- **Key dependencies:** DASCore (explicitly named as the foundational dependency); no other dependencies were stated in what was read
- **Scope signals:** README explicitly labels it "a development build" that "may contain errors or unstable functionality"; single-author project (Shihao Yuan); no installation instructions, dependency list, or license section were found
- **Source visible:** yes, the repository contains actual Python implementation files organized under `src/` and `notebooks/`, not just a description
- **Sources read:** https://github.com/Shihao-Yuan/ReMi-DAS, https://raw.githubusercontent.com/Shihao-Yuan/ReMi-DAS/main/README.md
