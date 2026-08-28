---
id: dasview
name: DASView
repository: hetinghong/DASView
repository_url: https://github.com/hetinghong/DASView
homepage: null
description: Cross-platform desktop application for interactive DAS visualization and processing.
status: watchlist
decision_reason: MIT licensed and clearly in scope, but the repository publishes only a README, a license,
  and screenshots; no source code is available to review or reuse.
primary_category: visualization-annotation
capabilities:
- desktop-application
- processing
- visualization
license_spdx: MIT
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
- github.com/hetinghong/dasview
reviewed_at: '2026-08-28'
provenance:
  agent: das-summarizer
  models:
  - claude-haiku-4-5-20251001
  - claude-sonnet-5
  ran_at: '2026-08-20T08:12:17+00:00'
  duration_seconds: 29.4
  turns: 4
  input_tokens: 21097
  output_tokens: 1763
  cache_read_tokens: 143026
  cache_write_tokens: 7919
  total_tokens: 173805
  api_list_cost_usd: 0.1324
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

## Summary

DASView is a desktop GUI application for interactive visualization and analysis of distributed acoustic sensing (DAS) data, aimed at researchers and practitioners working in seismic monitoring and urban sensing. It provides 2D waterfall plots for spatio-temporal overviews, single-channel waveform and spectrum inspection, digital filtering (bandpass, low-pass, high-pass), automatic vehicle tracking via Kalman filtering, interactive phase picking for seismic arrivals, and common-mode noise removal with data decimation. It distinguishes itself from a generic plotting toolkit by bundling DAS-specific workflows — format ingestion via DASPy, ObsPy-compatible seismic handling, and domain analysis routines like vehicle tracking and phase picking — into a single no-code, point-and-click application distributed as pre-compiled installers for Windows, macOS, and Linux.

## Details

- **Interface:** GUI application (built with PyQt)
- **Data formats:** commercial interrogator formats, HDF5, TDMS, RAPID datasets, and OOI data via DASPy; seismic-standard formats via ObsPy compatibility
- **Key dependencies:** PyQt, DASPy, ObsPy
- **Scope signals:** small early-stage project (8 stars, 11 commits, described as "under active development"); accompanying manuscript is "currently under review"; distributed only as pre-built binaries ("No setup—just download and run")
- **Source visible:** No — the GitHub repository contains only `README.md`, `LICENSE`, and a `screenshots/` folder; no application source code is published in the repo. The described functionality is documented but not independently verifiable from source.
- **Sources read:** https://github.com/hetinghong/DASView (fetched twice: once for README content, once for repository file listing)
