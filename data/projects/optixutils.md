---
curated:
  id: optixutils
  name: OptixUtils
  repository: uqzzhao/OptixUtils
  repository_url: https://github.com/uqzzhao/OptixUtils
  homepage: null
  description: Reading, writing, and plotting utilities for Optix DAS data backed by PyTables.
  status: included
  decision_reason: Reusable DAS-specific utility library explicitly licensed under LGPL-2.1.
  primary_category: data-management
  capabilities:
  - data-management
  - io
  - visualization
  license_spdx: LGPL-2.1-only
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
  scanned_at: '2026-08-28T12:57:05+00:00'
  snapshot: '2026-08-28'
  visibility: public
  language: Python
  stars: 1
  forks: 0
  contributors: 1
  releases: 0
  commits: 2
  last_commit_at: '2026-01-18T10:43:57Z'
  created_at: '2026-01-18T09:40:58Z'
  archived: false
  lines_of_code_estimate: 2173
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
  ran_at: 2026-08-20 08:16:58+00:00
  duration_seconds: 40.3
  turns: 6
  input_tokens: 23825
  output_tokens: 2738
  cache_read_tokens: 227374
  cache_write_tokens: 2433
  total_tokens: 256370
  api_list_cost_usd: 0.1372
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

# OptixUtils

Source: [uqzzhao/OptixUtils](https://github.com/uqzzhao/OptixUtils)

## Summary

OptixUtils is a small Python library for reading, writing, and visualizing distributed acoustic sensing (DAS) data produced by OptaSoft's Optix interrogator software. Its core is a `DasDataset` class that loads OSA files (OptaSoft's proprietary dictionary-based format), handles Raw/Accumulated/Differential data types, generates timestamp and length arrays from acquisition parameters, and exports data to NPZ, MATLAB (.mat), and CSV formats. It also includes a `TimeStamps` helper for building time arrays and matplotlib-based 2D waterfall plotting with zone/marker annotation. This targets researchers or engineers who operate Optix-brand DAS interrogators and need to convert vendor-specific OSA files into common formats for downstream analysis, rather than users of generic or open DAS file standards like HDF5-based TDMS/DASDAE conventions.

## Details

- **Interface:** library (Python module; no CLI or GUI described)
- **Data formats:** reads OSA files (OptaSoft/Optix proprietary format); writes OSA, NPZ, MAT (MATLAB), and CSV
- **Key dependencies:** NumPy, Pandas, SciPy (`scipy.io` for MATLAB I/O), Matplotlib; README also references PyTables for an HDF5-based `DasDataset` implementation, though the source file actually read (`dxs/das/dastables.py`) does not import PyTables
- **Scope signals:** very small, early-stage project — 2 commits, 1 star, 0 forks/watchers, no releases, no issues or pull requests; single author (Zhengguang Zhao); appears written for internal/personal use with a specific vendor's hardware
- **Source visible:** yes, source code is published (`dxs/das/dastables.py`, plus `data/`, `scripts/`, and `utils/` directories)
- **Sources read:** https://github.com/uqzzhao/OptixUtils, https://github.com/uqzzhao/OptixUtils/tree/master, https://github.com/uqzzhao/OptixUtils/tree/master/dxs/das, https://raw.githubusercontent.com/uqzzhao/OptixUtils/master/dxs/das/dastables.py

Note: the README describes the `DasDataset` class as PyTables-based, but the actual source file I read imports SciPy/NumPy/Pandas/Matplotlib and shows no PyTables usage — flagging this discrepancy rather than guessing which is authoritative.
