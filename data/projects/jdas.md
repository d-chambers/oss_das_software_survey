---
curated:
  id: jdas
  name: jDAS
  repository: martijnende/jDAS
  repository_url: https://github.com/martijnende/jDAS
  homepage: null
  description: Coherence-based deep-learning denoising for DAS data.
  status: included
  decision_reason: Reusable DAS denoising implementation with an MIT license.
  primary_category: machine-learning-detection
  capabilities:
  - denoising
  - machine-learning
  - processing
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
  scanned_at: '2026-08-28T12:56:55+00:00'
  snapshot: '2026-08-28'
  visibility: public
  language: Python
  stars: 41
  forks: 4
  contributors: 1
  releases: 1
  commits: 6
  last_commit_at: '2022-10-12T17:13:12Z'
  created_at: '2021-08-21T13:35:25Z'
  latest_release_at: '2021-09-08T14:14:43Z'
  archived: false
  lines_of_code_estimate: 748
  loc_basis: language bytes / 32, notebooks excluded
  dependencies: []
  has_docs: true
  has_tests: true
  has_ci: false
  unavailable:
    pypi_downloads_total: no free source publishes all-time PyPI totals
    conda_downloads_180d: anaconda.org publishes a cumulative count only, with no time series
summary:
  agent: das-summarizer
  models:
  - claude-haiku-4-5-20251001
  - claude-sonnet-5
  ran_at: 2026-08-20 08:15:28+00:00
  duration_seconds: 18.1
  turns: 3
  input_tokens: 6128
  output_tokens: 1317
  cache_read_tokens: 110587
  cache_write_tokens: 1611
  total_tokens: 119643
  api_list_cost_usd: 0.0652
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

# jDAS

Source: [martijnende/jDAS](https://github.com/martijnende/jDAS)

## Summary

jDAS is a self-supervised deep learning model for removing noise from distributed acoustic sensing (DAS) recordings. It works by predicting a channel's waveform from its surrounding channels, exploiting the idea that spatio-temporally coherent signals can be interpolated while incoherent noise cannot; this lets it denoise data without needing clean reference waveforms for training. It is aimed at researchers and engineers working with DAS systems, particularly in seismic monitoring and submarine cable sensing, who want to retrain the model on their own datasets to optimize the signal-noise separation for a specific deployment. What distinguishes it from a generic denoising toolkit is this self-supervised, channel-interpolation training scheme tailored specifically to the spatial coherence structure of DAS arrays, rather than a general-purpose signal-processing library. The method is described in a peer-reviewed IEEE publication.

## Details

- **Interface:** library (Python package with a `JDAS` class); example usage is provided via Jupyter notebooks
- **Data formats:** HDF5 (`.h5`) files for input/output
- **Key dependencies:** TensorFlow (≥2.2.0), NumPy, SciPy, Matplotlib, h5py; Jupyter optional for examples
- **Scope signals:** underlying method published in IEEE Transactions on Neural Networks and Learning Systems (2021); documentation hosted on ReadTheDocs; Travis CI integration present; modest adoption (41 GitHub stars, 4 forks) suggesting a research-oriented, niche tool rather than a widely deployed production system
- **Source visible:** yes — source code is present in `/jDAS`, `/models`, `/examples`, and `/test` directories, not just a description
- **Sources read:** https://github.com/martijnende/jDAS
