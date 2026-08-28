---
curated:
  id: daslab
  name: DASLab
  repository: yohanesnuwara/DASLab
  repository_url: https://github.com/yohanesnuwara/DASLab
  homepage: null
  description: Signal-processing and analysis routines for DAS fiber-optic data.
  status: included
  decision_reason: Reusable DAS-specific Python library with GPL-3.0 licensing and an archived release.
  primary_category: processing
  capabilities:
  - io
  - processing
  - visualization
  license_spdx: GPL-3.0-only
  license_class: osi-approved
  forge:
    kind: github
    host: github.com
  registries:
    pypi: []
    conda: []
    julia: []
  publications:
  - doi: 10.5281/zenodo.5797215
    role: canonical
    note: null
collected:
  scanned_at: '2026-08-18T06:37:48+00:00'
  snapshot: '2026-08-17'
  visibility: public
  language: Jupyter Notebook
  stars: 77
  forks: 24
  contributors: 1
  releases: 1
  commits: 117
  last_commit_at: '2025-08-30T08:32:19Z'
  created_at: '2021-05-09T05:00:00Z'
  latest_release_at: '2021-12-22T04:10:14Z'
  archived: false
  lines_of_code_estimate: 2208
  loc_basis: language bytes / 32, notebooks excluded
  canonical_citations: 1
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
  ran_at: 2026-08-20 08:12:11+00:00
  duration_seconds: 28.1
  turns: 4
  input_tokens: 8377
  output_tokens: 2199
  cache_read_tokens: 148950
  cache_write_tokens: 2673
  total_tokens: 162199
  api_list_cost_usd: 0.0936
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

# DASLab

Source: [yohanesnuwara/DASLab](https://github.com/yohanesnuwara/DASLab)

## Summary

DASLab is a research toolkit for processing and analyzing Distributed Acoustic Sensing (DAS) fiber-optic data, developed during work with the CO2 Storage Research Group at RITE (Research Institute of Innovative Technology for the Earth) in Japan. It targets researchers working with strain and seismic-wave measurements captured via laser light scattering in fiber-optic cables. Rather than a general signal-processing library, it packages specific DAS workflows as example notebooks: automated P- and S-wave picking (Kurtosis, AIC/BIC, STA/LTA, STFT), waveform comparison between straight and helical cable layouts, signal-to-noise analysis and trace stacking, spectral diagnostics and F-K filtering, earthquake catalog mapping, and detection-capability (detectivity) analysis relative to known earthquakes. It reads TDMS-format DAS recordings and is aimed at seismologists and DAS practitioners applying the technology to reservoir monitoring, infrastructure assessment, and earthquake detection rather than at software engineers building production pipelines.

## Details

- **Interface:** notebook collection (seven Jupyter notebooks) plus a set of standalone Python modules/scripts (`TDMS_Functions.py`, `autopick.py`, `dasplot.py`, `filter.py`, `input_output.py`, `signalprocessing.py`)
- **Data formats:** input is TDMS files (read via npTDMS); output is processed arrays and plots — no specific output file format stated
- **Key dependencies:** npTDMS 0.25.0, ObsPy, Utm
- **Scope signals:** versioned as v1.0.0 with a Zenodo citation/DOI (Nuwara, 2021); presented as a research repository from a specific applied project (CO2 storage monitoring at RITE), not a general-purpose maintained library
- **Source visible:** yes — the repository publishes actual Python source files and notebooks, not just a description
- **Sources read:** https://github.com/yohanesnuwara/DASLab, https://raw.githubusercontent.com/yohanesnuwara/DASLab/main/README.md
