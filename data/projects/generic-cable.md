---
curated:
  id: generic-cable
  name: GenericCable
  repository: subsurface4d/GenericCable
  repository_url: https://github.com/subsurface4d/GenericCable
  homepage: null
  description: Forward and adjoint modeling for fiber-optic cable responses.
  status: included
  decision_reason: Reusable DAS-specific modeling code published with no license file, which grants no
    reuse rights and is recorded as unlicensed rather than excluded.
  primary_category: modeling
  capabilities:
  - inversion
  - modeling
  license_spdx: null
  license_class: unlicensed
  forge:
    kind: github
    host: github.com
  registries:
    pypi: []
    conda: []
    julia: []
  publications: []
collected:
  scanned_at: '2026-08-18T06:38:35+00:00'
  snapshot: '2026-08-17'
  visibility: public
  language: Python
  stars: 22
  forks: 6
  contributors: 1
  releases: 0
  commits: 9
  last_commit_at: '2024-08-07T13:41:21Z'
  created_at: '2023-12-18T15:52:47Z'
  archived: false
  lines_of_code_estimate: 1333
  loc_basis: language bytes / 32, notebooks excluded
  dependencies: []
  has_docs: true
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
  ran_at: 2026-08-20 08:14:50+00:00
  duration_seconds: 40.9
  turns: 7
  input_tokens: 10257
  output_tokens: 2962
  cache_read_tokens: 260466
  cache_write_tokens: 9407
  total_tokens: 283092
  api_list_cost_usd: 0.178
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

# GenericCable

Source: [subsurface4d/GenericCable](https://github.com/subsurface4d/GenericCable)

## Summary

GenericCable is a Python library for modeling and inverting Distributed Acoustic Sensing (DAS) data along optical fiber cables. It represents fiber geometry (including irregular, non-straight layouts) as a "generic cable" object, provides forward modeling of DAS strain-rate response driven by SPECFEM3D seismic wavefield simulations, and supports full-waveform inversion (adjoint-based) to recover subsurface properties from DAS records. It is aimed at geophysicists and seismic researchers doing fiber-optic sensing imaging or monitoring work, particularly those already using SPECFEM3D. Unlike a generic seismic-processing toolkit, it is narrowly scoped to the fiber-to-wavefield coupling geometry problem, and it explicitly does not model physical fiber-subsurface coupling effects, instead treating the excitation as a delta-function pulse in its current version.

## Details

- **Interface:** library (Python package, installed with `pip install .`; usage shown via example scripts/notebooks in an `examples` folder)
- **Data formats:** not stated (README does not specify file formats for DAS or fiber-geometry I/O; forward modeling is tied to SPECFEM3D simulation outputs)
- **Key dependencies:** numpy, scipy, matplotlib, pyproj; forward modeling depends on SPECFEM3D (external simulator, not a Python dependency); built with poetry-core
- **Scope signals:** small, early-stage project — version 0.0.4, single primary author (Haipeng Li), 9 commits on main, 22 stars/6 forks, 2 open issues; README lists explicit physical limitations (no fiber-subsurface coupling, delta-function pulse assumption) and a "planned" (not yet delivered) smart-cable-design feature; acknowledges Stanford Earth Imaging Project (SEP) and Dr. Milad Bader
- **Source visible:** yes — repository contains actual source under `genericcable/`, plus `examples/` and `docs/` directories, not just a description
- **Sources read:** https://github.com/subsurface4d/GenericCable, https://raw.githubusercontent.com/subsurface4d/GenericCable/main/README.md, https://github.com/subsurface4d/GenericCable/tree/main, https://raw.githubusercontent.com/subsurface4d/GenericCable/main/pyproject.toml
