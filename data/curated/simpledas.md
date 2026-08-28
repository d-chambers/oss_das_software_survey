---
id: simpledas
name: simpleDAS
repository: ASN-Norway/simpleDAS
repository_url: https://github.com/ASN-Norway/simpleDAS
homepage: null
description: Vendor-published Python reader for ASN OptoDAS file formats.
status: included
decision_reason: Reusable DAS reader released by the interrogator vendor under GPL-3.0.
primary_category: data-management
capabilities:
- data-management
- io
license_spdx: GPL-3.0-only
license_class: osi-approved
forge:
  kind: github
  host: github.com
registries:
  pypi: []
  conda: []
  julia: []
publications: []
das_focus: das-native
sources:
- github.com/asn-norway/simpledas
reviewed_at: '2026-08-28'
provenance:
  agent: das-summarizer
  models:
  - claude-haiku-4-5-20251001
  - claude-sonnet-5
  ran_at: '2026-08-20T08:17:12+00:00'
  duration_seconds: 23.3
  turns: 4
  input_tokens: 6346
  output_tokens: 1615
  cache_read_tokens: 142974
  cache_write_tokens: 7737
  total_tokens: 158672
  api_list_cost_usd: 0.1154
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

## Summary

simpleDAS is a Python library from ASN (Alcatel Submarine Networks) Norway for reading, processing, and writing files in ASN's OptoDAS format, an HDF5-based file layout used by ASN's own distributed acoustic sensing interrogators. It loads DAS records into pandas DataFrames, with channel numbers as columns and timestamps as rows, and carries along instrument metadata rather than treating the file as a bare array. It also ships a small CLI utility, `print_hdf5`, for inspecting HDF5 file structure and contents. The library is aimed at users of ASN's own DAS hardware who need to load, manipulate, and re-save OptoDAS acquisitions in Python, rather than at general DAS format conversion; it is vendor-specific rather than a generic multi-format DAS toolkit.

## Details

- **Interface:** library (Python package), plus a bundled CLI tool (`print_hdf5`) for HDF5 inspection
- **Data formats:** reads and writes ASN OptoDAS files (HDF5-based); no other DAS formats stated
- **Key dependencies:** h5py, numpy, pandas, sympy, matplotlib
- **Scope signals:** modest adoption (28 stars, 10 forks per GitHub), 16 commits on master, versioned via hatch-vcs (dynamic versioning), documentation and Jupyter notebook examples included; appears to be a maintained internal-tool-turned-public-release rather than a large community project
- **Source visible:** yes — repository contains actual source under `src/simpledas/`, plus `doc/`, `examples/`, `pyproject.toml`, `hatch.toml`, and a `COPYING` (GPL-3.0) license file
- **Sources read:** https://github.com/ASN-Norway/simpleDAS, https://raw.githubusercontent.com/ASN-Norway/simpleDAS/master/pyproject.toml
