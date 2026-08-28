---
curated:
  id: invisensing
  name: invisensing
  repository: invisensing-io/python-lib
  repository_url: https://github.com/invisensing-io/python-lib
  homepage: null
  description: Vendor Python SDK reading every DAS acquisition format the Audace platform writes.
  status: included
  decision_reason: Reusable vendor-published DAS reader with an MIT license, documentation, CI, and PyPI
    releases.
  primary_category: data-management
  capabilities:
  - conversion
  - data-management
  - io
  license_spdx: MIT
  license_class: osi-approved
  forge:
    kind: github
    host: github.com
  registries:
    pypi:
    - invisensing
    conda: []
    julia: []
  publications: []
collected:
  scanned_at: '2026-08-28T12:56:53+00:00'
  snapshot: '2026-08-28'
  visibility: public
  language: Python
  stars: 0
  forks: 0
  contributors: 1
  releases: 6
  commits: 39
  last_commit_at: '2026-07-22T10:21:55Z'
  created_at: '2024-09-13T11:11:38Z'
  latest_release_at: '2026-07-22T10:32:50Z'
  archived: false
  lines_of_code_estimate: 4024
  loc_basis: language bytes / 32, notebooks excluded
  pypi_downloads_180d: 6215
  pypi_downloads_30d: 304
  dependencies:
  - package: invisensing
    dependency: h5py
    requirement: '>=3.0'
    marker: ''
    dependency_project: null
  - package: invisensing
    dependency: nptdms
    requirement: '>=1.6'
    marker: ''
    dependency_project: null
  - package: invisensing
    dependency: numpy
    requirement: '>=1.20'
    marker: ''
    dependency_project: null
  - package: invisensing
    dependency: segyio
    requirement: '>=1.9'
    marker: ''
    dependency_project: null
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
  ran_at: 2026-08-20 08:14:50+00:00
  duration_seconds: 21.1
  turns: 3
  input_tokens: 10184
  output_tokens: 1472
  cache_read_tokens: 103906
  cache_write_tokens: 7545
  total_tokens: 123107
  api_list_cost_usd: 0.1044
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

# invisensing

Source: [invisensing-io/python-lib](https://github.com/invisensing-io/python-lib)

## Summary

invisensing (python-lib) is a Python SDK for reading Distributed Acoustic Sensing (DAS) acquisition files produced by the Audace platform. It provides a uniform API across multiple vendor file formats and exposes demodulation channels (I/Q, arctan, magnitude, phase) with optional automatic physical-unit scaling, while preserving the original on-board DSP output rather than re-deriving it. The performance-sensitive parsing path is implemented in Rust via PyO3/maturin bindings, with the library citing multi-GB/s throughput and streaming support for large files. It targets researchers and engineers working directly with Audace DAS interrogator output who need fast, format-agnostic file access from Python rather than a generic scientific-computing toolkit.

## Details

- **Interface:** library (Python package with a Rust compiled extension)
- **Data formats:** `.dat` (native Rust backend), HDF5, TDMS, SEG-Y
- **Key dependencies:** NumPy, h5py, npTDMS, segyio; Rust extension built with PyO3/maturin
- **Scope signals:** semantic versioning (1.0.0+), MIT licensed, test suite including performance regression tests, ~39 commits, basic docs and an example script (`assets/basic_usage.py`); appears to be a small, focused, single-vendor-format project rather than a large community effort
- **Source visible:** yes — repository contains `src/lib.rs` (Rust), `python/invisensing/` (Python facade), `tests/`, `docs/`, and `assets/`
- **Sources read:** https://github.com/invisensing-io/python-lib
