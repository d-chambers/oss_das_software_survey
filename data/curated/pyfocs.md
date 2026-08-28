---
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
das_focus: other-fiber
sources:
- github.com/klapo/pyfocs
reviewed_at: '2026-08-28'
provenance:
  agent: das-summarizer
  models:
  - claude-haiku-4-5-20251001
  - claude-sonnet-5
  ran_at: '2026-08-20T08:16:16+00:00'
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

## Summary

pyfocs is a Python library for processing Fiber Optic Distributed Sensing (FODS) data from long-term, large-scale deployments, built around calibration and coordinate-mapping workflows for Distributed Temperature Sensing (DTS) instruments. It converts raw Silixa DTS `.xml` output into physically labeled, calibrated netCDF datasets, using the `dtscalibration` package for the calibration step and `xarray` for handling the resulting length-along-fiber and time-indexed data. It also supports deriving wind speed estimates from FODS measurements and includes statistical/diagnostic routines for assessing data quality. The intended users are researchers running environmental sensing campaigns with fiber-optic DTS hardware who need a repeatable pipeline from raw instrument files to analysis-ready data, rather than a generic signal-processing toolkit.

## Details

- **Interface:** library, with an accompanying command-line automation script (`PyFOX.py`) and example Jupyter notebooks for data exploration/validation
- **Data formats:** input is Silixa DTS `.xml` files; output is netCDF, structured for xarray, indexed by Length Along Fiber (LAF) and time
- **Key dependencies:** `dtscalibration`, `xarray`
- **Scope signals:** version 0.5.1 (mid-stage development), 23 stars, 12 forks, 7 open issues, 506 commits on main; GPL-3.0 licensed; documentation consists of three example notebooks covering raw data assessment, calibration validation, and final data checks
- **Source visible:** yes — repository includes library source, the automation script, tests, and notebooks
- **Sources read:** https://github.com/klapo/pyfocs
