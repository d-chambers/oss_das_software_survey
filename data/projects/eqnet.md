---
curated:
  id: eqnet
  name: EQNet / PhaseNet-DAS
  repository: AI4EPS/EQNet
  repository_url: https://github.com/AI4EPS/EQNet
  homepage: null
  description: Deep-learning earthquake detection and phase picking with DAS support.
  status: included
  decision_reason: Reusable DAS phase-picking and detection models under a custom academic/commercial
    license, which is source-available rather than OSI-approved.
  primary_category: machine-learning-detection
  capabilities:
  - detection
  - machine-learning
  - phase-picking
  - seismology
  license_spdx: LicenseRef-Academic-Commercial
  license_class: source-available
  forge:
    kind: github
    host: github.com
  registries:
    pypi: []
    conda: []
    julia: []
  publications: []
collected:
  scanned_at: '2026-08-28T12:56:27+00:00'
  snapshot: '2026-08-28'
  visibility: public
  language: Jupyter Notebook
  stars: 56
  forks: 19
  contributors: 4
  releases: 1
  commits: 265
  last_commit_at: '2026-08-18T06:44:45Z'
  created_at: '2022-07-18T21:30:56Z'
  latest_release_at: '2023-10-26T07:25:18Z'
  archived: false
  lines_of_code_estimate: 21334
  loc_basis: language bytes / 32, notebooks excluded
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
  ran_at: 2026-08-20 08:13:36+00:00
  duration_seconds: 47.8
  turns: 10
  input_tokens: 21117
  output_tokens: 3887
  cache_read_tokens: 305552
  cache_write_tokens: 4910
  total_tokens: 335466
  api_list_cost_usd: 0.1875
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

# EQNet / PhaseNet-DAS

Source: [AI4EPS/EQNet](https://github.com/AI4EPS/EQNet)

## Summary

EQNet (also referred to as PhaseNet-DAS in its DAS-specific variant) is a PyTorch-based toolkit of neural network models for automated seismic phase picking, developed by the AI4EPS research group. It bundles several related model architectures — PhaseNet for arrival-time picking, PhaseNet+ for picking with polarity, PhaseNet-TF for deep earthquakes, and PhaseNet-DAS specifically adapted to pick phases from distributed acoustic sensing fiber-optic data — under one codebase with shared training and prediction scripts. It targets seismologists and researchers processing continuous waveform or DAS strain-rate records who want pretrained deep-learning pickers rather than building detection models from scratch. Unlike a generic signal-processing toolkit, it ships trained weights plus a FastAPI inference service and example notebooks tying the models to a specific published architecture (arXiv:2302.08747), making it closer to a reusable research product than a general DSP library.

## Details

- **Interface:** CLI (`train.py`, `predict.py`) plus a FastAPI web service (`app.py`, exposing `POST /predict` and `GET /healthz`); Jupyter notebooks (`docs/phasenet_das.ipynb`, `docs/phasenet_plus.ipynb`) for examples
- **Data formats:** miniSEED (mseed) for standard seismic waveforms; DAS example/demo data loaded from HDF5; not stated whether other DAS-specific formats (e.g. SEG-Y, TDMS) are supported
- **Key dependencies:** torch, torchvision, numpy, scipy, h5py, obspy, pandas, matplotlib, tqdm, fsspec
- **Scope signals:** research-project scale — 56 stars, 19 forks, 265 commits, 8 open issues; tied to a specific arXiv paper (2302.08747) for the DAS model; documentation built with mkdocs
- **Source visible:** yes — full source (`eqnet` package, training/prediction scripts, FastAPI app, notebooks) is published in the repository
- **Sources read:** https://github.com/AI4EPS/EQNet, https://github.com/AI4EPS/EQNet/tree/main, https://github.com/AI4EPS/EQNet/blob/main/requirements.txt, https://github.com/AI4EPS/EQNet/tree/main/docs, https://github.com/AI4EPS/EQNet/blob/main/app.py
