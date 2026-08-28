---
curated:
  id: fiber-strain-modeling
  name: horizontal-fracture-fiber-strain
  repository: Pengchao-He/horizontal-fracture-fiber-strain
  repository_url: https://github.com/Pengchao-He/horizontal-fracture-fiber-strain
  homepage: null
  description: MATLAB strain and strain-rate modeling for horizontal shear fractures observed on monitoring
    fibers.
  status: included
  decision_reason: Reusable MATLAB modeling library with an MIT license, a documented function guide,
    and a citation file.
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
collected:
  scanned_at: '2026-08-18T06:38:27+00:00'
  snapshot: '2026-08-17'
  visibility: public
  language: MATLAB
  stars: 0
  forks: 0
  contributors: 1
  releases: 0
  commits: 1
  last_commit_at: '2026-07-19T08:01:55Z'
  created_at: '2026-07-19T08:02:08Z'
  archived: false
  lines_of_code_estimate: 2305
  loc_basis: language bytes / 32, notebooks excluded
  dependencies: []
  has_docs: false
  has_tests: false
  has_ci: false
  unavailable:
    pypi_downloads_total: no free source publishes all-time PyPI totals
    conda_downloads_180d: anaconda.org publishes a cumulative count only, with no time series
summary:
  agent: das-summarizer
  models:
  - claude-haiku-4-5-20251001
  - claude-sonnet-5
  ran_at: 2026-08-20 08:14:18+00:00
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

# horizontal-fracture-fiber-strain

Source: [Pengchao-He/horizontal-fracture-fiber-strain](https://github.com/Pengchao-He/horizontal-fracture-fiber-strain)

## Summary

This is a MATLAB toolkit for modeling static strain and time-dependent strain rates recorded by horizontal monitoring fibers positioned above shear fractures. It discretizes a horizontal fracture plane into rectangular Okada dislocation patches with user-defined slip distributions, then computes the resulting six strain-tensor components and fiber-axis strain at specified fiber depths and time steps. It would be used by geophysicists and researchers modeling distributed acoustic sensing (DAS) responses to subsurface shear-fracture slip, for example to interpret or forward-model fiber strain-rate signals during hydraulic fracturing or fault-slip monitoring. Unlike a generic elastic-dislocation library, it is specifically structured around horizontal fiber geometries and reuses precomputed Green's functions across multi-step slip histories for efficiency, with example datasets and regression tests included.

## Details

- **Interface:** library (MATLAB functions/scripts, no CLI, GUI, or notebooks mentioned)
- **Data formats:** input as MATLAB structures or `.mat` files (patch centers, fracture depth, slip matrices, fiber coordinates); output as MATLAB result files containing strain components, axial strain, and strain-rate data
- **Key dependencies:** base MATLAB only; no special toolbox stated as required for the core solver
- **Scope signals:** includes regression tests and multiple example scripts (`code_main/` for solvers and tests, `code_okada/` for Okada elastic dislocation routines, `input/` for example datasets, `output_*/` for representative results), suggesting a research-grade, tested codebase rather than a polished general-purpose package
- **Source visible:** yes, source code is published in the repository
- **Sources read:** https://github.com/Pengchao-He/horizontal-fracture-fiber-strain
