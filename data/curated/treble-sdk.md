---
id: treble-sdk
name: TrebleSDK
repository: terra15collab/TrebleSDK
repository_url: https://github.com/terra15collab/TrebleSDK
homepage: null
description: Vendor code library for reading and streaming Terra15 Treble DAS data.
status: included
decision_reason: Reusable vendor-published DAS access code with no license file, which grants no reuse
  rights.
primary_category: data-management
capabilities:
- data-management
- io
- streaming
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
das_focus: das-native
sources:
- github.com/terra15collab/treblesdk
reviewed_at: '2026-08-28'
provenance:
  agent: das-summarizer
  models:
  - claude-haiku-4-5-20251001
  - claude-sonnet-5
  ran_at: '2026-08-20T08:17:37+00:00'
  duration_seconds: 25.7
  turns: 4
  input_tokens: 8851
  output_tokens: 1694
  cache_read_tokens: 143162
  cache_write_tokens: 7869
  total_tokens: 161576
  api_list_cost_usd: 0.1195
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

## Summary

TrebleSDK is a collection of example code for interacting with the Terra15 Treble distributed acoustic sensor, published by the vendor's own GitHub account (terra15collab). It shows engineers and researchers how to read and process DAS recordings stored in HDF5 files and how to pull real-time data streams from a Treble server via its API, using Python scripts, a Jupyter notebook ("Getting Started.ipynb"), and parallel MATLAB/Octave implementations. Unlike a generic signal-processing toolkit, its purpose is narrowly tied to one manufacturer's hardware and proprietary streaming API (distributed as platform-specific wheel packages for Linux, Windows, and macOS), rather than providing general-purpose DAS analysis routines. It includes sample HDF5 datasets so users can run the examples without owning a physical interrogator, making it primarily a vendor-supplied onboarding kit for Treble device owners rather than a research library.

## Details

- **Interface:** notebook collection and Python/MATLAB scripts (example code, not a packaged library or CLI)
- **Data formats:** reads HDF5 files (Treble sensor recordings); streams real-time data via the vendor's Treble API
- **Key dependencies:** pyqtgraph, matplotlib, pytz, pandas, pyside6, ipykernel, plus a platform-specific Terra15 Treble API wheel package; requires Python 3.10
- **Scope signals:** small vendor-maintained repo (31 commits, 6 stars, 2 forks) hosted under the official terra15collab account; scoped to one manufacturer's device rather than general DAS interoperability
- **Source visible:** yes — repository contains actual example scripts and notebooks (HDF5_samples/, API_samples/, MATLAB_samples/, sample_data/), not just a description
- **Sources read:** https://github.com/terra15collab/TrebleSDK, https://github.com/terra15collab/TrebleSDK/blob/master/requirements.txt
