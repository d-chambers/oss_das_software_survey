---
curated:
  id: pyfocs
  name: pyfocs
  repository: klapo/pyfocs
  repository_url: https://github.com/klapo/pyfocs
  homepage: null
  description: Processing pipeline for fiber-optic distributed sensing temperature data.
  status: watchlist
  decision_reason: OSI-licensed DFOS package, but the modality is distributed temperature sensing rather
    than DAS.
  primary_category: processing
  capabilities:
  - calibration
  - io
  - processing
  - temperature-sensing
  license_spdx: GPL-3.0-only
  license_class: osi-approved
  forge:
    kind: github
    host: github.com
  registries:
    pypi:
    - pyfocs
    conda: []
    julia: []
  publications: []
collected:
  scanned_at: '2026-08-28T12:57:09+00:00'
  snapshot: '2026-08-28'
  visibility: public
  language: HTML
  stars: 23
  forks: 12
  contributors: 3
  releases: 1
  commits: 506
  last_commit_at: '2023-05-09T15:50:10Z'
  created_at: '2018-09-20T09:06:38Z'
  latest_release_at: '2020-11-26T17:40:46Z'
  archived: false
  lines_of_code_estimate: 62529
  loc_basis: language bytes / 32, notebooks excluded
  pypi_downloads_180d: 274
  pypi_downloads_30d: 32
  dependencies:
  - package: pyfocs
    dependency: dtscalibration
    requirement: ''
    marker: ''
    dependency_project: dtscalibration
  - package: pyfocs
    dependency: matplotlib
    requirement: '>3'
    marker: ''
    dependency_project: null
  - package: pyfocs
    dependency: netcdf4
    requirement: ''
    marker: ''
    dependency_project: null
  - package: pyfocs
    dependency: numpy
    requirement: ''
    marker: ''
    dependency_project: null
  - package: pyfocs
    dependency: pandas
    requirement: ''
    marker: ''
    dependency_project: null
  - package: pyfocs
    dependency: pyyaml
    requirement: '>=5.1'
    marker: ''
    dependency_project: null
  - package: pyfocs
    dependency: scipy
    requirement: ''
    marker: ''
    dependency_project: null
  - package: pyfocs
    dependency: xarray
    requirement: '>=0.15'
    marker: ''
    dependency_project: null
  - package: pyfocs
    dependency: xmltodict
    requirement: ''
    marker: ''
    dependency_project: null
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
  ran_at: 2026-08-20 08:16:16+00:00
  duration_seconds: 18.7
  turns: 3
  input_tokens: 7014
  output_tokens: 1392
  cache_read_tokens: 104832
  cache_write_tokens: 7430
  total_tokens: 120668
  api_list_cost_usd: 0.0998
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

# pyfocs

Source: [klapo/pyfocs](https://github.com/klapo/pyfocs)

## Summary

pyfocs is a Python library for processing Fiber Optic Distributed Sensing (FODS) data from long-term, large-scale deployments, built around calibration and coordinate-mapping workflows for Distributed Temperature Sensing (DTS) instruments. It converts raw Silixa DTS `.xml` output into physically labeled, calibrated netCDF datasets, using the `dtscalibration` package for the calibration step and `xarray` for handling the resulting length-along-fiber and time-indexed data. It also supports deriving wind speed estimates from FODS measurements and includes statistical/diagnostic routines for assessing data quality. The intended users are researchers running environmental sensing campaigns with fiber-optic DTS hardware who need a repeatable pipeline from raw instrument files to analysis-ready data, rather than a generic signal-processing toolkit.

## Details

- **Interface:** library, with an accompanying command-line automation script (`PyFOX.py`) and example Jupyter notebooks for data exploration/validation
- **Data formats:** input is Silixa DTS `.xml` files; output is netCDF, structured for xarray, indexed by Length Along Fiber (LAF) and time
- **Key dependencies:** `dtscalibration`, `xarray`
- **Scope signals:** version 0.5.1 (mid-stage development), 23 stars, 12 forks, 7 open issues, 506 commits on main; GPL-3.0 licensed; documentation consists of three example notebooks covering raw data assessment, calibration validation, and final data checks
- **Source visible:** yes — repository includes library source, the automation script, tests, and notebooks
- **Sources read:** https://github.com/klapo/pyfocs
