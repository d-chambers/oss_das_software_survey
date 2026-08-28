---
curated:
  id: dasstore
  name: DASstore
  repository: niyiyu/DASstore
  repository_url: https://github.com/niyiyu/DASstore
  homepage: null
  description: Object-storage and data-access tools designed for DAS datasets.
  status: included
  decision_reason: Reusable DAS storage software with GPL-3.0 licensing.
  primary_category: compression-storage
  capabilities:
  - data-management
  - io
  - object-storage
  license_spdx: GPL-3.0-only
  license_class: osi-approved
  forge:
    kind: github
    host: github.com
  registries:
    pypi: []
    conda: []
    julia: []
  publications:
  - doi: 10.5281/zenodo.10714765
    role: canonical
    note: null
collected:
  scanned_at: '2026-08-28T12:56:06+00:00'
  snapshot: '2026-08-28'
  visibility: public
  language: Jupyter Notebook
  stars: 21
  forks: 7
  contributors: 3
  releases: 4
  commits: 127
  last_commit_at: '2026-05-08T00:37:47Z'
  created_at: '2022-11-15T21:58:19Z'
  latest_release_at: '2024-09-24T20:37:04Z'
  archived: false
  lines_of_code_estimate: 1157
  loc_basis: language bytes / 32, notebooks excluded
  canonical_citations: 1
  dependencies: []
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
  ran_at: 2026-08-20 08:11:47+00:00
  duration_seconds: 34.2
  turns: 6
  input_tokens: 8700
  output_tokens: 2370
  cache_read_tokens: 182101
  cache_write_tokens: 8745
  total_tokens: 201916
  api_list_cost_usd: 0.1443
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

# DASstore

Source: [niyiyu/DASstore](https://github.com/niyiyu/DASstore)

## Summary

DASstore is a Python client library that provides object storage for distributed acoustic sensing (DAS) data, moving DAS data hosting from HDF5 files to the cloud-optimized Zarr format served through object storage (e.g. MinIO/S3-compatible backends) rather than flat files on disk. Researchers query subsets of channels and time ranges directly from a remote store via `dasstore.zarr.Client` methods such as `get_data()`, `get_metadata()`, and `get_channel()`, without downloading full HDF5 files. It also standardizes experiment metadata into a five-level hierarchy (Overview, Cable/Fiber, Interrogator, Acquisition, Channel) following DAS-RCN conventions. What differentiates it from a generic HDF5/DAS reader is this cloud-native storage and partial-access model, paired with a live hosted service (DASway) exposing real DAS datasets for remote querying rather than local file parsing alone.

## Details

- **Interface:** library (Python client, `dasstore.zarr.Client`); example notebooks (Google Colab tutorials for SeaDAS-N and Turkey earthquake datasets) are also provided
- **Data formats:** writes Zarr (primary); mentions TileDB as an alternative backend; reads DAS sensor/experiment data (source format not further specified)
- **Key dependencies:** Zarr, MinIO (object storage deployment), TileDB (alternative backend)
- **Scope signals:** marked "Experimental" lifecycle badge; published in *Seismological Research Letters* (2024, vol. 95, issue 1); has GitHub Actions test workflow with codecov coverage badge; connected to DAS-RCN metadata conventions; backs an active hosted data service (DASway)
- **Source visible:** yes, full implementation, tests, and tutorials published on GitHub under GPL-3.0
- **Sources read:** https://github.com/niyiyu/DASstore, https://raw.githubusercontent.com/niyiyu/DASstore/main/README.md
