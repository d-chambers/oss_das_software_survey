---
id: daspy
name: DASPy
repository: HMZ-03/DASPy
repository_url: https://github.com/HMZ-03/DASPy
homepage: https://daspy-tutorial.readthedocs.io
description: Python toolbox for DAS seismology and common array-processing workflows.
status: included
decision_reason: Reusable DAS-specific toolbox with an MIT license, documentation, and package releases.
primary_category: processing
capabilities:
- io
- processing
- seismology
- visualization
license_spdx: MIT
license_class: osi-approved
forge:
  kind: github
  host: github.com
registries:
  pypi:
  - daspy-toolbox
  conda:
  - conda-forge/daspy-toolbox
  julia: []
publications:
- doi: 10.1785/0220240124
  role: canonical
  note: null
das_focus: das-native
sources:
- github.com/hmz-03/daspy
reviewed_at: '2026-08-28'
provenance:
  agent: das-summarizer
  models:
  - claude-haiku-4-5-20251001
  - claude-sonnet-5
  ran_at: '2026-08-20T08:11:34+00:00'
  duration_seconds: 26.8
  turns: 4
  input_tokens: 8679
  output_tokens: 1860
  cache_read_tokens: 143132
  cache_write_tokens: 8134
  total_tokens: 161805
  api_list_cost_usd: 0.1214
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

## Summary

DASPy is a Python library for processing Distributed Acoustic Sensing (DAS) data, which uses fiber optic cables as distributed seismic sensors. It combines standard seismic-processing operations (filtering, spectral analysis, visualization) with DAS-specific algorithms such as denoising, wavefield decomposition, and strain-to-velocity conversion, exposed through purpose-built data structures (`Section`, `Collection`, `DASDateTime`) rather than generic arrays. It targets DAS seismology researchers and practitioners who need domain-specific I/O and processing beyond what general seismology toolkits (e.g., ObsPy) provide out of the box. The project states its goal is to "lower the barrier for DAS processing" and support the growing field of DAS seismology; it is referenced in a peer-reviewed seismology journal publication (2024) and is distributed via PyPI and Conda-Forge, with tutorials in both English and Chinese.

## Details

- **Interface:** library (Python package, programmatic API; no CLI or GUI mentioned)
- **Data formats:** reads SEGY, HDF5, and TDMS files; documentation also mentions converting from other packages' formats
- **Key dependencies:** NumPy, SciPy, Matplotlib, h5py, segyio, nptdms
- **Scope signals:** 154 stars, 29 forks, 457 commits on main, MIT license, requires Python 3.9+, published via PyPI and Conda-Forge, cited in a 2024 peer-reviewed seismology journal — indicates an actively maintained, academically credible research tool rather than experimental or unmaintained code
- **Source visible:** yes — repository contains a `/daspy/` package directory, a `/document/` directory with tutorials/examples, and standard packaging files (`pyproject.toml`, `setup.py`)
- **Sources read:** https://github.com/HMZ-03/DASPy, https://daspy-tutorial.readthedocs.io
