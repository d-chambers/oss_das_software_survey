---
curated:
  id: dasvader
  name: DASVader.jl
  repository: marianoarnaiz/DASvader.jl
  repository_url: https://github.com/marianoarnaiz/DASvader.jl
  homepage: null
  description: Julia framework for loading, processing, and analyzing DAS data.
  status: included
  decision_reason: Reusable DAS-specific Julia library with an MIT license.
  primary_category: core-framework
  capabilities:
  - io
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
    julia:
    - DASVader
  publications: []
collected:
  scanned_at: '2026-08-28T12:56:10+00:00'
  snapshot: '2026-08-28'
  visibility: public
  language: Julia
  stars: 7
  forks: 1
  contributors: 1
  releases: 0
  commits: 90
  last_commit_at: '2026-07-03T19:57:36Z'
  created_at: '2024-12-02T15:08:03Z'
  archived: false
  lines_of_code_estimate: 5016
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
  ran_at: 2026-08-20 08:11:57+00:00
  duration_seconds: 18.4
  turns: 3
  input_tokens: 6803
  output_tokens: 1301
  cache_read_tokens: 104848
  cache_write_tokens: 7507
  total_tokens: 120459
  api_list_cost_usd: 0.0984
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

# DASVader.jl

Source: [marianoarnaiz/DASvader.jl](https://github.com/marianoarnaiz/DASvader.jl)

## Summary

DASVader.jl is a Julia package for reading, processing, and visualizing Distributed Acoustic Sensing (DAS) data, aimed at seismologists and researchers who need to work efficiently with large DAS datasets. It provides functions such as `rdas()` for loading FEBUS A1 format HDF5 files and `viewdas()` for interactive, dynamic visualization, positioning itself as an alternative to traditional seismic tools like SAC or PQL but tailored to DAS workflows. It supports signal processing in both frequency and wavelength domains and is built on top of established Julia seismology and signal-processing packages rather than reimplementing that functionality. What distinguishes it from a generic plotting or data-loading toolkit is its focus on interactive, dynamic visualization of large DAS records, rather than static plots alone.

## Details

- **Interface:** library (Julia package)
- **Data formats:** reads FEBUS A1 DAS HDF5 files; exports visualizations as PDF
- **Key dependencies:** Seis.jl, FFTW.jl, FourierAnalysis.jl, InteractiveViz.jl (customized fork), Geodesics.jl
- **Scope signals:** small, early-stage project — 7 stars, unregistered Julia package requiring manual installation, no releases, 0 open issues/PRs, README describes documentation as "coming soon"; 90 commits on main indicate ongoing development
- **Source visible:** yes — repository contains populated `/src`, `/Examples`, and `/Documents` directories, not just a description
- **Sources read:** https://github.com/marianoarnaiz/DASvader.jl
