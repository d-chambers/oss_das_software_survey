---
curated:
  id: daspack
  name: DASPack
  repository: asleix/daspack
  repository_url: https://github.com/asleix/daspack
  homepage: null
  description: Lossless and fixed-accuracy lossy compression for large DAS datasets.
  status: included
  decision_reason: Reusable DAS-specific compressor with a BSD-3-Clause license and package release.
  primary_category: compression-storage
  capabilities:
  - compression
  - io
  - streaming
  license_spdx: BSD-3-Clause
  license_class: osi-approved
  forge:
    kind: github
    host: github.com
  registries:
    pypi:
    - daspack-dev
    conda: []
    julia: []
  publications:
  - doi: 10.1093/gji/ggaf397
    role: canonical
    note: null
collected:
  scanned_at: '2026-08-18T06:37:54+00:00'
  snapshot: '2026-08-17'
  visibility: public
  language: Rust
  stars: 25
  forks: 5
  contributors: 1
  releases: 0
  commits: 20
  last_commit_at: '2025-10-16T15:06:15Z'
  created_at: '2025-07-11T15:05:39Z'
  archived: false
  lines_of_code_estimate: 6658
  loc_basis: language bytes / 32, notebooks excluded
  pypi_downloads_180d: 314
  pypi_downloads_30d: 102
  canonical_citations: 8
  dependencies:
  - package: daspack-dev
    dependency: numpy
    requirement: '>=1.24'
    marker: ''
    dependency_project: null
  has_docs: true
  has_tests: true
  has_ci: false
  unavailable:
    pypi_downloads_total: no free source publishes all-time PyPI totals
    conda_downloads_180d: anaconda.org publishes a cumulative count only, with no time series
summary:
  agent: das-summarizer
  models:
  - claude-haiku-4-5-20251001
  - claude-sonnet-5
  ran_at: 2026-08-20 08:11:26+00:00
  duration_seconds: 19.0
  turns: 3
  input_tokens: 6312
  output_tokens: 1399
  cache_read_tokens: 104824
  cache_write_tokens: 7499
  total_tokens: 120034
  api_list_cost_usd: 0.0991
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

# DASPack

Source: [asleix/daspack](https://github.com/asleix/daspack)

## Summary

DASPack is an open-source data compressor built specifically for Distributed Acoustic Sensing (DAS) datasets. It supports both lossless compression and lossy compression with guaranteed, user-controlled error bounds, letting users trade off file size against reconstruction accuracy. Its pipeline quantizes the data, applies a 5/3 wavelet transform, performs 2-D linear predictive coding, and finishes with arithmetic coding; quantization is skipped for integer inputs. Unlike generic compressors (e.g. gzip or standard HDF5 filters), it is tailored to the structure of DAS strain-rate arrays and reports throughput above 800 MB/s on an 8-core laptop. It targets DAS researchers and infrastructure operators who need to shrink very large continuous fiber-optic sensing datasets for storage or transfer while preserving numerical fidelity within a known tolerance. The core is written in pure Rust with no unsafe C buffers, exposed to users through a Python wrapper.

## Details

- **Interface:** library (Python package wrapping a Rust core; no CLI or GUI mentioned)
- **Data formats:** reads NumPy arrays (integer and floating-point); writes binary bitstreams as uint8 byte arrays, described as compatible with HDF5 storage
- **Key dependencies:** Python ≥ 3.9, Rust ≥ 1.74 (for building from source); NumPy and h5py used in examples
- **Scope signals:** actively maintained per the README; 25 GitHub stars; accompanying academic paper published in *Geophysical Journal International* (2025); supports multi-threading with configurable thread counts, block sizes, predictor levels, and prediction order
- **Source visible:** yes, the repository publishes source code (Rust core plus Python bindings)
- **Sources read:** https://github.com/asleix/daspack
