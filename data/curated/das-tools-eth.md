---
id: das-tools-eth
name: DAS_Tools
repository: afichtner/DAS_Tools
repository_url: https://github.com/afichtner/DAS_Tools
homepage: null
description: Reading, writing, and frequency-wavenumber filtering routines for DAS data.
status: included
decision_reason: Reusable DAS-specific Python tools published with no license file, which grants no reuse
  rights.
primary_category: processing
capabilities:
- io
- processing
- visualization
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
- github.com/afichtner/das_tools
reviewed_at: '2026-08-28'
provenance:
  agent: das-summarizer
  models:
  - claude-haiku-4-5-20251001
  - claude-sonnet-5
  ran_at: '2026-08-20T08:10:19+00:00'
  duration_seconds: 48.0
  turns: 9
  input_tokens: 17572
  output_tokens: 3164
  cache_read_tokens: 267242
  cache_write_tokens: 4217
  total_tokens: 292195
  api_list_cost_usd: 0.1596
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

## Summary

DAS_Tools is a small collection of two Python modules (`fk.py`, `helpers.py`) for post-processing distributed acoustic sensing records once they are already loaded into memory as NumPy arrays. It provides frequency-wavenumber (f-k) transforms, dispersion-curve and phase-velocity filtering in the f-k domain, conversion to frequency-slowness and frequency-velocity representations, plus supporting utilities for plotting record sections, cropping data by space/time extent, and comparing two traces in the frequency and time domains after bandpass filtering. It would suit a researcher already working with DAS or dense seismic array data in Python/ObsPy who wants ready-made f-k filtering and quick-look plotting routines rather than a full acquisition-to-analysis pipeline. Unlike a generic toolkit, it is narrowly scoped to array-processing operations (f-k analysis and related filtering) rather than instrument I/O, metadata handling, or a broader processing framework.

## Details

- **Interface:** library (two importable Python modules, no CLI or GUI observed)
- **Data formats:** not stated — despite the repository description mentioning "reading, writing," neither source file performs file I/O or references a specific DAS/seismic file format; functions operate on in-memory NumPy arrays
- **Key dependencies:** NumPy, SciPy (`interpolate`), Matplotlib, ObsPy (including `obspy.signal.filter.bandpass`)
- **Scope signals:** very small (2 files, 4 stars, 0 forks), no README, no license file, no tests or packaging files visible — appears to be a personal/lab utility script collection rather than a maintained package
- **Source visible:** yes, both `fk.py` and `helpers.py` are published and were read directly
- **Sources read:** https://github.com/afichtner/DAS_Tools, https://api.github.com/repos/afichtner/DAS_Tools, https://api.github.com/repos/afichtner/DAS_Tools/contents/, https://raw.githubusercontent.com/afichtner/DAS_Tools/master/fk.py, https://raw.githubusercontent.com/afichtner/DAS_Tools/master/helpers.py
