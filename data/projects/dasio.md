---
curated:
  id: dasio
  name: dasio
  repository: jxli2a/dasio
  repository_url: https://github.com/jxli2a/dasio
  homepage: null
  description: Basic input, output, and processing helpers for DAS file formats.
  status: included
  decision_reason: Reusable DAS-specific Python package with an MIT license.
  primary_category: data-management
  capabilities:
  - data-management
  - io
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
  scanned_at: '2026-08-28T12:55:52+00:00'
  snapshot: '2026-08-28'
  visibility: public
  language: Python
  stars: 0
  forks: 0
  contributors: 1
  releases: 0
  commits: 58
  last_commit_at: '2026-08-09T13:01:43Z'
  created_at: '2026-06-26T00:21:49Z'
  archived: false
  lines_of_code_estimate: 14063
  loc_basis: language bytes / 32, notebooks excluded
  dependencies: []
  has_docs: false
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
  ran_at: 2026-08-20 08:11:36+00:00
  duration_seconds: 30.0
  turns: 4
  input_tokens: 6409
  output_tokens: 2117
  cache_read_tokens: 142995
  cache_write_tokens: 8255
  total_tokens: 159776
  api_list_cost_usd: 0.1233
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

# dasio

Source: [jxli2a/dasio](https://github.com/jxli2a/dasio)

## Summary

dasio is a Python library providing input/output and lightweight signal processing for distributed acoustic sensing (DAS) data. It supplies vendor-specific HDF5 readers for ASN/OptoDAS, OptaSense/QuantX, and AP Sensing instruments, converts raw vendor measurements to physical units, and exposes a numpy-based container (`DASdata`) for downstream analysis such as bandpass filtering (implemented in C++/OpenMP) and common-mode subtraction. It also includes internal Proc/Basic/Event file formats for storing processed data and a cataloging component (`DASdb`) for time-windowed queries across multiple files. This targets DAS researchers and practitioners who need to normalize data across hardware vendors before analysis, rather than end users seeking a turnkey visualization or interpretation tool; optional extras add interactive plotting, PyTorch-based ambient-noise cross-correlation, and PhaseNet-DAS phase picking.

## Details

- **Interface:** library (Python package with a C++ extension; no CLI or GUI described, though an optional interactive viewer extra exists)
- **Data formats:** reads vendor HDF5 files (ASN/OptoDAS, OptaSense/QuantX, AP Sensing); writes/uses internal Proc, Basic, and Event formats, plus CSV catalogs via DASdb
- **Key dependencies:** pybind11, scikit-build-core, C++14/CMake/OpenMP for the compiled bandpass extension; optional fastplotlib and ipywidgets (viewer), PyTorch (noise cross-correlation, PhaseNet-DAS phase picking)
- **Scope signals:** early-stage, MIT-licensed, 0 GitHub stars at time of reading; requires editable (`pip install -e .`) installation due to the C++ extension; optional features are lazily loaded so the core library works without them; documentation notes handling of vendor-specific quirks like OptaSense 32-bit rollover unwrapping, suggesting active use with real instrument data rather than a toy example
- **Source visible:** yes, the repository publishes source code (Python package plus a C++/OpenMP extension), confirmed via README and quickstart usage examples
- **Sources read:** https://github.com/jxli2a/dasio, https://raw.githubusercontent.com/jxli2a/dasio/main/README.md
