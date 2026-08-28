---
id: das-to-store
name: das-to-store
repository: jacobrdavis/das-to-store
repository_url: https://github.com/jacobrdavis/das-to-store
homepage: null
description: Transformation of DAS interrogator output into cloud-native, analysis-ready stores.
status: included
decision_reason: Reusable DAS-specific conversion tooling with an MIT license.
primary_category: compression-storage
capabilities:
- conversion
- data-management
- io
- object-storage
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
- github.com/jacobrdavis/das-to-store
reviewed_at: '2026-08-28'
provenance:
  agent: das-summarizer
  models:
  - claude-haiku-4-5-20251001
  - claude-sonnet-5
  ran_at: '2026-08-20T08:10:19+00:00'
  duration_seconds: 35.3
  turns: 6
  input_tokens: 8987
  output_tokens: 2872
  cache_read_tokens: 187937
  cache_write_tokens: 3113
  total_tokens: 202909
  api_list_cost_usd: 0.1183
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

## Summary

das-to-store is a Python toolkit for converting distributed acoustic sensing (DAS) interrogator output files into cloud-native, analysis-ready virtual datasets and stores. It provides source modules organized around "interrogators" (handling DAS instrument output), "kerchunk" (building virtual/indexed references over the raw data), and a "catalog" component, alongside a demo Jupyter notebook illustrating the workflow. The project targets researchers or data engineers working with DAS field data who need to expose large raw interrogator files as queryable, chunked datasets without duplicating the underlying data — a task distinct from generic DAS processing or visualization toolkits, since it focuses specifically on the storage/indexing layer using the Zarr/Kerchunk virtual-dataset ecosystem rather than signal processing or analysis. The project is early-stage, single-author, with no released version history beyond internal tagging.

## Details

- **Interface:** library (Python package under `src/das_to_store/`), with a demo Jupyter notebook (`demo.ipynb`) and supporting scripts
- **Data formats:** input format not explicitly stated in the README; output described as "cloud-native, analysis-ready virtual datasets and stores" (built via Zarr and Kerchunk, per dependencies)
- **Key dependencies:** xarray, dask, zarr (pinned 2.18.3), kerchunk, numcodecs, netcdf4, h5netcdf, numpy, pandas, scipy, pytorch
- **Scope signals:** early-stage (0 stars/forks/issues at time of reading), ~15 commits, single author (Jake Davis, WHOI), MIT licensed, Python >=3.13 required, dependencies managed via conda `environment.yml` rather than `pyproject.toml`
- **Source visible:** yes — actual implementation exists under `src/das_to_store/` (`catalog/`, `interrogators/`, `kerchunk/` subpackages), plus a working demo notebook, not just a description
- **Sources read:** https://github.com/jacobrdavis/das-to-store, https://raw.githubusercontent.com/jacobrdavis/das-to-store/main/pyproject.toml, https://github.com/jacobrdavis/das-to-store/tree/main/src/das_to_store, https://raw.githubusercontent.com/jacobrdavis/das-to-store/main/environment.yml
