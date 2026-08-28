---
curated:
  id: alakoro-fibersense
  name: Alakoro FiberSense
  repository: Colombiano/Alakoro_FiberSense
  repository_url: https://github.com/Colombiano/Alakoro_FiberSense
  homepage: null
  description: Multi-modal DFOS processing and simulation platform for oil and gas wells.
  status: included
  decision_reason: Reusable DFOS platform with an MIT license, packaging, and documentation. The README
    advertises a PyPI release that does not resolve, so no registry name is declared.
  primary_category: application-domain
  capabilities:
  - io
  - modeling
  - processing
  - visualization
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
  scanned_at: '2026-08-28T12:54:42+00:00'
  snapshot: '2026-08-28'
  visibility: public
  language: Python
  stars: 0
  forks: 0
  contributors: 1
  releases: 0
  commits: 23
  last_commit_at: '2026-07-18T11:33:26Z'
  created_at: '2026-07-11T21:26:42Z'
  archived: false
  lines_of_code_estimate: 2823
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
  ran_at: 2026-08-20 08:07:39+00:00
  duration_seconds: 34.6
  turns: 5
  input_tokens: 12035
  output_tokens: 2422
  cache_read_tokens: 176178
  cache_write_tokens: 15121
  total_tokens: 205756
  api_list_cost_usd: 0.1833
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

# Alakoro FiberSense

Source: [Colombiano/Alakoro_FiberSense](https://github.com/Colombiano/Alakoro_FiberSense)

## Summary

Alakoro FiberSense is a Python platform for processing, simulating, and interpreting distributed fiber optic sensing data from oil and gas wells, covering DAS (acoustic), DTS (temperature), and DSS (strain) sensing modalities. It generates synthetic sensing signatures and well-geometry models, and includes a semantic event-detection layer built on a JSON Schema (v1.1.0) covering 18 event types across 15 canonical signatures. The intended users are petroleum/reservoir engineers and researchers analyzing well behavior from fiber sensing arrays, including non-programmers who use a packaged GUI installer rather than the Python API directly. What distinguishes it from a generic signal-processing toolkit is its domain-specific focus: canonical signature libraries and a structured event taxonomy tailored to oil-and-gas well diagnostics, rather than general DAS waveform processing.

## Details

- **Interface:** library (pip-installable Python package), plus a GUI installer (Windows batch/Unix shell/Python GUI), a Docker container, and a Jupyter notebook (Colab-compatible) demo
- **Data formats:** not stated (README does not name specific file formats such as LAS, HDF5, TDMS, or SEG-Y)
- **Key dependencies:** numpy, scipy, matplotlib, pytest (from requirements.txt)
- **Scope signals:** version 2.2.1, described as supporting well arrays of up to ~3,000 channels; 40+ unit tests with claimed 91.3% validation coverage; GitHub Actions CI/CD for testing, linting, and releases; published to PyPI (`alakoro-fibersense`) and Docker Hub; bilingual (Portuguese/English) documentation; MIT licensed
- **Source visible:** yes — source code is published under `/src` with corresponding tests, not just a description
- **Sources read:** https://github.com/Colombiano/Alakoro_FiberSense, https://raw.githubusercontent.com/Colombiano/Alakoro_FiberSense/main/README.md, https://raw.githubusercontent.com/Colombiano/Alakoro_FiberSense/main/requirements.txt
