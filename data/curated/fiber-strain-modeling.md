---
id: fiber-strain-modeling
name: horizontal-fracture-fiber-strain
repository: Pengchao-He/horizontal-fracture-fiber-strain
repository_url: https://github.com/Pengchao-He/horizontal-fracture-fiber-strain
homepage: null
description: MATLAB strain and strain-rate modeling for horizontal shear fractures observed on monitoring
  fibers.
status: included
decision_reason: Reusable MATLAB modeling library with an MIT license, a documented function guide, and
  a citation file.
primary_category: modeling
capabilities:
- modeling
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
- github.com/pengchao-he/horizontal-fracture-fiber-strain
reviewed_at: '2026-08-28'
provenance:
  agent: das-summarizer
  models:
  - claude-haiku-4-5-20251001
  - claude-sonnet-5
  ran_at: '2026-08-20T08:14:18+00:00'
  duration_seconds: 19.1
  turns: 3
  input_tokens: 5778
  output_tokens: 1315
  cache_read_tokens: 110660
  cache_write_tokens: 1704
  total_tokens: 119457
  api_list_cost_usd: 0.0651
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

## Summary

This is a MATLAB toolkit for modeling static strain and time-dependent strain rates recorded by horizontal monitoring fibers positioned above shear fractures. It discretizes a horizontal fracture plane into rectangular Okada dislocation patches with user-defined slip distributions, then computes the resulting six strain-tensor components and fiber-axis strain at specified fiber depths and time steps. It would be used by geophysicists and researchers modeling distributed acoustic sensing (DAS) responses to subsurface shear-fracture slip, for example to interpret or forward-model fiber strain-rate signals during hydraulic fracturing or fault-slip monitoring. Unlike a generic elastic-dislocation library, it is specifically structured around horizontal fiber geometries and reuses precomputed Green's functions across multi-step slip histories for efficiency, with example datasets and regression tests included.

## Details

- **Interface:** library (MATLAB functions/scripts, no CLI, GUI, or notebooks mentioned)
- **Data formats:** input as MATLAB structures or `.mat` files (patch centers, fracture depth, slip matrices, fiber coordinates); output as MATLAB result files containing strain components, axial strain, and strain-rate data
- **Key dependencies:** base MATLAB only; no special toolbox stated as required for the core solver
- **Scope signals:** includes regression tests and multiple example scripts (`code_main/` for solvers and tests, `code_okada/` for Okada elastic dislocation routines, `input/` for example datasets, `output_*/` for representative results), suggesting a research-grade, tested codebase rather than a polished general-purpose package
- **Source visible:** yes, source code is published in the repository
- **Sources read:** https://github.com/Pengchao-He/horizontal-fracture-fiber-strain
