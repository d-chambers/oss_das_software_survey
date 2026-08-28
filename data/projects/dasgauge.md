---
curated:
  id: dasgauge
  name: dasgauge
  repository: UWGeoD/dasgauge
  repository_url: https://github.com/UWGeoD/dasgauge
  homepage: null
  description: Similarity measurement between two DAS datasets.
  status: included
  decision_reason: Reusable DAS-specific comparison package with an MIT license.
  primary_category: benchmarking
  capabilities:
  - benchmarking
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
  scanned_at: '2026-08-28T12:55:49+00:00'
  snapshot: '2026-08-28'
  visibility: public
  language: Python
  stars: 0
  forks: 0
  contributors: 1
  releases: 0
  commits: 7
  last_commit_at: '2026-08-22T06:23:00Z'
  created_at: '2026-07-31T04:49:00Z'
  archived: false
  lines_of_code_estimate: 6850
  loc_basis: language bytes / 32, notebooks excluded
  dependencies: []
  has_docs: false
  has_tests: true
  has_ci: false
  unavailable:
    pypi_downloads_total: no free source publishes all-time PyPI totals
    conda_downloads_180d: anaconda.org publishes a cumulative count only, with no time series
summary:
  agent: das-summarizer
  models:
  - claude-haiku-4-5-20251001
  - claude-sonnet-5
  ran_at: 2026-08-20 08:11:36+00:00
  duration_seconds: 20.3
  turns: 3
  input_tokens: 5580
  output_tokens: 1415
  cache_read_tokens: 110599
  cache_write_tokens: 1666
  total_tokens: 119260
  api_list_cost_usd: 0.066
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

# dasgauge

Source: [UWGeoD/dasgauge](https://github.com/UWGeoD/dasgauge)

## Summary

dasgauge is a small Python library for reading, preprocessing, and visualizing distributed acoustic sensing (DAS) data recorded from fiber-optic cables. It provides an I/O module that reads HDF5 files from OptaSense and Silixa interrogators (as well as a generic HDF5 path), a preprocessing module offering a composable pipeline of operations such as detrending, bandpass and f-k filtering, downsampling, integration, Hilbert transforms, and curvelet-based denoising, and a plotting module for heatmap and single-channel waveform displays. It is aimed at researchers who need to load raw DAS acquisitions and run standard signal-conditioning steps before analysis, rather than at building full processing pipelines or applications. Unlike a generic seismic or signal-processing toolkit, its scope is narrowly tied to DAS-specific file formats and channel/gauge-length conventions used by common interrogator vendors. The code is derived from an earlier UWGeoD/DAS_Preprocessing repository, with attribution documented in a PROVENANCE.md file.

## Details

- **Interface:** library (Python package, imported as `dasgauge`; no CLI or GUI)
- **Data formats:** HDF5 files from OptaSense and Silixa (DAS-RCN format), plus generic HDF5 sources
- **Key dependencies:** NumPy, SciPy, h5py (core); Matplotlib (optional, lazy-loaded for plotting)
- **Scope signals:** Very early-stage — 0 stars/forks/watchers, only 3 commits, no releases or published packages; code ported from a prior repository (UWGeoD/DAS_Preprocessing) rather than written fresh
- **Source visible:** Yes — the repository publishes actual source code (`dasgauge/`, `tests/`, `provenance/` directories), not just a description
- **Sources read:** https://github.com/UWGeoD/dasgauge
