---
curated:
  id: optodas-processor
  name: OptoDAS_processor
  repository: speleos/OptoDAS_processor
  repository_url: https://github.com/speleos/OptoDAS_processor
  homepage: null
  description: Automated processing workflows for ASN OptoDAS datasets.
  status: included
  decision_reason: Reusable DAS-specific processing tool with GPL-3.0 licensing.
  primary_category: processing
  capabilities:
  - io
  - pipelines
  - processing
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
collected:
  scanned_at: '2026-08-28T12:57:07+00:00'
  snapshot: '2026-08-28'
  visibility: public
  language: Jupyter Notebook
  stars: 0
  forks: 0
  contributors: 1
  releases: 2
  commits: 55
  last_commit_at: '2026-06-11T15:10:38Z'
  created_at: '2026-03-30T16:37:19Z'
  latest_release_at: '2026-04-28T14:08:51Z'
  archived: false
  lines_of_code_estimate: 3944
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
  ran_at: 2026-08-20 08:16:58+00:00
  duration_seconds: 29.0
  turns: 4
  input_tokens: 7805
  output_tokens: 2040
  cache_read_tokens: 148967
  cache_write_tokens: 2523
  total_tokens: 161335
  api_list_cost_usd: 0.0908
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

# OptoDAS_processor

Source: [speleos/OptoDAS_processor](https://github.com/speleos/OptoDAS_processor)

## Summary

OptoDAS_processor is a Python tool suite for automating the processing of OptoDAS distributed acoustic sensing datasets, built on ObsPy for seismic waveform handling. It runs configurable processing chains defined in Python config files (`sources_list.py`, `shared_config.py`) that specify events, time windows, channel selections, and ordered processing steps. The suite targets researchers working with fiber-optic cable acoustic sensing for three specific applications: seismic event analysis and spectrograms, dispersion curve fitting from downsampled HDF5 recordings, and marine bioacoustics (baleen whale detection via template matching, plus whale localization from decimated streams). Unlike a generic DAS toolkit, it is oriented around a specific instrument (OptoDAS) and a specific research program funded under the EU Horizon Europe SUBMERSE project, with example notebooks and whale-locator demonstrations rather than a general-purpose API.

## Details

- **Interface:** Python library, with Jupyter notebook examples (`example/`, `whale_locator_example/`)
- **Data formats:** reads raw DAS data as HDF5 (including 1 Hz downsampled 30-minute HDF5 for dispersion curve fitting); reads and writes miniSEED files; works with ObsPy `Stream` objects internally
- **Key dependencies:** ObsPy (seismic data handling); other standard scientific Python libraries referenced but not itemized in a visible requirements file
- **Scope signals:** small early-stage research codebase (~55 commits, 0 stars/forks/watchers); no releases visible; funded by Horizon Europe (SUBMERSE project) and Portuguese research institutions; structured around specific processing modules (`das_processor`, `dispersion_curves`, `config`, `example`, `whale_locator_example`)
- **Source visible:** yes, source code is published in the repository (not just a description)
- **Sources read:** https://github.com/speleos/OptoDAS_processor, https://raw.githubusercontent.com/speleos/OptoDAS_processor/main/README.md
