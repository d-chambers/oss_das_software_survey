---
curated:
  id: dastools
  name: dastools
  repository: geofon/dastools
  repository_url: https://git.gfz-potsdam.de/geofon/dastools
  homepage: null
  description: Reading, conversion, and metadata tooling for DAS acquisitions, from GEOFON.
  status: included
  decision_reason: Reusable DAS tool set with GPL-3.0-or-later licensing and PyPI releases; the first
    catalogued project hosted outside GitHub.
  primary_category: data-management
  capabilities:
  - conversion
  - data-management
  - io
  - metadata
  license_spdx: GPL-3.0-or-later
  license_class: osi-approved
  forge:
    kind: gitlab
    host: git.gfz-potsdam.de
  registries:
    pypi:
    - dastools
    conda: []
    julia: []
  publications: []
collected:
  scanned_at: '2026-08-28T12:56:08+00:00'
  snapshot: '2026-08-28'
  visibility: public
  language: Python
  stars: 2
  forks: 0
  contributors: 1
  releases: 15
  last_commit_at: '2025-12-27T10:12:07.000+01:00'
  created_at: '2019-06-17T01:05:32.741+02:00'
  latest_release_at: '2025-08-26T20:53:40.164+02:00'
  archived: false
  pypi_downloads_180d: 486
  pypi_downloads_30d: 42
  dependencies:
  - package: dastools
    dependency: click
    requirement: ''
    marker: ''
    dependency_project: null
  - package: dastools
    dependency: fastapi
    requirement: ''
    marker: ''
    dependency_project: null
  - package: dastools
    dependency: h5py
    requirement: ''
    marker: ''
    dependency_project: null
  - package: dastools
    dependency: httpx
    requirement: ''
    marker: ''
    dependency_project: null
  - package: dastools
    dependency: jinja2
    requirement: ''
    marker: ''
    dependency_project: null
  - package: dastools
    dependency: jsonschema
    requirement: ''
    marker: ''
    dependency_project: null
  - package: dastools
    dependency: numpy
    requirement: ''
    marker: ''
    dependency_project: null
  - package: dastools
    dependency: obspy
    requirement: ''
    marker: ''
    dependency_project: null
  - package: dastools
    dependency: pydantic
    requirement: '>=2'
    marker: ''
    dependency_project: null
  - package: dastools
    dependency: pytest-cov
    requirement: ''
    marker: ''
    dependency_project: null
  - package: dastools
    dependency: scipy
    requirement: ''
    marker: ''
    dependency_project: null
  - package: dastools
    dependency: sphinx
    requirement: ''
    marker: ''
    dependency_project: null
  - package: dastools
    dependency: tqdm
    requirement: ''
    marker: ''
    dependency_project: null
  - package: dastools
    dependency: uvicorn
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
  ran_at: 2026-08-20 08:11:57+00:00
  duration_seconds: 54.4
  turns: 11
  input_tokens: 9179
  output_tokens: 4412
  cache_read_tokens: 301169
  cache_write_tokens: 11106
  total_tokens: 325866
  api_list_cost_usd: 0.2165
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

# dastools

Source: [geofon/dastools](https://git.gfz-potsdam.de/geofon/dastools)

## Summary

dastools is a Python package for reading, manipulating, and converting seismic waveforms produced by distributed acoustic sensing (DAS) interrogator systems. It targets researchers and engineers who need to move raw DAS output into formats usable by standard seismology workflows: it reads Silixa's TDMS format and OptoDAS/Alcatel's HDF5 format, and converts them to miniSEED, the standard format used across the seismological community and FDSN data centers. Unlike a generic file-conversion utility, it also ships an FDSN-compatible Dataselect web service (`dasws`), letting converted DAS data be served over the same protocol seismologists already use to query conventional seismic networks. It is maintained by GFZ Potsdam's GEOFON program, tying it directly into an operational seismic-data infrastructure rather than being a standalone research script.

## Details

- **Interface:** CLI (three console scripts: `dasconv`, `dasmetadata`, `dasws`) plus a Python library (e.g. a `TDMS` class for use in custom scripts); `dasws` also runs as a FastAPI-based web service
- **Data formats:** reads TDMS (Silixa) and HDF5 (OptoDAS/Alcatel); writes miniSEED
- **Key dependencies:** obspy, numpy, scipy, h5py, fastapi, uvicorn, pydantic, click, jinja2, sphinx, jsonschema, httpx, tqdm
- **Scope signals:** classified "Production/Stable" in setup.py, supports Python 3.9–3.12, GPLv3+ licensed, 842 commits and 15 releases since June 2019; README notes some features are incomplete (`dasmetadata` "needs to be done", `dasws` QueryAuth "NOT implemented yet")
- **Source visible:** yes — full package source visible (`dastools/app`, `dastools/core.py`, `dastools/server`, `dastools/input`, `dastools/output`, `dastools/partition`, tests, etc.), not just a description
- **Sources read:** https://git.gfz-potsdam.de/geofon/dastools, https://git.gfz-potsdam.de/api/v4/projects/geofon%2Fdastools, https://git.gfz-potsdam.de/geofon/dastools/-/raw/master/README.rst, https://git.gfz-potsdam.de/geofon/dastools/-/raw/master/setup.py, https://git.gfz-potsdam.de/api/v4/projects/geofon%2Fdastools/repository/tree?path=dastools&ref=master
