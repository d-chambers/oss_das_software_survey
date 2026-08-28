---
id: das-realtime
name: DAS-realtime
repository: Caltech-DASHub/DAS-realtime
repository_url: https://github.com/Caltech-DASHub/DAS-realtime
homepage: null
description: Real-time DAS processing components for operational earthquake monitoring.
status: included
decision_reason: Reusable DAS-specific framework with GPL-3.0 licensing and an operational interface.
primary_category: machine-learning-detection
capabilities:
- machine-learning
- phase-picking
- seismology
- streaming
license_spdx: GPL-3.0-only
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
- github.com/caltech-dashub/das-realtime
reviewed_at: '2026-08-28'
provenance:
  agent: das-summarizer
  models:
  - claude-haiku-4-5-20251001
  - claude-sonnet-5
  ran_at: '2026-08-20T08:08:39+00:00'
  duration_seconds: 26.6
  turns: 4
  input_tokens: 5791
  output_tokens: 1867
  cache_read_tokens: 143102
  cache_write_tokens: 8150
  total_tokens: 158910
  api_list_cost_usd: 0.1192
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

## Summary

DAS-realtime is a Python package for processing distributed acoustic sensing data streams in real time to support earthquake monitoring and early warning operations. It integrates with the Earthworm seismic processing system via PyEarthworm to stream selected DAS channels alongside conventional seismic data, and it relies on EQNet (included as a git submodule) for the underlying detection or picking models. The intended users are seismological network operators and researchers building real-time monitoring pipelines that incorporate DAS alongside traditional seismometers, rather than general DAS data analysts doing offline processing. What distinguishes it from a generic DAS toolkit is its narrow focus on the real-time, operational earthquake-monitoring use case and its direct coupling to the Earthworm system, a specific piece of seismic-network infrastructure, rather than providing broad-purpose DAS file I/O or signal-processing utilities.

## Details

- **Interface:** library (Python package)
- **Data formats:** not stated
- **Key dependencies:** ObsPy, FastAPI, PyEarthworm, Earthworm (external system), EQNet (git submodule)
- **Scope signals:** small, early-stage project (9 stars, 3 forks, 13 commits on main, no releases); tied to a manuscript under review at *Seismological Research Letters* (Biondi, Tepp, Yu, et al., 2025) on real-time DAS processing for earthquake monitoring operations
- **Source visible:** yes, source code is published (Python package under `/python/`, plus `/external/` for the EQNet submodule)
- **Sources read:** https://github.com/Caltech-DASHub/DAS-realtime, https://raw.githubusercontent.com/Caltech-DASHub/DAS-realtime/main/README.md
