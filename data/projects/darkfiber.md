---
curated:
  id: darkfiber
  name: darkfiber
  repository: Sirkraven/darkfiber
  repository_url: https://github.com/Sirkraven/darkfiber
  homepage: null
  description: Slowness-based coherence engine producing auditable DAS event verdicts.
  status: included
  decision_reason: Reusable DAS-specific detection engine under AGPL-3.0-or-later with tests, CI, and
    an archived release.
  primary_category: processing
  capabilities:
  - detection
  - processing
  - seismology
  license_spdx: AGPL-3.0-or-later
  license_class: osi-approved
  forge:
    kind: github
    host: github.com
  registries:
    pypi: []
    conda: []
    julia: []
  publications:
  - doi: 10.5281/zenodo.21383275
    role: canonical
    note: null
collected:
  scanned_at: '2026-08-18T06:36:58+00:00'
  snapshot: '2026-08-17'
  visibility: public
  language: Python
  stars: 0
  forks: 0
  contributors: 1
  releases: 2
  commits: 17
  last_commit_at: '2026-07-22T10:28:06Z'
  created_at: '2026-07-15T12:57:53Z'
  latest_release_at: '2026-07-20T12:30:34Z'
  archived: false
  lines_of_code_estimate: 8930
  loc_basis: language bytes / 32, notebooks excluded
  canonical_citations: 0
  dependencies: []
  has_docs: true
  has_tests: true
  has_ci: true
  unavailable:
    pypi_downloads_total: no free source publishes all-time PyPI totals
    conda_downloads_180d: anaconda.org publishes a cumulative count only, with no time series
summary:
  agent: das-summarizer
  models:
  - claude-haiku-4-5-20251001
  - claude-sonnet-5
  ran_at: 2026-08-20 08:07:39+00:00
  duration_seconds: 23.5
  turns: 3
  input_tokens: 9431
  output_tokens: 1691
  cache_read_tokens: 98441
  cache_write_tokens: 13981
  total_tokens: 123544
  api_list_cost_usd: 0.1431
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

# darkfiber

Source: [Sirkraven/darkfiber](https://github.com/Sirkraven/darkfiber)

## Summary

darkfiber is a physics-based earthquake detection system for distributed acoustic sensing (DAS) data. Rather than using per-channel machine-learning classifiers, it identifies events by the geometric slope of signals across the fiber: earthquakes show a near-vertical, km/s moveout, vehicles produce diagonal streaks in the 2–40 m/s range, and local transients lack a consistent slope. It targets seismologists, DAS network operators, and earthquake-monitoring teams who need transparent, uncertainty-quantified detections rather than opaque classifier outputs. The project ships both a Python library and a set of console-script CLIs (e.g. `darkfiber-validate`, `darkfiber-quakeflow`, `darkfiber-stanford`) for running detection and validation workflows against Stanford DAS array data and the QuakeFlow DAS dataset. Its documented validation against 16 ground-truth events reports zero false positives across 27 negative controls, framing correctness and honest reporting of uncertainty as an explicit design goal over raw hit rate.

## Details

- **Interface:** library plus CLI (console scripts `darkfiber-validate`, `darkfiber-quakeflow`, `darkfiber-stanford`)
- **Data formats:** HDF5 and NPZ arrays (Stanford DAS format), SEG-Y (converted to NPZ via a provided `convert_stanford_sgy.py` script), QuakeFlow DAS dataset (via Hugging Face Hub), SQLite for event signature catalogs
- **Key dependencies:** Python 3.10+, Pydantic v2, ONNX (optional ML inference), NumPy/SciPy, Hugging Face Hub
- **Scope signals:** Small/early-stage project — 0 stars, 0 forks, 17 commits, but with a full `src/darkfiber/` package layout, a `tests/` suite, and documentation; validation results are reported against a modest 16-event ground-truth set, suggesting research/prototype maturity rather than production deployment; AGPL-3.0-or-later license
- **Source visible:** Yes — repository contains actual source (`src/darkfiber/`), tests, scripts, and docs, not just a description
- **Sources read:** https://github.com/Sirkraven/darkfiber
