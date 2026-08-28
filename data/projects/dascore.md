---
curated:
  id: dascore
  name: DASCore
  repository: DASDAE/dascore
  repository_url: https://github.com/DASDAE/dascore
  homepage: https://dascore.org
  description: General data model, I/O, processing, and visualization for distributed fiber sensing.
  status: included
  decision_reason: Reusable DAS-specific library with documented LGPL-3.0-or-later licensing and package
    releases.
  primary_category: core-framework
  capabilities:
  - data-management
  - data-model
  - io
  - processing
  - visualization
  license_spdx: LGPL-3.0-or-later
  license_class: osi-approved
  forge:
    kind: github
    host: github.com
  registries:
    pypi:
    - dascore
    conda:
    - conda-forge/dascore
    julia: []
  publications:
  - doi: 10.26443/seismica.v3i2.1184
    role: canonical
    note: null
collected:
  scanned_at: '2026-08-18T06:37:32+00:00'
  snapshot: '2026-08-17'
  visibility: public
  language: Python
  stars: 159
  forks: 41
  contributors: 18
  releases: 34
  commits: 526
  last_commit_at: '2026-08-08T11:21:33Z'
  created_at: '2021-10-29T15:34:47Z'
  latest_release_at: '2026-07-25T10:46:45Z'
  archived: false
  lines_of_code_estimate: 71844
  loc_basis: language bytes / 32, notebooks excluded
  pypi_downloads_180d: 15268
  pypi_downloads_30d: 7219
  conda_downloads_total: 48060
  canonical_citations: 17
  dependencies:
  - package: dascore
    dependency: h5py
    requirement: ''
    marker: ''
    dependency_project: null
  - package: dascore
    dependency: matplotlib
    requirement: '>=3.10'
    marker: ''
    dependency_project: null
  - package: dascore
    dependency: numpy
    requirement: '>=1.24'
    marker: ''
    dependency_project: null
  - package: dascore
    dependency: packaging
    requirement: ''
    marker: ''
    dependency_project: null
  - package: dascore
    dependency: pandas
    requirement: '>=2.0'
    marker: ''
    dependency_project: null
  - package: dascore
    dependency: pint
    requirement: ''
    marker: ''
    dependency_project: null
  - package: dascore
    dependency: pooch
    requirement: '>=1.2'
    marker: ''
    dependency_project: null
  - package: dascore
    dependency: pydantic
    requirement: '>2.1'
    marker: ''
    dependency_project: null
  - package: dascore
    dependency: rich
    requirement: ''
    marker: ''
    dependency_project: null
  - package: dascore
    dependency: scipy
    requirement: '>=1.15'
    marker: ''
    dependency_project: null
  - package: dascore
    dependency: tables
    requirement: '>=3.7'
    marker: ''
    dependency_project: null
  - package: dascore
    dependency: typing-extensions
    requirement: '>=4.12'
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
  ran_at: 2026-08-20 08:11:02+00:00
  duration_seconds: 49.0
  turns: 9
  input_tokens: 14785
  output_tokens: 3552
  cache_read_tokens: 307563
  cache_write_tokens: 4391
  total_tokens: 330291
  api_list_cost_usd: 0.1726
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

# DASCore

Source: [DASDAE/dascore](https://github.com/DASDAE/dascore)

## Summary

DASCore is a Python library for working with distributed acoustic sensing (DAS) data, a fiber-optic sensing technology used to record seismic and other ground-motion signals along a cable. It provides programmatic tools to read, write, and manipulate DAS data through a `Patch`/`Spool` data model, along with common processing routines (filtering, decimation, detrending) and basic visualization (e.g., waterfall plots). It targets researchers and engineers in geophysics and seismology who need to work with fiber-optic sensing datasets in Python rather than through a standalone application. What distinguishes it from a generic array-processing toolkit is its broad, purpose-built support for the many proprietary and vendor-specific DAS file formats produced by interrogator hardware, unifying them behind a consistent API. It is developed under the DAS Data Analysis Ecosystem (DASDAE) and was described in a peer-reviewed 2024 Seismica paper.

## Details

- **Interface:** library (Python; imported into scripts, e.g. `dc.spool()`, `patch.decimate()`, `patch.viz.waterfall()`)
- **Data formats:** reads APSENSING, DASDAE, DASHDF5, DASVADER, FEBUS (multiple variants incl. FEBUS_G1_CSV, FEBUS_MTX_H5, FEBUS_BSL_H5, FEBUS_T1), GDR_DAS, H5SIMPLE, NEUBREXRFS, NEUBREXDAS, OPTODAS (v8–11), PICKLE, PRODML (2, 2.1), SEGY (multiple versions), SENTEK, SILIXA_H5, SINTELA_BINARY, SR4731, TDMS, TERRA15 (v4–6), XMLBINARY; writes DASDAE (v1), SEGY (v0, 0.1, 1, 2, 2.1), RSF (v1), and WAV
- **Key dependencies:** numpy, pandas, scipy, matplotlib, h5py, pytables (`tables`), pydantic, pint, pooch, rich, packaging, typing_extensions; optional extras include xarray, obspy, numba, segyio, findiff, bottleneck
- **Scope signals:** ~159 GitHub stars, 41 forks, 526 commits, 41 contributors; PyPI/Conda-Forge distribution; listed as Development Status "4 - Beta"; supports Python 3.10–3.14; part of the DASDAE ecosystem; peer-reviewed publication in Seismica (2024)
- **Source visible:** yes, full source published on GitHub
- **Sources read:** https://github.com/DASDAE/dascore, https://dascore.org, https://dascore.org/supported_formats.html, https://raw.githubusercontent.com/DASDAE/dascore/master/pyproject.toml
