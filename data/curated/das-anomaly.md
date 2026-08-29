---
id: das-anomaly
name: das-anomaly
repository: DASDAE/das-anomaly
repository_url: https://github.com/DASDAE/das-anomaly
homepage: null
description: Anomaly-detection methods and workflows for DAS datasets.
status: included
decision_reason: Reusable DAS-specific package explicitly licensed under LGPL-3.0.
primary_category: machine-learning-detection
capabilities:
- anomaly-detection
- machine-learning
- processing
license_spdx: LGPL-3.0-only
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
- github.com/dasdae/das-anomaly
reviewed_at: '2026-08-28'
provenance:
  agent: das-summarizer
  models:
  - claude-haiku-4-5-20251001
  - claude-sonnet-5
  ran_at: '2026-08-20T08:08:02+00:00'
  duration_seconds: 34.0
  turns: 4
  input_tokens: 10944
  output_tokens: 2418
  cache_read_tokens: 143097
  cache_write_tokens: 8869
  total_tokens: 165328
  api_list_cost_usd: 0.1321
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

## Summary

das-anomaly is a Python package for detecting anomalies in distributed acoustic sensing (DAS) data using an unsupervised, autoencoder-based deep learning workflow. It converts raw DAS data into power spectral density (PSD) images, trains a convolutional autoencoder to reconstruct "normal" PSD patterns, and flags segments with high reconstruction error (MSE) and density-score deviation as anomalies. It targets DAS researchers and engineers who need to screen large continuous acquisitions for unusual signals (e.g., equipment faults, unexpected events) without labeled training data beyond a small manually curated anomaly set. Unlike a generic anomaly-detection toolkit, it is purpose-built around DAS data ingestion via DASCore and a fixed seven-step PSD-to-detection pipeline, with optional MPI-based parallel PSD generation for large datasets. The project explicitly states it is still under development and should be used with caution.

## Details

- **Interface:** library (Python classes/config objects; usage shown via scripts and example Jupyter notebooks; no CLI)
- **Data formats:** input DAS data read through DASCore (specific file formats not stated here); intermediate/output are PSD images in RGB format
- **Key dependencies:** DASCore, TensorFlow, scikit-learn, matplotlib; optional MPI4Py (requires Open MPI)
- **Scope signals:** README states "Still under development. Use with caution"; ~169 commits, 28 GitHub stars, LGPLv3 license, CI/CD and code coverage tracking, Zenodo DOI for citation, supports Python 3.10–3.12
- **Source visible:** yes — repository contains `das_anomaly/` (core library with `psd`, `train`, `detect`, `count` modules), `examples/`, `tests/`, and `docs/figures/`
- **Sources read:** https://github.com/DASDAE/das-anomaly, https://raw.githubusercontent.com/DASDAE/das-anomaly/main/README.md
