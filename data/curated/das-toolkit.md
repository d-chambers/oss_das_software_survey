---
id: das-toolkit
name: das-toolkit
repository: RobbinLuo/das-toolkit
repository_url: https://github.com/RobbinLuo/das-toolkit
homepage: null
description: Python toolkit for common DAS reading and processing steps.
status: included
decision_reason: Reusable DAS-specific Python toolkit with an MIT license.
primary_category: processing
capabilities:
- io
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
- github.com/robbinluo/das-toolkit
reviewed_at: '2026-08-28'
provenance:
  agent: das-summarizer
  models:
  - claude-haiku-4-5-20251001
  - claude-sonnet-5
  ran_at: '2026-08-20T08:10:19+00:00'
  duration_seconds: 39.6
  turns: 7
  input_tokens: 9807
  output_tokens: 3204
  cache_read_tokens: 220860
  cache_write_tokens: 9639
  total_tokens: 243510
  api_list_cost_usd: 0.171
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

## Summary

das-toolkit is a small Python library for reading and preprocessing distributed acoustic sensing (DAS) waveform data. Its core module provides a unified `read_das` function that dispatches to format-specific readers for HDF5, TDMS, and SEG-Y files, returning either file metadata (sampling interval, channel count, gauge length) or channel/time-sliced trace arrays. It also includes basic signal-conditioning routines: detrending and median-offset removal, Tukey tapering, and Butterworth band-pass, high-pass, and low-pass filtering. This is a utility library rather than a full processing pipeline or application — it targets researchers who already have DAS acquisition files (from interrogators that write TDMS, HDF5, or SEG-Y) and need a lightweight, dependency-thin way to load and clean traces before their own analysis, rather than a generic seismic-processing toolkit with visualization, event detection, or inversion capabilities.

## Details

- **Interface:** library (Python package, `DasTools`), with two Jupyter notebooks (`DAS_demo.ipynb`, `DAS_demo_2.ipynb`) as usage demonstrations
- **Data formats:** reads `.h5` (HDF5), `.tdms` (TDMS), and `.segy`/`.sgy` (SEG-Y); no write/export formats stated
- **Key dependencies:** `h5py`, `nptdms`, `numpy`, `scipy`, `segyio` (pinned versions in `requirements.txt`: h5py 2.10.0, nptdms 1.6.0, numpy 1.18.5, scipy 1.5.0, segyio 1.9.9)
- **Scope signals:** small and lightly maintained — 9 commits on `main`, 20 stars, 2 forks, 1 watcher; single core module (`DasPrep.py`) plus package init; MIT licensed; README is a bare title with no prose documentation
- **Source visible:** yes — the `DasTools` directory contains real implementation code (`DasPrep.py`), not just a description
- **Sources read:** https://github.com/RobbinLuo/das-toolkit, https://raw.githubusercontent.com/RobbinLuo/das-toolkit/main/README.md, https://raw.githubusercontent.com/RobbinLuo/das-toolkit/main/requirements.txt, https://github.com/RobbinLuo/das-toolkit/tree/main/DasTools, https://raw.githubusercontent.com/RobbinLuo/das-toolkit/main/DasTools/DasPrep.py
