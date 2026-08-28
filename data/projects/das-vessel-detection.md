---
curated:
  id: das-vessel-detection
  name: das-vessel-detection
  repository: UAH-PSI/das-vessel-detection
  repository_url: https://github.com/UAH-PSI/das-vessel-detection
  homepage: null
  description: Vessel detection and localization from distributed acoustic sensing recordings.
  status: included
  decision_reason: Reusable DAS-specific detection system with GPL-3.0 licensing.
  primary_category: application-domain
  capabilities:
  - detection
  - machine-learning
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
  scanned_at: '2026-08-18T06:37:28+00:00'
  snapshot: '2026-08-17'
  visibility: public
  language: Python
  stars: 6
  forks: 1
  contributors: 1
  releases: 0
  commits: 66
  last_commit_at: '2026-08-03T15:08:36Z'
  created_at: '2025-06-05T22:26:24Z'
  archived: false
  lines_of_code_estimate: 14995
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
  ran_at: 2026-08-20 08:11:02+00:00
  duration_seconds: 31.0
  turns: 4
  input_tokens: 11524
  output_tokens: 2440
  cache_read_tokens: 149540
  cache_write_tokens: 2955
  total_tokens: 166459
  api_list_cost_usd: 0.1
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

# das-vessel-detection

Source: [UAH-PSI/das-vessel-detection](https://github.com/UAH-PSI/das-vessel-detection)

## Summary

das-vessel-detection is a research codebase for detecting and localizing surface vessels using distributed acoustic sensing (DAS) on a submarine fiber-optic cable. It processes spatial-spectral DAS features extracted from a 2,553-meter cable segment to classify whether a vessel is present and to regress its distance from the cable, using baseline XGBoost models trained on a published 74,771-sample, 10-day dataset. The intended users are maritime-acoustics and DAS researchers working on ship detection and passive underwater monitoring, particularly those wanting a reproducible baseline tied to a peer-reviewed paper and an accompanying Zenodo dataset. Unlike a general DAS processing toolkit, it is narrowly scoped to one detection task and one dataset, packaging data loading, day-wise cross-validation splitting (to avoid temporal leakage), baseline model training, and result visualization rather than general fiber-sensing signal processing.

## Details

- **Interface:** Python scripts and shell-script experiment launchers (CLI-style); no GUI, web service, or notebook interface
- **Data formats:** HDF5 (primary dataset: feature matrices, distance labels, timestamps, vessel metadata), NumPy `.npy`/`.npz` (partitioned data), CSV (`fbands.csv`, frequency-band definitions), PNG (visualization output)
- **Key dependencies:** numpy, scikit-learn, pandas, h5py, torch, xgboost, lightgbm, mlflow, prefect, shap, imbalanced-learn (per `requirements.txt`)
- **Scope signals:** Small research project (6 stars, 1 fork, no releases); tied to an IEEE JSTARS article (2026) and a Zenodo dataset (DOI 10.5281/zenodo.15611778); repo description marks it as actively under development; authors explicitly disclaim suitability for operational safety use
- **Source visible:** Yes — repository contains actual source (`src/`, `models/`, `scripts/`, `docs/`, plus a demonstration HDF5 data extract), not just a description
- **Sources read:** https://github.com/UAH-PSI/das-vessel-detection, https://raw.githubusercontent.com/UAH-PSI/das-vessel-detection/main/requirements.txt
