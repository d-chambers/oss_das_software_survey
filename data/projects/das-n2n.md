---
curated:
  id: das-n2n
  name: DAS-N2N-torch
  repository: sachalapins/DAS-N2N-torch
  repository_url: https://github.com/sachalapins/DAS-N2N-torch
  homepage: null
  description: PyTorch implementation of coherence-based Noise2Noise denoising for DAS data.
  status: included
  decision_reason: Reusable DAS denoising package with GPL-3.0 licensing, packaging metadata, and distributed
    model weights.
  primary_category: machine-learning-detection
  capabilities:
  - denoising
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
  scanned_at: '2026-08-28T12:55:10+00:00'
  snapshot: '2026-08-28'
  visibility: public
  language: Python
  stars: 17
  forks: 1
  contributors: 1
  releases: 0
  commits: 32
  last_commit_at: '2026-03-27T10:57:26Z'
  created_at: '2025-01-20T16:23:34Z'
  archived: false
  lines_of_code_estimate: 450
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
  ran_at: 2026-08-20 08:08:33+00:00
  duration_seconds: 39.6
  turns: 6
  input_tokens: 9045
  output_tokens: 2650
  cache_read_tokens: 221666
  cache_write_tokens: 8984
  total_tokens: 242345
  api_list_cost_usd: 0.1607
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

# DAS-N2N-torch

Source: [sachalapins/DAS-N2N-torch](https://github.com/sachalapins/DAS-N2N-torch)

## Summary

DAS-N2N-torch is a PyTorch implementation of a denoising model for Distributed Acoustic Sensing (DAS) signals, based on a peer-reviewed method (DAS-N2N, published in *Geophysical Journal International*) that removes incoherent noise without requiring paired clean training data. Users load pre-trained weights and apply the model to 2D numpy arrays of DAS data through a small Python API (`DASN2N().denoise_numpy(data)`). It targets seismologists and DAS researchers who need to clean raw strain-rate records before downstream event detection or analysis, rather than general signal-processing engineers. What distinguishes it from a generic denoising toolkit is that it packages a specific published self-supervised (Noise2Noise-style) architecture and pre-trained weights for DAS data specifically, with GPU acceleration (CUDA and Apple MPS) and example Jupyter notebooks, instead of offering configurable general-purpose filters.

## Details

- **Interface:** library (Python package with a small class-based API); example Jupyter notebooks included
- **Data formats:** input is 2D numpy arrays of DAS data; no specific file format (e.g., HDF5, TDMS, SEG-Y) stated
- **Key dependencies:** PyTorch (core); optional extras for Jupyter (`pip install dasn2n[jupyter]`) and other example dependencies (`pip install dasn2n[optional]`) — specific package names not stated
- **Scope signals:** small project (17 stars, 1 fork at time of reading); README points to a peer-reviewed publication (Lapins et al., *Geophysical Journal International*, https://doi.org/10.1093/gji/ggad460) and gives the author's contact email for help applying the model to custom DAS data, suggesting a research-grade tool aimed at DAS practitioners rather than a broadly productionized package; no releases or test information visible
- **Source visible:** yes — repository contains the `dasn2n` module, an `examples` directory, and a `data` directory
- **Sources read:** https://github.com/sachalapins/DAS-N2N-torch, https://raw.githubusercontent.com/sachalapins/DAS-N2N-torch/main/README.md, https://github.com/sachalapins/DAS-N2N-torch/blob/main/pyproject.toml
