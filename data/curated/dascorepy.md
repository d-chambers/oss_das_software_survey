---
id: dascorepy
name: dascorepy
repository: DASDAE/dascorepy
repository_url: https://github.com/DASDAE/dascorepy
homepage: null
description: Conversion bridge between DASCore and DASPy data structures.
status: included
decision_reason: Reusable DAS interoperability package with an MIT license.
primary_category: interoperability
capabilities:
- data-model
- interoperability
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
- github.com/dasdae/dascorepy
reviewed_at: '2026-08-28'
provenance:
  agent: das-summarizer
  models:
  - claude-haiku-4-5-20251001
  - claude-sonnet-5
  ran_at: '2026-08-20T08:11:02+00:00'
  duration_seconds: 28.8
  turns: 6
  input_tokens: 6581
  output_tokens: 2440
  cache_read_tokens: 143232
  cache_write_tokens: 8920
  total_tokens: 161173
  api_list_cost_usd: 0.1287
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

## Summary

dascorepy is a small Python library that bridges the DASCore distributed acoustic sensing (DAS) toolkit with DASPy, a separate seismic signal-processing package. It adds a `patch.daspy` namespace to DASCore's `Patch` objects, exposing DASPy algorithms — such as common-mode noise removal, curvelet denoising, channel-quality checking, and FK-domain or curvelet-based strain/strain-rate conversion — for operations DASCore itself does not already implement. It is aimed at researchers already using DASCore who want access to specific DASPy signal-processing routines without switching data structures or workflows. What distinguishes it from a generic toolkit is its narrow scope: it does not reimplement DAS processing itself but acts strictly as an adapter layer, converting between DASCore `Patch` and DASPy `Section` objects and forwarding to DASPy's algorithms.

## Details

- **Interface:** library (Python package, installed via `uv pip install dascorepy`)
- **Data formats:** not stated (operates on in-memory DASCore `Patch` objects and DASPy `Section` objects, not specific file formats)
- **Key dependencies:** DASCore, DASPy
- **Scope signals:** very early-stage — repository has 5 commits and 0 stars/watchers/forks; README covers only 9 namespace methods and basic install/usage instructions; MIT licensed
- **Source visible:** yes, source code is published in the repository (not just a description)
- **Sources read:** https://github.com/DASDAE/dascorepy, https://raw.githubusercontent.com/DASDAE/dascorepy/main/README.md
