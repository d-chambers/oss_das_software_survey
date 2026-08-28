---
id: dasvader-ds
name: DASVaderDS.jl
repository: marianoarnaiz/DASVaderDS.jl
repository_url: https://github.com/marianoarnaiz/DASVaderDS.jl
homepage: null
description: Julia detection, picking, and visualization tools for DAS data streams.
status: included
decision_reason: Reusable DAS-specific Julia library with an MIT license and a source tree distinct from
  DASVader.jl.
primary_category: core-framework
capabilities:
- detection
- io
- phase-picking
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
- github.com/marianoarnaiz/dasvaderds.jl
reviewed_at: '2026-08-28'
provenance:
  agent: das-summarizer
  models:
  - claude-haiku-4-5-20251001
  - claude-sonnet-5
  ran_at: '2026-08-20T08:12:03+00:00'
  duration_seconds: 21.2
  turns: 3
  input_tokens: 6868
  output_tokens: 1460
  cache_read_tokens: 104862
  cache_write_tokens: 7470
  total_tokens: 120660
  api_list_cost_usd: 0.1008
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

## Summary

DASVaderDS.jl is a Julia package for reading, processing, and visualizing distributed acoustic sensing (DAS) data, built specifically to run on servers and headless systems without a graphical display (the "DS" variant of a related "DASVader" package). It targets researchers in seismology and related fields who need command-line or server-based DAS analysis rather than an interactive desktop workflow. The package reads FEBUS A1 DAS HDF5 files and exposes functions such as `rdas()` for loading data and `viewdas()` for visualization, with plots exportable to PDF. It builds on the existing Julia seismology ecosystem (Seis.jl, FFTW.jl, FourierAnalysis.jl, Geodesics.jl) rather than reimplementing signal-processing primitives, and its distinguishing feature versus a generic toolkit is the headless/server orientation for DAS-specific formats.

## Details

- **Interface:** library (Julia package, programmatic API)
- **Data formats:** reads FEBUS A1 DAS HDF5 files; writes PDF figures via `savefig()`
- **Key dependencies:** Seis.jl, FFTW.jl, FourierAnalysis.jl, Geodesics.jl, a customized InteractiveViz.jl
- **Scope signals:** early-stage — unregistered Julia package (manual installation), 13 commits on main, no tagged releases, 0 stars/forks, documentation and examples marked "coming soon"; MIT licensed with example datasets provided
- **Source visible:** yes, source code is published in the repository
- **Sources read:** https://github.com/marianoarnaiz/DASVaderDS.jl
