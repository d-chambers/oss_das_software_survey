---
id: dastools
name: dastools
repository: geofon/dastools
repository_url: https://git.gfz-potsdam.de/geofon/dastools
homepage: null
description: Reading, conversion, and metadata tooling for DAS acquisitions, from GEOFON.
status: included
decision_reason: Reusable DAS tool set with GPL-3.0-or-later licensing and PyPI releases; the first catalogued
  project hosted outside GitHub.
primary_category: data-management
capabilities:
- conversion
- data-management
- io
- metadata
license_spdx: GPL-3.0-or-later
license_class: osi-approved
forge:
  kind: gitlab
  host: git.gfz-potsdam.de
registries:
  pypi:
  - dastools
  conda: []
  julia: []
publications: []
das_focus: das-native
sources:
- git.gfz-potsdam.de/geofon/dastools
reviewed_at: '2026-08-28'
provenance:
  agent: das-summarizer
  models:
  - claude-haiku-4-5-20251001
  - claude-sonnet-5
  ran_at: '2026-08-20T08:11:57+00:00'
  duration_seconds: 54.4
  turns: 11
  input_tokens: 9179
  output_tokens: 4412
  cache_read_tokens: 301169
  cache_write_tokens: 11106
  total_tokens: 325866
  api_list_cost_usd: 0.2165
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

## Summary

dastools is a Python package for reading, manipulating, and converting seismic waveforms produced by distributed acoustic sensing (DAS) interrogator systems. It targets researchers and engineers who need to move raw DAS output into formats usable by standard seismology workflows: it reads Silixa's TDMS format and OptoDAS/Alcatel's HDF5 format, and converts them to miniSEED, the standard format used across the seismological community and FDSN data centers. Unlike a generic file-conversion utility, it also ships an FDSN-compatible Dataselect web service (`dasws`), letting converted DAS data be served over the same protocol seismologists already use to query conventional seismic networks. It is maintained by GFZ Potsdam's GEOFON program, tying it directly into an operational seismic-data infrastructure rather than being a standalone research script.

## Details

- **Interface:** CLI (three console scripts: `dasconv`, `dasmetadata`, `dasws`) plus a Python library (e.g. a `TDMS` class for use in custom scripts); `dasws` also runs as a FastAPI-based web service
- **Data formats:** reads TDMS (Silixa) and HDF5 (OptoDAS/Alcatel); writes miniSEED
- **Key dependencies:** obspy, numpy, scipy, h5py, fastapi, uvicorn, pydantic, click, jinja2, sphinx, jsonschema, httpx, tqdm
- **Scope signals:** classified "Production/Stable" in setup.py, supports Python 3.9–3.12, GPLv3+ licensed, 842 commits and 15 releases since June 2019; README notes some features are incomplete (`dasmetadata` "needs to be done", `dasws` QueryAuth "NOT implemented yet")
- **Source visible:** yes — full package source visible (`dastools/app`, `dastools/core.py`, `dastools/server`, `dastools/input`, `dastools/output`, `dastools/partition`, tests, etc.), not just a description
- **Sources read:** https://git.gfz-potsdam.de/geofon/dastools, https://git.gfz-potsdam.de/api/v4/projects/geofon%2Fdastools, https://git.gfz-potsdam.de/geofon/dastools/-/raw/master/README.rst, https://git.gfz-potsdam.de/geofon/dastools/-/raw/master/setup.py, https://git.gfz-potsdam.de/api/v4/projects/geofon%2Fdastools/repository/tree?path=dastools&ref=master
