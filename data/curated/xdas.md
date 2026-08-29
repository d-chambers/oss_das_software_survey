---
id: xdas
name: xdas
repository: xdas-dev/xdas
repository_url: https://github.com/xdas-dev/xdas
homepage: https://xdas.readthedocs.io
description: Labeled arrays, multi-file access, streaming, and scalable processing for DAS data.
status: included
decision_reason: Reusable DAS-specific framework with GPL-3.0 licensing and package releases.
primary_category: core-framework
capabilities:
- data-management
- data-model
- io
- processing
- streaming
- visualization
license_spdx: GPL-3.0-only
license_class: osi-approved
forge:
  kind: github
  host: github.com
registries:
  pypi:
  - xdas
  conda: []
  julia: []
publications:
- doi: 10.1785/0220240366
  role: canonical
  note: null
- doi: 10.31223/x5141g
  role: related
  note: the EarthArXiv preprint of the canonical paper, cited separately
das_focus: das-native
sources:
- github.com/xdas-dev/xdas
reviewed_at: '2026-08-28'
provenance:
  agent: das-summarizer
  models:
  - claude-haiku-4-5-20251001
  - claude-sonnet-5
  ran_at: '2026-08-20T08:17:39+00:00'
  duration_seconds: 47.6
  turns: 8
  input_tokens: 9968
  output_tokens: 3603
  cache_read_tokens: 263112
  cache_write_tokens: 10206
  total_tokens: 286889
  api_list_cost_usd: 0.191
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

## Summary

xdas is a Python library for managing, processing, and visualizing distributed acoustic sensing (DAS) data, aimed at DAS researchers and seismologists who work with dense, multi-file recordings from fiber-optic interrogators. It reads DAS formats into self-described array objects that pair data with coordinate metadata, borrowing labeled-array concepts from Xarray and a lazy-computation model inspired by Dask. Its stated differentiator from a generic array toolkit is native support for larger-than-memory processing across multi-file DAS datasets with optimized I/O, plus multi-threaded implementations of common DAS signal-processing routines, and interoperability with NumPy/SciPy for custom pipelines. The authors note it can also be applied to other dense N-dimensional sensor data, such as large-N seismic arrays, beyond DAS specifically.

## Details

- **Interface:** library (installable via `pip install xdas`)
- **Data formats:** not stated precisely on the pages read; the `xdas.io` module operates on HDF5 files (e.g. an in-place dataset `compress` utility) and includes `ZMQPublisher`/`ZMQSubscriber` classes for streaming data over ZeroMQ in an ASN (interrogator) context; no explicit list of vendor formats (e.g. Febus, Silixa, Sintela, TDMS, SEG-Y) was found in the pages fetched
- **Key dependencies:** dask, h5netcdf, h5py, hdf5plugin, numba, numpy, obspy, pandas, plotly, scipy, xarray, pyzmq, loky, msgpack, tqdm, xinterp (per `pyproject.toml`)
- **Scope signals:** ~73 GitHub stars, 16 forks, 1,124 commits, active issue tracker (3 open issues, 1 open PR), codecov integration, and a documentation/tutorial site — signals of an actively maintained but modest-sized research-community project rather than a large-scale production system; requires Python ≥ 3.10
- **Source visible:** yes, source code is published in the GitHub repository (not just a description)
- **Sources read:** https://github.com/xdas-dev/xdas, https://xdas.readthedocs.io, https://raw.githubusercontent.com/xdas-dev/xdas/main/pyproject.toml, https://xdas.readthedocs.io/en/latest/api/io.html, https://xdas.readthedocs.io/en/latest/api/index.html
