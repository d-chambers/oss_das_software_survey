---
curated:
  id: fiberwatch-cli
  name: FiberWatch CLI
  repository: theBlackfish01/FiberWatchCLI
  repository_url: https://github.com/theBlackfish01/FiberWatchCLI
  homepage: null
  description: Command-line training and evaluation of fault and event models for OTDR and DAS traces.
  status: included
  decision_reason: Reusable command-line toolkit for fiber-sensing data with an MIT license.
  primary_category: machine-learning-detection
  capabilities:
  - detection
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
  scanned_at: '2026-08-28T12:56:41+00:00'
  snapshot: '2026-08-28'
  visibility: public
  language: Jupyter Notebook
  stars: 8
  forks: 0
  contributors: 1
  releases: 0
  commits: 183
  last_commit_at: '2026-08-09T12:32:59Z'
  created_at: '2025-07-06T20:49:28Z'
  archived: false
  lines_of_code_estimate: 71774
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
  ran_at: 2026-08-20 08:14:18+00:00
  duration_seconds: 21.6
  turns: 3
  input_tokens: 11132
  output_tokens: 1707
  cache_read_tokens: 110626
  cache_write_tokens: 1940
  total_tokens: 125405
  api_list_cost_usd: 0.0759
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

# FiberWatch CLI

Source: [theBlackfish01/FiberWatchCLI](https://github.com/theBlackfish01/FiberWatchCLI)

## Summary

FiberWatchCLI is a command-line toolkit for training, evaluating, and explaining machine learning models applied to fiber optic fault detection. It targets two sensing modalities: classic OTDR reflectometry, which produces 1-D amplitude traces, and Φ-OTDR/DAS, which produces time-channel backscatter matrices. Beyond detection and fault localization, the toolkit generates natural-language explanations of model outputs using LLM integration, optionally grounded with retrieval-augmented generation over a reference corpus. Likely users are researchers or engineers evaluating anomaly-detection models (GRU-AE, TCN, TST, CNN, TFT) on fiber-sensing data who also want interpretable, text-based summaries of predictions rather than raw metrics alone. What sets it apart from a generic ML toolkit is the explicit pairing of a DAS/OTDR-specific data and modeling pipeline with an LLM-based explanation layer, including composite visual "LLM sheets" combining plots and probability distributions.

## Details

- **Interface:** CLI (Python, argparse/Click-based subcommands for training, evaluation, and inference)
- **Data formats:** OTDR — 1-D amplitude traces in CSV with scalar metadata (SNR, position estimates); Φ-OTDR/DAS — time-channel matrices in `.mat` files representing normalized backscatter intensity
- **Key dependencies:** PyTorch, Click/argparse, Pinecone (RAG vector store), OpenAI embeddings/vision models, NumPy, scikit-learn, Matplotlib
- **Scope signals:** small project (8 GitHub stars, 0 forks, 183 commits); organized into separate `OTDR_CLI/` and `PHI-OTDR/` tracks; documentation covers experimental protocols, ablations, and zero-/few-shot extensions; MIT licensed; includes protocol locks and SHA-256 sidecars for data integrity, suggesting research-grade rather than production-grade maturity
- **Source visible:** yes — full implementation present (model classes, data handlers, training loops, evaluation metrics, RAG/corpus infrastructure, Jupyter notebooks, `requirements.txt`)
- **Sources read:** https://github.com/theBlackfish01/FiberWatchCLI
