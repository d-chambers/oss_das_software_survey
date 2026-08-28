---
curated:
  id: dss-analyzer
  name: DSS_analyzer_Mariner
  repository: shenyaojin/DSS_analyzer_Mariner
  repository_url: https://github.com/shenyaojin/DSS_analyzer_Mariner
  homepage: null
  description: Distributed strain sensing processing tools for the Bakken Mariner project.
  status: watchlist
  decision_reason: OSI-licensed and archived by its author; the modality is distributed strain sensing
    rather than DAS.
  primary_category: processing
  capabilities:
  - io
  - processing
  - strain-sensing
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
  scanned_at: '2026-08-28T12:56:21+00:00'
  snapshot: '2026-08-28'
  visibility: public
  language: Python
  stars: 3
  forks: 0
  contributors: 1
  releases: 0
  commits: 53
  last_commit_at: '2025-01-31T21:03:53Z'
  created_at: '2023-10-06T00:04:02Z'
  archived: true
  lines_of_code_estimate: 1637
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
  ran_at: 2026-08-20 08:13:02+00:00
  duration_seconds: 33.4
  turns: 5
  input_tokens: 9524
  output_tokens: 2396
  cache_read_tokens: 181844
  cache_write_tokens: 8515
  total_tokens: 202279
  api_list_cost_usd: 0.1431
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

# DSS_analyzer_Mariner

Source: [shenyaojin/DSS_analyzer_Mariner](https://github.com/shenyaojin/DSS_analyzer_Mariner)

## Summary

DSS_analyzer_Mariner is a Python library for processing Distributed Strain Sensing (DSS) and fiber-optic sensing (FOS) data collected for the Bakken Mariner project, alongside associated engineering datasets such as pumping curves and gauge measurements. It provides modules for reading, organizing, and plotting 1D, 2D, and 3D fiber sensing data, plus signal-processing and event-detection utilities. It would be used by researchers analyzing hydraulic-fracturing or well-monitoring fiber data tied to this specific field project, rather than by general DAS practitioners, since it is explicitly adapted from a more general internal library ("JIN's pylib") to match the Mariner dataset's structure. Unlike a generic DAS toolkit, its scope is narrow and project-specific, with ad hoc readers for several file formats described as temporary until a unified format is finalized. The repository is archived (read-only) as of 2025-05-27, with the author stating the code will be reconstructed into a separate library.

## Details

- **Interface:** library (importable Python package; no CLI or GUI mentioned)
- **Data formats:** CSV (gauge data), HDF5/.h5 (DSS/RFS data), Excel .xlsx (event data), NPZ (DSS data) — per `datareader.py` reader functions; NPZ is noted as the intended eventual standard
- **Key dependencies:** numpy, pandas, openpyxl (for Excel reading); other dependencies not stated
- **Scope signals:** archived/read-only repository, 53 commits, 3 stars, 0 forks, 1 watcher; author states the code will be "reconstructed and combined" into a separate "PDS lib" project — indicates a small, project-specific, superseded codebase rather than an actively maintained general tool
- **Source visible:** yes — source files present, including `datareader.py`, `Data1D_GAUGE.py`, `Data1D_PumpingCurve.py`, `Data2D_XT_DSS.py`, `Data2D_PFSnapshot.py`, `Data3D_geometry.py`, `gjsignal.py`, `plot_utils.py`, `event_analysis_tools.py`
- **Sources read:**
  - https://github.com/shenyaojin/DSS_analyzer_Mariner
  - https://raw.githubusercontent.com/shenyaojin/DSS_analyzer_Mariner/main/README.md
  - https://github.com/shenyaojin/DSS_analyzer_Mariner/blob/main/datareader.py
