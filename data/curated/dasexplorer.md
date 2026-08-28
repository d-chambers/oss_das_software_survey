---
id: dasexplorer
name: DASexplorer
repository: sermomon/DASexplorer
repository_url: https://github.com/sermomon/DASexplorer
homepage: https://sermomon.github.io/DASexplorer/
description: Desktop application for DAS visualization, filtering, picking, and annotation.
status: included
decision_reason: Reusable DAS application explicitly licensed under GPL-3.0-or-later.
primary_category: visualization-annotation
capabilities:
- annotation
- desktop-application
- io
- processing
- visualization
license_spdx: GPL-3.0-or-later
license_class: osi-approved
forge:
  kind: github
  host: github.com
registries:
  pypi:
  - dasexplorer
  conda: []
  julia: []
publications: []
das_focus: das-native
sources:
- github.com/sermomon/dasexplorer
reviewed_at: '2026-08-28'
provenance:
  agent: das-summarizer
  models:
  - claude-haiku-4-5-20251001
  - claude-sonnet-5
  ran_at: '2026-08-20T08:11:36+00:00'
  duration_seconds: 25.5
  turns: 4
  input_tokens: 8029
  output_tokens: 1925
  cache_read_tokens: 149780
  cache_write_tokens: 1581
  total_tokens: 161315
  api_list_cost_usd: 0.084
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

## Summary

DASexplorer is a desktop GUI application for loading, visualizing, filtering, and annotating Distributed Acoustic Sensing (DAS) recordings without requiring programming knowledge. It targets researchers and engineers who work with raw DAS data from multiple interrogator hardware vendors (Aragón Photonics HDAS, Silixa iDAS, Luna Innovations OptaSense, ASN OptoDAS) and need to inspect t-x waveform data interactively, apply signal-processing filters (band-pass, F-K, Hilbert envelope), and produce labeled datasets. What differentiates it from a generic seismic or signal viewer is its native support for several vendor-specific DAS interrogator file formats in one interface, plus built-in annotation tooling (bounding boxes, keypoints, lines) with export directly into machine-learning-ready formats such as YOLO and COCO JSON, positioning it as a bridge between raw fiber-optic sensing acquisition and downstream ML labeling workflows.

## Details

- **Interface:** GUI desktop application (PyQt5-based)
- **Data formats:** reads `.bin` (HDAS), `.h5` (OptaSense), `.tdms` (iDAS), `.hdf5` (OptoDAS), `.mat` (MATLAB); exports NPZ, MAT, YOLO, COCO JSON, Raven Pro
- **Key dependencies:** PyQt5, pyqtgraph
- **Scope signals:** small community project — 7 stars, 3 forks, 115 commits, latest release v1.0.3, GPL v3 license, published on PyPI (`pip install dasexplorer`), has a Zenodo DOI for citation, supports Windows/Linux/macOS with Python 3.10+
- **Source visible:** yes — full source present (dasexplorer and dasexplorer-docs folders, setup.py, pyproject.toml, MANIFEST.in)
- **Sources read:** https://github.com/sermomon/DASexplorer, https://sermomon.github.io/DASexplorer/
