---
curated:
  id: das-sensitivity
  name: DAS_sensitivity
  repository: olfontai/DAS_sensitivity
  repository_url: https://github.com/olfontai/DAS_sensitivity
  homepage: null
  description: Ray-based assessment of DAS directional sensitivity to seismic waves.
  status: included
  decision_reason: Reusable DAS-specific modeling package with an MIT license and importable source modules.
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
  scanned_at: '2026-08-28T12:55:19+00:00'
  snapshot: '2026-08-28'
  visibility: public
  language: Jupyter Notebook
  stars: 3
  forks: 0
  contributors: 1
  releases: 0
  commits: 30
  last_commit_at: '2026-04-30T20:12:36Z'
  created_at: '2025-10-31T14:41:07Z'
  archived: false
  lines_of_code_estimate: 1032
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
  ran_at: 2026-08-20 08:09:25+00:00
  duration_seconds: 34.6
  turns: 5
  input_tokens: 9419
  output_tokens: 2459
  cache_read_tokens: 188717
  cache_write_tokens: 2216
  total_tokens: 202811
  api_list_cost_usd: 0.1068
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

# DAS_sensitivity

Source: [olfontai/DAS_sensitivity](https://github.com/olfontai/DAS_sensitivity)

## Summary

DAS_sensitivity is a Python/Jupyter Notebook package for forward-modeling the amplitude that a distributed acoustic sensing (DAS) array records from a point source, using 3D sensitivity equations derived from ray theory. It computes travel-time grids and predicted along-fiber amplitude, then compares those predictions against measured amplitudes to separate site-amplification effects from fiber-orientation effects and to estimate rescaling factors. It models sources as moment tensors, single forces, or isotropic sources, and represents receivers and ray paths as objects. This is research code aimed at seismologists and DAS-array researchers analyzing single-channel or array-scale fiber sensitivity, rather than a general-purpose DAS processing toolkit — it targets the specific physics problem of why measured DAS amplitudes differ from theoretical predictions along a fiber.

## Details

- **Interface:** Jupyter notebook collection, with supporting Python modules under `/src` providing an object-oriented API (Receiver, Path, Source classes)
- **Data formats:** not stated in the README beyond bundled sample datasets (Brady Hot Springs array geometry/velocity model/measured amplitudes, two synthetic Belgian DAS arrays, a single-channel test case); no explicit file-format names given
- **Key dependencies:** Pykonal (travel-time grid generation, explicitly called out in the README); environment.yml additionally lists numpy, scipy, h5py, matplotlib, pandas, xarray, and obspy
- **Scope signals:** small research repository (README notes 3 stars, ~30 commits), supports a peer-reviewed preprint, includes documented Windows-specific Pykonal install workarounds suggesting active but early-stage development; no CLI or packaging/entry points documented
- **Source visible:** yes — source code (notebooks and `/src` modules) is published in the repository, not just a description
- **Sources read:** https://github.com/olfontai/DAS_sensitivity, https://raw.githubusercontent.com/olfontai/DAS_sensitivity/main/README.md, https://raw.githubusercontent.com/olfontai/DAS_sensitivity/main/environment.yml
