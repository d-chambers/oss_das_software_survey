---
curated:
  id: derzug
  name: DerZug
  repository: DASDAE/derzug
  repository_url: https://github.com/DASDAE/derzug
  homepage: null
  description: Interactive DFOS visualization and annotation application built on DASCore.
  status: included
  decision_reason: Reusable DFOS application with GPL-3.0 licensing and PyPI and conda-forge releases;
    self-declared experimental, which the policy does not exclude.
  primary_category: visualization-annotation
  capabilities:
  - annotation
  - desktop-application
  - processing
  - visualization
  license_spdx: GPL-3.0-only
  license_class: osi-approved
  forge:
    kind: github
    host: github.com
  registries:
    pypi:
    - derzug
    conda:
    - conda-forge/derzug
    julia: []
  publications: []
collected:
  scanned_at: '2026-08-18T06:38:09+00:00'
  snapshot: '2026-08-17'
  visibility: public
  language: Python
  stars: 4
  forks: 0
  contributors: 1
  releases: 11
  commits: 57
  last_commit_at: '2026-08-13T15:11:16Z'
  created_at: '2026-03-09T10:20:00Z'
  latest_release_at: '2026-08-13T15:12:13Z'
  archived: false
  lines_of_code_estimate: 88404
  loc_basis: language bytes / 32, notebooks excluded
  pypi_downloads_180d: 1495
  pypi_downloads_30d: 259
  conda_downloads_total: 2269
  dependencies:
  - package: derzug
    dependency: dascore
    requirement: '>=0.1.15'
    marker: ''
    dependency_project: dascore
  - package: derzug
    dependency: orange3
    requirement: ''
    marker: ''
    dependency_project: null
  - package: derzug
    dependency: pyqt6
    requirement: '!=6.8.*'
    marker: ''
    dependency_project: null
  - package: derzug
    dependency: pyqtgraph
    requirement: ''
    marker: ''
    dependency_project: null
  - package: derzug
    dependency: typer
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
  ran_at: 2026-08-20 08:13:02+00:00
  duration_seconds: 24.7
  turns: 4
  input_tokens: 6371
  output_tokens: 1978
  cache_read_tokens: 148826
  cache_write_tokens: 2467
  total_tokens: 159642
  api_list_cost_usd: 0.0895
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

# DerZug

Source: [DASDAE/derzug](https://github.com/DASDAE/derzug)

## Summary

DerZug is an early-stage visualization and workflow tool for distributed fiber optic sensing (DFOS) research, built on the DASCore ecosystem. It lets researchers interactively create, debug, and share reproducible DFOS workflows, either through a standalone GUI application or programmatically as a Python library. Its core feature is a waterfall-style visualization window for viewing seismic patches produced by DASCore, combined with a workflow-building interface adapted from the Orange3 data-mining platform. It targets researchers and practitioners already working within the DASDAE/DASCore software stack who need an interactive way to inspect data and construct analysis pipelines, rather than a general-purpose plotting or data-management toolkit. The project is explicitly described by its authors as a proof of concept, not production-ready software, with no commitment to ongoing maintenance.

## Details

- **Interface:** GUI application (standalone, launched from the command line) and interactive Python library; also offers a demo mode
- **Data formats:** not stated (README does not name specific file formats such as TDMS, HDF5, or SEG-Y; it references DASCore "patches" as the data unit)
- **Key dependencies:** Orange3, PyQtGraph, DASCore
- **Scope signals:** README explicitly states "DerZug is an early-stage proof of concept. Expect bugs, incomplete behavior, data-loss risks, and frequent breaking changes," and the authors "make no promises of further development or maintenance"; installable via PyPI or conda/mamba
- **Source visible:** yes — repository contains source code (src/, tests/, scripts/ directories, ~57 commits), not just a description
- **Sources read:** https://github.com/DASDAE/derzug, https://raw.githubusercontent.com/DASDAE/derzug/main/README.md
