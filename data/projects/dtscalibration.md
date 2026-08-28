---
curated:
  id: dtscalibration
  name: python-dts-calibration
  repository: dtscalibration/python-dts-calibration
  repository_url: https://github.com/dtscalibration/python-dts-calibration
  homepage: https://python-dts-calibration.readthedocs.io
  description: Loading and calibration of raw distributed temperature sensing measurements.
  status: watchlist
  decision_reason: Mature, OSI-licensed DFOS package, but distributed temperature sensing is a different
    modality from DAS and is held out of the headline comparison.
  primary_category: processing
  capabilities:
  - calibration
  - io
  - processing
  - temperature-sensing
  license_spdx: BSD-3-Clause
  license_class: osi-approved
  forge:
    kind: github
    host: github.com
  registries:
    pypi:
    - dtscalibration
    conda:
    - conda-forge/dtscalibration
    julia: []
  publications: []
collected:
  scanned_at: '2026-08-28T12:56:24+00:00'
  snapshot: '2026-08-28'
  visibility: public
  language: Python
  stars: 43
  forks: 22
  contributors: 5
  releases: 32
  commits: 1002
  last_commit_at: '2026-05-06T10:40:38Z'
  created_at: '2018-07-31T22:46:08Z'
  latest_release_at: '2024-09-13T13:30:15Z'
  archived: false
  lines_of_code_estimate: 16588
  loc_basis: language bytes / 32, notebooks excluded
  pypi_downloads_180d: 2226
  pypi_downloads_30d: 219
  conda_downloads_total: 985
  dependencies:
  - package: dtscalibration
    dependency: dask
    requirement: ''
    marker: ''
    dependency_project: null
  - package: dtscalibration
    dependency: matplotlib
    requirement: ''
    marker: ''
    dependency_project: null
  - package: dtscalibration
    dependency: nc-time-axis
    requirement: '>=1.4.1'
    marker: ''
    dependency_project: null
  - package: dtscalibration
    dependency: netcdf4
    requirement: '>=1.6.4'
    marker: ''
    dependency_project: null
  - package: dtscalibration
    dependency: numpy
    requirement: ''
    marker: ''
    dependency_project: null
  - package: dtscalibration
    dependency: pandas
    requirement: ''
    marker: ''
    dependency_project: null
  - package: dtscalibration
    dependency: pyyaml
    requirement: '>=6.0.1'
    marker: ''
    dependency_project: null
  - package: dtscalibration
    dependency: scipy
    requirement: ''
    marker: ''
    dependency_project: null
  - package: dtscalibration
    dependency: xarray
    requirement: ''
    marker: ''
    dependency_project: null
  - package: dtscalibration
    dependency: xmltodict
    requirement: ''
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
  ran_at: 2026-08-20 08:13:36+00:00
  duration_seconds: 24.7
  turns: 4
  input_tokens: 10375
  output_tokens: 1810
  cache_read_tokens: 147092
  cache_write_tokens: 3337
  total_tokens: 162614
  api_list_cost_usd: 0.0958
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

# python-dts-calibration

Source: [dtscalibration/python-dts-calibration](https://github.com/dtscalibration/python-dts-calibration)

## Summary

python-dts-calibration is a Python library for calibrating raw Distributed Temperature Sensing (DTS) measurements from fiber-optic cables into temperature readings with quantified uncertainty. It implements a weighted least-squares calibration procedure (described in des Tombe et al., 2020) that improves on the basic calibration manufacturers provide, supporting single- and double-ended fiber configurations, step-loss correction at connectors, and J-configuration section matching. It reads raw instrument output files directly from several commercial DTS interrogators (Silixa, Sensornet, AP Sensing, SensorTran) rather than requiring users to pre-parse them. The intended users are researchers and practitioners in hydrology, geophysics, and environmental monitoring who use fiber-optic sensing for temperature measurement and need a rigorous, citable calibration method rather than vendor-provided defaults.

## Details

- **Interface:** Python library, with Jupyter notebook usage examples
- **Data formats:** Silixa Ultima/XT-DTS (.xml), Sensornet Oryx/Halo/Sentinel (.ddf), AP Sensing N4386B (.xml), SensorTran 5100 (.dat, binary)
- **Key dependencies:** numpy, xarray, dask, pandas, scipy, matplotlib, xmltodict, netCDF4, pyyaml
- **Scope signals:** ~43 stars, 22 forks, 1,002 commits, 22 open issues; BSD-3-Clause license; has a Zenodo DOI for citation; documented via ReadTheDocs; test coverage via GitHub Actions CI; requires Python 3.12+; distributed via PyPI and conda-forge — indicates a small but active, academically-grounded research tool rather than a large-scale product
- **Source visible:** yes, full source code is published in the repository
- **Sources read:** https://github.com/dtscalibration/python-dts-calibration, https://raw.githubusercontent.com/dtscalibration/python-dts-calibration/master/pyproject.toml
