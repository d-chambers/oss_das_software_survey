---
curated:
  id: das4whales
  name: DAS4Whales
  repository: DAS4Whales/DAS4Whales
  repository_url: https://github.com/DAS4Whales/DAS4Whales
  homepage: https://das4whales.readthedocs.io
  description: DAS processing and visualization for marine bioacoustics.
  status: included
  decision_reason: Reusable DAS library for marine bioacoustics. Its CC BY-NC-SA license is source-available
    rather than OSI-approved, which the license class records instead of the inclusion decision.
  primary_category: application-domain
  capabilities:
  - bioacoustics
  - detection
  - io
  - processing
  - visualization
  license_spdx: CC-BY-NC-SA-4.0
  license_class: source-available
  forge:
    kind: github
    host: github.com
  registries:
    pypi:
    - das4whales
    conda: []
    julia: []
  publications:
  - doi: 10.5281/zenodo.7760187
    role: canonical
    note: null
collected:
  scanned_at: '2026-08-18T06:37:30+00:00'
  snapshot: '2026-08-17'
  visibility: public
  language: Python
  stars: 79
  forks: 21
  contributors: 4
  releases: 4
  commits: 610
  last_commit_at: '2026-07-30T14:32:40Z'
  created_at: '2023-02-21T19:26:59Z'
  latest_release_at: '2026-07-06T14:57:16Z'
  archived: false
  lines_of_code_estimate: 14726
  loc_basis: language bytes / 32, notebooks excluded
  pypi_downloads_180d: 806
  pypi_downloads_30d: 74
  canonical_citations: 1
  dependencies:
  - package: das4whales
    dependency: cmocean
    requirement: ''
    marker: ''
    dependency_project: null
  - package: das4whales
    dependency: dask
    requirement: ''
    marker: ''
    dependency_project: null
  - package: das4whales
    dependency: datetime
    requirement: ''
    marker: ''
    dependency_project: null
  - package: das4whales
    dependency: deprecation
    requirement: ''
    marker: ''
    dependency_project: null
  - package: das4whales
    dependency: h5py
    requirement: ''
    marker: ''
    dependency_project: null
  - package: das4whales
    dependency: librosa
    requirement: ''
    marker: ''
    dependency_project: null
  - package: das4whales
    dependency: matplotlib
    requirement: ''
    marker: ''
    dependency_project: null
  - package: das4whales
    dependency: netcdf4
    requirement: ''
    marker: ''
    dependency_project: null
  - package: das4whales
    dependency: nptdms
    requirement: ''
    marker: ''
    dependency_project: null
  - package: das4whales
    dependency: numpy
    requirement: ''
    marker: ''
    dependency_project: null
  - package: das4whales
    dependency: numpydoc
    requirement: ''
    marker: ''
    dependency_project: null
  - package: das4whales
    dependency: opencv-python
    requirement: ''
    marker: ''
    dependency_project: null
  - package: das4whales
    dependency: pandas
    requirement: ''
    marker: ''
    dependency_project: null
  - package: das4whales
    dependency: pyproj
    requirement: ''
    marker: ''
    dependency_project: null
  - package: das4whales
    dependency: pytest
    requirement: ''
    marker: ''
    dependency_project: null
  - package: das4whales
    dependency: scikit-image
    requirement: ''
    marker: ''
    dependency_project: null
  - package: das4whales
    dependency: scipy
    requirement: ''
    marker: ''
    dependency_project: null
  - package: das4whales
    dependency: sparse
    requirement: ''
    marker: ''
    dependency_project: null
  - package: das4whales
    dependency: tqdm
    requirement: ''
    marker: ''
    dependency_project: null
  - package: das4whales
    dependency: wget
    requirement: ''
    marker: ''
    dependency_project: null
  - package: das4whales
    dependency: xarray
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
  ran_at: 2026-08-20 08:11:02+00:00
  duration_seconds: 33.0
  turns: 5
  input_tokens: 11120
  output_tokens: 2325
  cache_read_tokens: 187990
  cache_write_tokens: 2940
  total_tokens: 204375
  api_list_cost_usd: 0.1109
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

# DAS4Whales

Source: [DAS4Whales/DAS4Whales](https://github.com/DAS4Whales/DAS4Whales)

## Summary

DAS4Whales is a Python library for processing and analyzing Distributed Acoustic Sensing (DAS) data in marine bioacoustics research, specifically for detecting and studying whale vocalizations recorded on fiber-optic cable arrays. It provides functions to load DAS strain data and metadata from HDF5 files, apply signal-processing filters (high-pass, band-pass, and frequency-wavenumber filtering), generate spatio-temporal and spatio-spectral visualizations and spectrograms, and play back single-channel audio extracted from a channel. It is aimed at marine bioacousticians and oceanographers working with OptaSense-style DAS interrogator data rather than general signal-processing users, and is distributed with example Jupyter notebooks runnable in Google Colab. The documentation describes it as the authors' "first Python package," indicating an early-stage, research-driven tool rather than a mature, general-purpose framework.

## Details

- **Interface:** library (Python package), with example Jupyter notebooks
- **Data formats:** reads DAS strain data and metadata from HDF5 files (example dataset from an OptaSense interrogator)
- **Key dependencies:** h5py, numpy, scipy, matplotlib, dask, xarray, librosa, pandas, pyproj, scikit-image, opencv-python, nptdms; optional torch/torchvision for image processing
- **Scope signals:** 79 stars, 21 forks, 619 commits; authors from Cornell Lab of Ornithology and University of Washington; docs describe it as the team's "first Python package" and invite community contributions/bug reports; Creative Commons BY-NC-SA 4.0 license; has a Zenodo citation DOI and GitHub Actions CI
- **Source visible:** yes, full source code is published in the repository
- **Sources read:** https://github.com/DAS4Whales/DAS4Whales, https://das4whales.readthedocs.io, https://raw.githubusercontent.com/DAS4Whales/DAS4Whales/main/pyproject.toml
