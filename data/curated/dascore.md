---
id: dascore
name: DASCore
repository: DASDAE/dascore
repository_url: https://github.com/DASDAE/dascore
homepage: https://dascore.org
description: General data model, I/O, processing, and visualization for distributed fiber sensing.
status: included
decision_reason: Reusable DAS-specific library with documented LGPL-3.0-or-later licensing and package
  releases.
primary_category: core-framework
capabilities:
- data-management
- data-model
- io
- processing
- visualization
license_spdx: LGPL-3.0-or-later
license_class: osi-approved
forge:
  kind: github
  host: github.com
registries:
  pypi:
  - dascore
  conda:
  - conda-forge/dascore
  julia: []
publications:
- doi: 10.26443/seismica.v3i2.1184
  role: canonical
  note: null
- doi: 10.31223/x5b978
  role: related
  note: the EarthArXiv preprint of the canonical paper, cited separately
das_focus: das-native
sources:
- github.com/dasdae/dascore
reviewed_at: '2026-08-28'
provenance:
  agent: das-summarizer
  models:
  - claude-haiku-4-5-20251001
  - claude-sonnet-5
  ran_at: '2026-08-20T08:11:02+00:00'
  duration_seconds: 49.0
  turns: 9
  input_tokens: 14785
  output_tokens: 3552
  cache_read_tokens: 307563
  cache_write_tokens: 4391
  total_tokens: 330291
  api_list_cost_usd: 0.1726
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

## Summary

DASCore is a Python library for working with distributed acoustic sensing (DAS) data, a fiber-optic sensing technology used to record seismic and other ground-motion signals along a cable. It provides programmatic tools to read, write, and manipulate DAS data through a `Patch`/`Spool` data model, along with common processing routines (filtering, decimation, detrending) and basic visualization (e.g., waterfall plots). It targets researchers and engineers in geophysics and seismology who need to work with fiber-optic sensing datasets in Python rather than through a standalone application. What distinguishes it from a generic array-processing toolkit is its broad, purpose-built support for the many proprietary and vendor-specific DAS file formats produced by interrogator hardware, unifying them behind a consistent API. It is developed under the DAS Data Analysis Ecosystem (DASDAE) and was described in a peer-reviewed 2024 Seismica paper.

## Details

- **Interface:** library (Python; imported into scripts, e.g. `dc.spool()`, `patch.decimate()`, `patch.viz.waterfall()`)
- **Data formats:** reads APSENSING, DASDAE, DASHDF5, DASVADER, FEBUS (multiple variants incl. FEBUS_G1_CSV, FEBUS_MTX_H5, FEBUS_BSL_H5, FEBUS_T1), GDR_DAS, H5SIMPLE, NEUBREXRFS, NEUBREXDAS, OPTODAS (v8–11), PICKLE, PRODML (2, 2.1), SEGY (multiple versions), SENTEK, SILIXA_H5, SINTELA_BINARY, SR4731, TDMS, TERRA15 (v4–6), XMLBINARY; writes DASDAE (v1), SEGY (v0, 0.1, 1, 2, 2.1), RSF (v1), and WAV
- **Key dependencies:** numpy, pandas, scipy, matplotlib, h5py, pytables (`tables`), pydantic, pint, pooch, rich, packaging, typing_extensions; optional extras include xarray, obspy, numba, segyio, findiff, bottleneck
- **Scope signals:** ~159 GitHub stars, 41 forks, 526 commits, 41 contributors; PyPI/Conda-Forge distribution; listed as Development Status "4 - Beta"; supports Python 3.10–3.14; part of the DASDAE ecosystem; peer-reviewed publication in Seismica (2024)
- **Source visible:** yes, full source published on GitHub
- **Sources read:** https://github.com/DASDAE/dascore, https://dascore.org, https://dascore.org/supported_formats.html, https://raw.githubusercontent.com/DASDAE/dascore/master/pyproject.toml
