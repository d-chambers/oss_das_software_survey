---
id: derzug
name: DerZug
repository: DASDAE/derzug
repository_url: https://github.com/DASDAE/derzug
homepage: null
description: Interactive DFOS visualization and annotation application built on DASCore.
status: included
decision_reason: Reusable DFOS application with GPL-3.0 licensing and PyPI and conda-forge releases; self-declared
  experimental, which the policy does not exclude.
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
das_focus: das-native
sources:
- github.com/dasdae/derzug
reviewed_at: '2026-08-28'
provenance:
  agent: das-summarizer
  models:
  - claude-haiku-4-5-20251001
  - claude-sonnet-5
  ran_at: '2026-08-20T08:13:02+00:00'
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

## Summary

DerZug is an early-stage visualization and workflow tool for distributed fiber optic sensing (DFOS) research, built on the DASCore ecosystem. It lets researchers interactively create, debug, and share reproducible DFOS workflows, either through a standalone GUI application or programmatically as a Python library. Its core feature is a waterfall-style visualization window for viewing seismic patches produced by DASCore, combined with a workflow-building interface adapted from the Orange3 data-mining platform. It targets researchers and practitioners already working within the DASDAE/DASCore software stack who need an interactive way to inspect data and construct analysis pipelines, rather than a general-purpose plotting or data-management toolkit. The project is explicitly described by its authors as a proof of concept, not production-ready software, with no commitment to ongoing maintenance.

## Details

- **Interface:** GUI application (standalone, launched from the command line) and interactive Python library; also offers a demo mode
- **Data formats:** not stated (README does not name specific file formats such as TDMS, HDF5, or SEG-Y; it references DASCore "patches" as the data unit)
- **Key dependencies:** Orange3, PyQtGraph, DASCore
- **Scope signals:** README explicitly states "DerZug is an early-stage proof of concept. Expect bugs, incomplete behavior, data-loss risks, and frequent breaking changes," and the authors "make no promises of further development or maintenance"; installable via PyPI or conda/mamba
- **Source visible:** yes — repository contains source code (src/, tests/, scripts/ directories, ~57 commits), not just a description
- **Sources read:** https://github.com/DASDAE/derzug, https://raw.githubusercontent.com/DASDAE/derzug/main/README.md
