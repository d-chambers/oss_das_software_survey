---
curated:
  id: daspy
  name: DASPy
  repository: HMZ-03/DASPy
  repository_url: https://github.com/HMZ-03/DASPy
  homepage: https://daspy-tutorial.readthedocs.io
  description: Python toolbox for DAS seismology and common array-processing workflows.
  status: included
  decision_reason: Reusable DAS-specific toolbox with an MIT license, documentation, and package releases.
  primary_category: processing
  capabilities:
  - io
  - processing
  - seismology
  - visualization
  license_spdx: MIT
  license_class: osi-approved
  forge:
    kind: github
    host: github.com
  registries:
    pypi:
    - daspy-toolbox
    conda:
    - conda-forge/daspy-toolbox
    julia: []
  publications:
  - doi: 10.1785/0220240124
    role: canonical
    note: null
collected:
  scanned_at: '2026-08-18T06:37:56+00:00'
  snapshot: '2026-08-17'
  visibility: public
  language: Jupyter Notebook
  stars: 154
  forks: 29
  contributors: 3
  releases: 10
  commits: 457
  last_commit_at: '2026-06-26T01:34:37Z'
  created_at: '2024-03-27T10:47:41Z'
  latest_release_at: '2026-06-26T01:36:36Z'
  archived: false
  lines_of_code_estimate: 9319
  loc_basis: language bytes / 32, notebooks excluded
  pypi_downloads_180d: 2545
  pypi_downloads_30d: 458
  conda_downloads_total: 6926
  canonical_citations: 19
  dependencies:
  - package: DASPy-toolbox
    dependency: geographiclib
    requirement: ''
    marker: ''
    dependency_project: null
  - package: DASPy-toolbox
    dependency: h5py
    requirement: ''
    marker: ''
    dependency_project: null
  - package: DASPy-toolbox
    dependency: matplotlib
    requirement: ''
    marker: ''
    dependency_project: null
  - package: DASPy-toolbox
    dependency: nptdms
    requirement: ''
    marker: ''
    dependency_project: null
  - package: DASPy-toolbox
    dependency: numpy
    requirement: ''
    marker: ''
    dependency_project: null
  - package: DASPy-toolbox
    dependency: pyproj
    requirement: ''
    marker: ''
    dependency_project: null
  - package: DASPy-toolbox
    dependency: scipy
    requirement: '>=1.13'
    marker: ''
    dependency_project: null
  - package: DASPy-toolbox
    dependency: segyio
    requirement: ''
    marker: ''
    dependency_project: null
  - package: DASPy-toolbox
    dependency: tqdm
    requirement: ''
    marker: ''
    dependency_project: null
  has_docs: false
  has_tests: false
  has_ci: true
  unavailable:
    pypi_downloads_total: no free source publishes all-time PyPI totals
    conda_downloads_180d: anaconda.org publishes a cumulative count only, with no time series
summary:
  agent: das-summarizer
  models:
  - claude-haiku-4-5-20251001
  - claude-sonnet-5
  ran_at: 2026-08-20 08:11:34+00:00
  duration_seconds: 26.8
  turns: 4
  input_tokens: 8679
  output_tokens: 1860
  cache_read_tokens: 143132
  cache_write_tokens: 8134
  total_tokens: 161805
  api_list_cost_usd: 0.1214
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

# DASPy

Source: [HMZ-03/DASPy](https://github.com/HMZ-03/DASPy)

## Summary

DASPy is a Python library for processing Distributed Acoustic Sensing (DAS) data, which uses fiber optic cables as distributed seismic sensors. It combines standard seismic-processing operations (filtering, spectral analysis, visualization) with DAS-specific algorithms such as denoising, wavefield decomposition, and strain-to-velocity conversion, exposed through purpose-built data structures (`Section`, `Collection`, `DASDateTime`) rather than generic arrays. It targets DAS seismology researchers and practitioners who need domain-specific I/O and processing beyond what general seismology toolkits (e.g., ObsPy) provide out of the box. The project states its goal is to "lower the barrier for DAS processing" and support the growing field of DAS seismology; it is referenced in a peer-reviewed seismology journal publication (2024) and is distributed via PyPI and Conda-Forge, with tutorials in both English and Chinese.

## Details

- **Interface:** library (Python package, programmatic API; no CLI or GUI mentioned)
- **Data formats:** reads SEGY, HDF5, and TDMS files; documentation also mentions converting from other packages' formats
- **Key dependencies:** NumPy, SciPy, Matplotlib, h5py, segyio, nptdms
- **Scope signals:** 154 stars, 29 forks, 457 commits on main, MIT license, requires Python 3.9+, published via PyPI and Conda-Forge, cited in a 2024 peer-reviewed seismology journal — indicates an actively maintained, academically credible research tool rather than experimental or unmaintained code
- **Source visible:** yes — repository contains a `/daspy/` package directory, a `/document/` directory with tutorials/examples, and standard packaging files (`pyproject.toml`, `setup.py`)
- **Sources read:** https://github.com/HMZ-03/DASPy, https://daspy-tutorial.readthedocs.io
