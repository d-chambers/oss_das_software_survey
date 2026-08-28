---
id: daseventnet
name: DASEventNet
repository: Tieyuan/DASEventNet
repository_url: https://github.com/Tieyuan/DASEventNet
homepage: null
description: ResNet-based microseismic event detection on DAS arrays.
status: included
decision_reason: Reusable DAS detection model with an MIT license, distributed as scripts rather than
  an installable package.
primary_category: machine-learning-detection
capabilities:
- detection
- machine-learning
- seismology
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
das_focus: das-native
sources:
- github.com/tieyuan/daseventnet
reviewed_at: '2026-08-28'
provenance:
  agent: das-summarizer
  models:
  - claude-haiku-4-5-20251001
  - claude-sonnet-5
  ran_at: '2026-08-20T08:11:36+00:00'
  duration_seconds: 30.9
  turns: 4
  input_tokens: 6392
  output_tokens: 2428
  cache_read_tokens: 149747
  cache_write_tokens: 2037
  total_tokens: 160604
  api_list_cost_usd: 0.0891
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

## Summary

DASEventNet is a deep-learning tool for detecting microseismic events in Distributed Acoustic Sensing (DAS) fiber-optic data, built on a ResNet architecture. It was developed to identify small induced-seismicity signals recorded during the 2022 hydraulic stimulation of the Utah FORGE well 16A (78)-32, using Silixa DAS data and multiple associated event catalogs (Silixa, Geo-Energie Suisse borehole geophones, and a semblance-based catalog from Porras et al. 2024). The intended users are geophysicists and seismologists working on geothermal or oil/gas induced-seismicity monitoring who need automated event detection on large DAS arrays rather than manual picking. Unlike a generic seismic-processing toolkit, it is a research artifact tied to a specific published study and dataset, packaged as a ResNet-based classifier rather than a general DAS analysis library. It accompanies a 2024 JGR: Solid Earth paper and is intended to be cited when used.

## Details

- **Interface:** library (Python module `DASEventNet.py` plus a `resnet50.py` architecture file; no CLI or GUI described)
- **Data formats:** not stated explicitly beyond "DAS fiber" time-series data from the Silixa interrogator used at Utah FORGE; no specific file format (e.g., HDF5/SEG-Y) is named in the README
- **Key dependencies:** matplotlib, numpy, obspy, pandas, scipy, tensorflow
- **Scope signals:** tied to one specific field experiment (Utah FORGE well 16A (78)-32) and one published paper (Yu et al. 2024, JGR Solid Earth); presented as a research/reproducibility artifact rather than a general-purpose or actively maintained package; contact is a single researcher (Pengliang Yu) for questions/bugs/collaboration
- **Source visible:** yes — repository contains actual implementation files (`DASEventNet.py`, `resnet50.py`) and a data folder, not just a description
- **Sources read:** https://github.com/Tieyuan/DASEventNet, https://raw.githubusercontent.com/Tieyuan/DASEventNet/main/README.md
