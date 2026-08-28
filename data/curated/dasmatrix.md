---
id: dasmatrix
name: DASMatrix
repository: QIanGua/DASMatrix
repository_url: https://github.com/QIanGua/DASMatrix
homepage: https://qiangua.github.io/DASMatrix
description: Python framework for DAS acquisition, processing, and analysis.
status: included
decision_reason: Reusable DAS-specific Python framework with an MIT license, published documentation,
  and continuous integration.
primary_category: core-framework
capabilities:
- data-model
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
- github.com/qiangua/dasmatrix
reviewed_at: '2026-08-28'
provenance:
  agent: das-summarizer
  models:
  - claude-haiku-4-5-20251001
  - claude-sonnet-5
  ran_at: '2026-08-20T08:12:11+00:00'
  duration_seconds: 23.1
  turns: 5
  input_tokens: 9659
  output_tokens: 1690
  cache_read_tokens: 149360
  cache_write_tokens: 2324
  total_tokens: 163033
  api_list_cost_usd: 0.0897
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

## Summary

DASMatrix is a Python library for processing and analyzing distributed acoustic sensing (DAS) data, built around a chainable `DASFrame` class and a functional API for composing processing pipelines. It targets researchers and engineers working in geophysics, structural health monitoring, and security surveillance who need to ingest DAS recordings in a wide range of vendor and interchange formats and run out-of-core, JIT-accelerated processing on them. What distinguishes it from a generic signal-processing toolkit is its breadth of native DAS format support (12+ formats spanning major interrogator vendors and general array-data containers) combined with lazy loading via Xarray/Dask and built-in hooks for machine-learning inference, rather than requiring users to write custom format parsers or conversion scripts before analysis.

## Details

- **Interface:** library (Python), with a chainable `DASFrame` API and functional processing pipeline
- **Data formats:** DAT, HDF5, PRODML, Silixa, Febus, Terra15, APSensing, ZARR, NetCDF, SEG-Y, MiniSEED, TDMS
- **Key dependencies:** Xarray, Dask, Numba, PyTorch, ONNX, Pint, Matplotlib
- **Scope signals:** MIT-licensed, early-stage (1 star, 66 commits on main), includes CI/CD via GitHub Actions, pre-commit hooks, examples, tests, and documentation — signals a young but professionally structured project rather than a mature, widely-adopted one
- **Source visible:** yes, full source code is published in the repository (modules for data acquisition, processing, ML inference, visualization, and configuration)
- **Sources read:** https://github.com/QIanGua/DASMatrix (documentation site at https://qiangua.github.io/DASMatrix redirects to a non-resolving domain, qiangua.me, so it was not reachable)
