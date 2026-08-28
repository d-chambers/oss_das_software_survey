---
curated:
  id: cqi-das
  name: cqi_das
  repository: B-CSI/cqi_das
  repository_url: https://github.com/B-CSI/cqi_das
  homepage: null
  description: Automatic channel-quality scoring for distributed acoustic sensing arrays.
  status: included
  decision_reason: Reusable DAS-specific quality-assessment package explicitly licensed under LGPL-3.0.
  primary_category: processing
  capabilities:
  - machine-learning
  - processing
  - quality-control
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
collected:
  scanned_at: '2026-08-28T12:54:46+00:00'
  snapshot: '2026-08-28'
  visibility: public
  language: Jupyter Notebook
  stars: 11
  forks: 0
  contributors: 2
  releases: 0
  commits: 44
  last_commit_at: '2025-10-21T08:52:48Z'
  created_at: '2025-01-15T21:12:38Z'
  archived: false
  lines_of_code_estimate: 3327
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
  ran_at: 2026-08-20 08:07:39+00:00
  duration_seconds: 21.1
  turns: 3
  input_tokens: 6709
  output_tokens: 1516
  cache_read_tokens: 98439
  cache_write_tokens: 13906
  total_tokens: 120570
  api_list_cost_usd: 0.1383
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

# cqi_das

Source: [B-CSI/cqi_das](https://github.com/B-CSI/cqi_das)

## Summary

cqi_das is a Python module for detecting and classifying channel quality in distributed acoustic sensing (DAS) data recorded on submarine fiber-optic cables. It provides an automated quality-prediction function, `calculate_cqi`, that scores channels using a trained machine-learning classifier, alongside an interactive `ChannelSelector` GUI for manual labeling of channel quality. The tool is aimed at researchers and engineers working with submarine cable DAS deployments who need to separate high-quality acoustic channels from noisy or unusable ones across long cable distances, a task that is otherwise done by eye. The authors note the model was trained and validated specifically on submarine cable data, and performance degrades on land-based DAS segments, distinguishing it from a general-purpose DAS quality-control toolkit.

## Details

- **Interface:** library (core Python module), with a matplotlib-based interactive GUI (`ChannelSelector`) for manual labeling and an interactive threshold-adjustment plot within `calculate_cqi`
- **Data formats:** input as pandas DataFrames (channels as columns, time samples as rows); output as pandas Series of quality probabilities or binary classifications; an HDF5 (.h5) example dataset is provided
- **Key dependencies:** pandas, matplotlib, scikit-learn, joblib, SHAP
- **Scope signals:** small project (11 stars, 44 commits on main), LGPL-3.0 licensed, no open issues/PRs; explicitly scoped to submarine cable DAS, with stated reduced accuracy on land segments; includes internal notebooks for feature extraction and model validation
- **Source visible:** yes — functional Python code is present in the `cqi_das/` directory, plus supporting notebooks in `internal_docs/`
- **Sources read:** https://github.com/B-CSI/cqi_das
