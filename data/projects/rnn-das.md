---
curated:
  id: rnn-das
  name: RNN-DAS
  repository: Javier-FernandezCarabantes/RNN-DAS
  repository_url: https://github.com/Javier-FernandezCarabantes/RNN-DAS
  homepage: null
  description: Recurrent-network detection and real-time monitoring of volcano-seismic signals on DAS.
  status: included
  decision_reason: Reusable DAS detection application under GPL-3.0, shipped with trained model weights
    and a runnable interface.
  primary_category: machine-learning-detection
  capabilities:
  - detection
  - machine-learning
  - phase-picking
  - seismology
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
  - doi: 10.1029/2025jb031756
    role: canonical
    note: null
collected:
  scanned_at: '2026-08-18T06:39:06+00:00'
  snapshot: '2026-08-17'
  visibility: public
  language: Jupyter Notebook
  stars: 4
  forks: 0
  contributors: 1
  releases: 3
  commits: 172
  last_commit_at: '2026-07-06T17:01:31Z'
  created_at: '2025-01-30T12:10:19Z'
  latest_release_at: '2025-09-18T13:58:36Z'
  archived: false
  lines_of_code_estimate: 2541
  loc_basis: language bytes / 32, notebooks excluded
  canonical_citations: 5
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
  ran_at: 2026-08-20 08:16:37+00:00
  duration_seconds: 33.1
  turns: 4
  input_tokens: 19135
  output_tokens: 2321
  cache_read_tokens: 143309
  cache_write_tokens: 8427
  total_tokens: 173192
  api_list_cost_usd: 0.1389
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

# RNN-DAS

Source: [Javier-FernandezCarabantes/RNN-DAS](https://github.com/Javier-FernandezCarabantes/RNN-DAS)

## Summary

RNN-DAS is a Python command-line tool that applies a recurrent neural network (LSTM) to Distributed Acoustic Sensing data to detect and classify volcano-seismic events. The model was trained on Volcano-Tectonic (VT) event waveforms recorded during the 2021 La Palma eruption and reportedly achieves ~97% classification accuracy across more than 2 million waveforms. It is aimed at seismologists and DAS researchers studying volcanic activity who need to pick, track, and classify VT-type events from strain or strain-rate DAS records, rather than at general DAS signal-processing users. What distinguishes it from a generic DAS toolkit is that it ships a pretrained, task-specific LSTM classifier (with frequency-based signal-energy features) rather than general filtering, denoising, or array-processing utilities, and it is scoped narrowly to VT-event detection/classification for volcano monitoring, with claims of generalizing to other volcanic settings with minimal retraining.

## Details

- **Interface:** CLI (`python RNN-DAS.py --files_id files.txt`, with flags like `--model_path`, `--data_folder`, `--n_cpu`); an example Jupyter notebook is also included
- **Data formats:** Input is HDF5 files (2D channel × time-sample strain/strain-rate matrix with `dt_s`, `dx_m`, `begin_time` attributes), referenced via a text file listing event IDs; output includes CSV pick/prediction files and MiniSEED waveforms
- **Key dependencies:** TensorFlow/Keras (LSTM model), joblib (parallelization), ObsPy (MiniSEED I/O); exact versions are listed in `requirements/requirements_RNN_DAS.txt` and `requirements/RNN_DAS.yml` but not stated inline in the README
- **Scope signals:** Includes a pretrained model, an accompanying research paper PDF, example data/images, and GPL-3.0 licensing; built around one specific dataset (2021 La Palma VT events) and optional NVIDIA CUDA 9.0 GPU support, suggesting a research-grade, single-purpose tool rather than a general platform
- **Source visible:** Yes — full source is published, including `RNN-DAS.py`, a `model/` directory, and a `scripts/` directory
- **Sources read:** https://github.com/Javier-FernandezCarabantes/RNN-DAS, https://raw.githubusercontent.com/Javier-FernandezCarabantes/RNN-DAS/main/README.md
