---
curated:
  id: pyseafom
  name: pySEAFOM
  repository: SEAFOM-Fiber-Optic-Monitoring-Group/pySEAFOM
  repository_url: https://github.com/SEAFOM-Fiber-Optic-Monitoring-Group/pySEAFOM
  homepage: https://seafom-fiber-optic-monitoring-group.github.io/pySEAFOM/
  description: Reproducible performance evaluation for DAS and other fiber-optic interrogators.
  status: included
  decision_reason: Reusable benchmarking package under the MIT license.
  primary_category: benchmarking
  capabilities:
  - benchmarking
  - interrogator-evaluation
  - visualization
  license_spdx: MIT
  license_class: osi-approved
  forge:
    kind: github
    host: github.com
  registries:
    pypi:
    - pySEAFOM
    conda: []
    julia: []
  publications: []
collected:
  scanned_at: '2026-08-28T12:57:11+00:00'
  snapshot: '2026-08-28'
  visibility: public
  language: Jupyter Notebook
  stars: 8
  forks: 3
  contributors: 2
  releases: 1
  commits: 72
  last_commit_at: '2026-03-21T16:38:30Z'
  created_at: '2025-07-13T10:54:17Z'
  latest_release_at: '2026-03-21T16:23:21Z'
  archived: false
  lines_of_code_estimate: 4505
  loc_basis: language bytes / 32, notebooks excluded
  pypi_downloads_180d: 531
  pypi_downloads_30d: 23
  dependencies:
  - package: pySEAFOM
    dependency: matplotlib
    requirement: '>=3.3.0'
    marker: ''
    dependency_project: null
  - package: pySEAFOM
    dependency: numpy
    requirement: '>=1.20.0'
    marker: ''
    dependency_project: null
  - package: pySEAFOM
    dependency: scipy
    requirement: '>=1.7.0'
    marker: ''
    dependency_project: null
  has_docs: true
  has_tests: false
  has_ci: true
  unavailable:
    pypi_downloads_total: no free source publishes all-time PyPI totals
    conda_downloads_180d: anaconda.org publishes a cumulative count only, with no time series
summary:
  agent: das-summarizer
  models:
  - claude-haiku-4-5-20251001
  - claude-sonnet-5
  ran_at: 2026-08-20 08:16:24+00:00
  duration_seconds: 33.2
  turns: 5
  input_tokens: 14302
  output_tokens: 2529
  cache_read_tokens: 182615
  cache_write_tokens: 8948
  total_tokens: 208394
  api_list_cost_usd: 0.1507
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

# pySEAFOM

Source: [SEAFOM-Fiber-Optic-Monitoring-Group/pySEAFOM](https://github.com/SEAFOM-Fiber-Optic-Monitoring-Group/pySEAFOM)

## Summary

pySEAFOM is a Python library for performance analysis and testing of Distributed Acoustic Sensing (DAS) interrogators, developed under SEAFOM's Measuring Sensor Performance (MSP) group. It implements standardized test procedures — self-noise (amplitude spectral density), dynamic range, fidelity (total harmonic distortion), crosstalk, frequency response, and spatial resolution — as reusable functions rather than a generic signal-processing toolkit. It is intended for engineers and researchers benchmarking DAS interrogator hardware against SEAFOM's published recommended procedures, so results are consistent and comparable across vendors and labs. Unlike general DSP or fiber-sensing packages, its scope is narrowly the metrology of interrogator performance testing, with each module producing the specific plots, CSV reports, and console summaries defined by the corresponding SEAFOM MSP document.

## Details

- **Interface:** library (installable via `pip install pySEAFOM`), with modular function-based APIs; example notebooks referenced in the repo
- **Data formats:** input as NumPy `.npy` files (2D arrays of channels × time or time × space); outputs are CSV reports and PNG figures per module (e.g., ASD spectra, THD/harmonics, crosstalk profiles, frequency response curves, spatial resolution widths)
- **Key dependencies:** numpy (≥1.20.0), scipy (≥1.7.0), matplotlib (≥3.3.0)
- **Scope signals:** declared development status "Alpha," version 0.1.10, 8 stars / 3 forks / 72 commits — a small, early-stage, specialized tool aimed at fiber-optic sensing test/compliance engineers rather than a general audience
- **Source visible:** yes, source code is published in the repository (not just a description)
- **Sources read:** https://github.com/SEAFOM-Fiber-Optic-Monitoring-Group/pySEAFOM, https://seafom-fiber-optic-monitoring-group.github.io/pySEAFOM/, https://raw.githubusercontent.com/SEAFOM-Fiber-Optic-Monitoring-Group/pySEAFOM/main/pyproject.toml
