---
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
das_focus: other-fiber
sources:
- github.com/dtscalibration/python-dts-calibration
reviewed_at: '2026-08-28'
provenance:
  agent: das-summarizer
  models:
  - claude-haiku-4-5-20251001
  - claude-sonnet-5
  ran_at: '2026-08-20T08:13:36+00:00'
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

## Summary

python-dts-calibration is a Python library for calibrating raw Distributed Temperature Sensing (DTS) measurements from fiber-optic cables into temperature readings with quantified uncertainty. It implements a weighted least-squares calibration procedure (described in des Tombe et al., 2020) that improves on the basic calibration manufacturers provide, supporting single- and double-ended fiber configurations, step-loss correction at connectors, and J-configuration section matching. It reads raw instrument output files directly from several commercial DTS interrogators (Silixa, Sensornet, AP Sensing, SensorTran) rather than requiring users to pre-parse them. The intended users are researchers and practitioners in hydrology, geophysics, and environmental monitoring who use fiber-optic sensing for temperature measurement and need a rigorous, citable calibration method rather than vendor-provided defaults.

## Details

- **Interface:** Python library, with Jupyter notebook usage examples
- **Data formats:** Silixa Ultima/XT-DTS (.xml), Sensornet Oryx/Halo/Sentinel (.ddf), AP Sensing N4386B (.xml), SensorTran 5100 (.dat, binary)
- **Key dependencies:** numpy, xarray, dask, pandas, scipy, matplotlib, xmltodict, netCDF4, pyyaml
- **Scope signals:** ~43 stars, 22 forks, 1,002 commits, 22 open issues; BSD-3-Clause license; has a Zenodo DOI for citation; documented via ReadTheDocs; test coverage via GitHub Actions CI; requires Python 3.12+; distributed via PyPI and conda-forge — indicates a small but active, academically-grounded research tool rather than a large-scale product
- **Source visible:** yes, full source code is published in the repository
- **Sources read:** https://github.com/dtscalibration/python-dts-calibration, https://raw.githubusercontent.com/dtscalibration/python-dts-calibration/master/pyproject.toml
