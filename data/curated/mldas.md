---
id: mldas
name: MLDAS
repository: ml4science/mldas
repository_url: https://gitlab.com/ml4science/mldas
homepage: null
description: Machine-learning tools for DAS data.
status: included
decision_reason: Reusable DAS machine-learning package under the Lawrence Berkeley National Labs BSD variant,
  an OSI-approved license a forge cannot auto-detect. Catalogued at its GitLab home rather than
  the DAS-RCN GitHub mirror, which is eight commits and a year behind it.
primary_category: machine-learning-detection
capabilities:
- detection
- machine-learning
- processing
license_spdx: BSD-3-Clause-LBNL
license_class: osi-approved
forge:
  kind: gitlab
  host: gitlab.com
registries:
  pypi:
  - mldas
  conda: []
  julia: []
publications: []
das_focus: das-native
sources:
- gitlab.com/ml4science/mldas
- github.com/das-rcn/mldas
reviewed_at: '2026-08-28'
provenance:
  agent: das-summarizer
  models:
  - claude-haiku-4-5-20251001
  - claude-sonnet-5
  ran_at: '2026-08-20T08:14:57+00:00'
  duration_seconds: 77.1
  turns: 14
  input_tokens: 19174
  output_tokens: 5333
  cache_read_tokens: 503688
  cache_write_tokens: 12350
  total_tokens: 540545
  api_list_cost_usd: 0.3077
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

## Summary

MLDAS (Machine Learning for Distributed Acoustic Sensing) is a Python package from Lawrence Berkeley National Laboratory for analyzing DAS data and training machine learning models on it. Its README describes it simply as tools "for studying Distributed Acoustic Sensing (DAS) data and train machine learning algorithms on them," with training invoked via a script (`mldas/train.py`) driven by YAML configuration files specifying hyperparameters like learning rate, batch size, and training depth. Source inspection shows the training pipeline built on PyTorch/torchvision, using `ImageFolder`-style datasets and text label files rather than direct DAS instrument formats, suggesting DAS records are pre-converted into image representations (e.g. spectrograms) before model training. It would suit researchers applying deep learning classification to DAS datasets rather than users needing raw waveform I/O or general seismic processing.

## Details

- **Interface:** library, installed via pip, with a command-line training entry point (`python mldas/train.py configs/multilabel.yaml`)
- **Data formats:** not stated explicitly for raw DAS input; training code observed reads image files via `torchvision.datasets.ImageFolder` plus a plain-text `label.txt` label file
- **Key dependencies:** h5py, hdf5storage, matplotlib, mpi4py, numpy, pillow, pyyaml, scipy, torch, torchvision (from `setup.py`)
- **Scope signals:** small research codebase; primary development and docs are hosted on GitLab (`gitlab.com/ml4science/mldas`, docs at `ml4science.gitlab.io/mldas`), and the `DAS-RCN/mldas` GitHub copy is a mirror that stopped tracking it in 2021; funded by U.S. Department of Energy, developed at LBNL; `setup.py` lists the license as "Proprietary" while the README states a "modified BSD license"
- **Source visible:** yes — full source code is published (`mldas/` package with `datasets`, `models`, `trainers`, `explore`, `production`, `utils` subdirectories, plus `matlab` submodules)
- **Sources read:**
  - https://github.com/DAS-RCN/mldas
  - https://raw.githubusercontent.com/DAS-RCN/mldas/master/README.rst
  - https://raw.githubusercontent.com/DAS-RCN/mldas/master/setup.py
  - https://github.com/DAS-RCN/mldas/tree/master/mldas
  - https://github.com/DAS-RCN/mldas/tree/master/mldas/datasets
  - https://raw.githubusercontent.com/DAS-RCN/mldas/master/mldas/datasets/das.py
