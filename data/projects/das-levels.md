---
curated:
  id: das-levels
  name: DAS_levels
  repository: DAS4Whales/DAS_levels
  repository_url: https://github.com/DAS4Whales/DAS_levels
  homepage: null
  description: Conversion of DAS-measured strain into acoustic pressure levels.
  status: included
  decision_reason: Reusable DAS conversion code published with no license file, which grants no reuse
    rights.
  primary_category: processing
  capabilities:
  - bioacoustics
  - processing
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
  scanned_at: '2026-08-28T12:55:06+00:00'
  snapshot: '2026-08-28'
  visibility: public
  language: Python
  stars: 3
  forks: 0
  contributors: 1
  releases: 1
  commits: 17
  last_commit_at: '2025-03-11T21:06:07Z'
  created_at: '2025-03-04T16:04:50Z'
  latest_release_at: '2025-03-11T21:02:45Z'
  archived: false
  lines_of_code_estimate: 1091
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
  ran_at: 2026-08-20 08:08:16+00:00
  duration_seconds: 39.4
  turns: 7
  input_tokens: 10597
  output_tokens: 2773
  cache_read_tokens: 220724
  cache_write_tokens: 9198
  total_tokens: 243292
  api_list_cost_usd: 0.1634
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

# DAS_levels

Source: [DAS4Whales/DAS_levels](https://github.com/DAS4Whales/DAS_levels)

## Summary

DAS_levels is a research code repository accompanying a scientific paper on converting distributed acoustic sensing (DAS) strain measurements into acoustic pressure levels for marine bioacoustics. It implements a four-step workflow — loading and converting interrogator data to strain, temporal/spatial resampling, frequency-wavenumber and bandpass filtering, and time-compensated level estimation — applied to a labeled dataset of fin whale 20 Hz calls. It would be used by bioacoustics researchers studying whale vocalizations recorded on fiber-optic DAS arrays, particularly those already using the DAS4Whales library, on which this code depends extensively. Unlike a generic DAS processing toolkit, it is narrowly scoped to reproducing one paper's received-level analysis rather than providing general-purpose DAS tooling, and pairs with a companion manual annotation tool (DASSourceLocator) and a Zenodo-hosted labeled dataset.

## Details

- **Interface:** not stated as a package or CLI; consists of a single top-level script (`scripts/main_received_levels.py`) plus a `utils/` module (`data_handle.py`, `dsp.py`, `plot.py`)
- **Data formats:** not stated (README describes conversion "to strain" in an interrogator-dependent way but does not name specific file formats)
- **Key dependencies:** DAS4Whales (Python library for DAS marine bioacoustics analysis); no other dependencies stated, and no requirements.txt/pyproject.toml was found in the repository
- **Scope signals:** small research-paper companion repo — only a README, `.gitignore`, `.gitattributes`, and two code directories; no package metadata, tests, or CI found; author Léa Bouffaut, K. Lisa Yang Center for Conservation Bioacoustics, Cornell Lab of Ornithology; licensed CC BY-NC-SA 4.0
- **Source visible:** yes — `scripts/main_received_levels.py` and four files under `utils/` are published in the repository
- **Sources read:** https://github.com/DAS4Whales/DAS_levels, https://raw.githubusercontent.com/DAS4Whales/DAS_levels/main/README.md, https://api.github.com/repos/DAS4Whales/DAS_levels/contents/, https://api.github.com/repos/DAS4Whales/DAS_levels/contents/scripts, https://api.github.com/repos/DAS4Whales/DAS_levels/contents/utils
