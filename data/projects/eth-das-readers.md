---
curated:
  id: eth-das-readers
  name: ETH_DAS_readers
  repository: dcbowden/ETH_DAS_readers
  repository_url: https://github.com/dcbowden/ETH_DAS_readers
  homepage: null
  description: Python readers for HDF5 DAS data in the Silixa and PRODML 2.1 header formats.
  status: included
  decision_reason: Reusable DAS format readers published with no license file, which grants no reuse rights.
  primary_category: data-management
  capabilities:
  - data-management
  - io
  license_spdx: null
  license_class: unlicensed
  forge:
    kind: github
    host: github.com
  registries:
    pypi: []
    conda: []
    julia: []
  publications: []
collected:
  scanned_at: '2026-08-18T06:38:23+00:00'
  snapshot: '2026-08-17'
  visibility: public
  language: Jupyter Notebook
  stars: 7
  forks: 0
  contributors: 1
  releases: 0
  commits: 12
  last_commit_at: '2024-11-22T00:18:34Z'
  created_at: '2023-01-31T15:18:00Z'
  archived: false
  lines_of_code_estimate: 2595
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
  ran_at: 2026-08-20 08:13:36+00:00
  duration_seconds: 39.1
  turns: 7
  input_tokens: 23348
  output_tokens: 3013
  cache_read_tokens: 221412
  cache_write_tokens: 9526
  total_tokens: 257299
  api_list_cost_usd: 0.1797
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

# ETH_DAS_readers

Source: [dcbowden/ETH_DAS_readers](https://github.com/dcbowden/ETH_DAS_readers)

## Summary

ETH_DAS_readers is a small Python toolkit for reading and writing distributed acoustic sensing (DAS) data stored in HDF5 files that follow the Silixa iDAS / PRODML 2.1 header convention. It provides functions to load headers only, load a single file's full data, or assemble data across a requested time and distance window by stitching together multiple files, with optional unit conversion and downsampling. It also writes processed data back out to HDF5 using a consistent internal header naming scheme, so the same reader can be reused on both raw instrument files and custom-converted datasets. It targets researchers at ETH Zürich (and similarly equipped groups) working with Silixa iDAS acquisitions who need a lightweight, format-aware loader rather than a full processing framework; it does not implement the complete PRODML standard, only the headers the authors found useful, and channel-mapping support was still unsettled as of the last documented update.

## Details

- **Interface:** library (Python module `pydas_readers`) plus five example Jupyter notebooks
- **Data formats:** reads and writes HDF5 DAS files following the Silixa / PRODML 2.1 header convention (not a full PRODML implementation)
- **Key dependencies:** h5py, numpy; standard library `os`, `datetime`, `glob`, `re`
- **Scope signals:** small research-utility project (7 stars, 12 commits, no open issues/PRs), last updated April 2023, maintained by ETH Zürich researchers (contacts daniel.bowden@erdw.ethz.ch, patrick.paitz@erdw.ethz.ch); README notes channel-mapping handling was still unresolved as of January 2023
- **Source visible:** yes — repository publishes the `pydas_readers` package (`readers/load_das_h5.py`, `readers/write_das_h5.py`, plus `mapping` and `util` subfolders) and the example notebooks
- **Sources read:**
  - https://github.com/dcbowden/ETH_DAS_readers
  - https://raw.githubusercontent.com/dcbowden/ETH_DAS_readers/master/README.md
  - https://github.com/dcbowden/ETH_DAS_readers/tree/master/pydas_readers
  - https://github.com/dcbowden/ETH_DAS_readers/tree/master/pydas_readers/readers
  - https://raw.githubusercontent.com/dcbowden/ETH_DAS_readers/master/pydas_readers/readers/load_das_h5.py
