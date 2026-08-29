---
id: filark
name: FiLark
repository: Guoguo828/fliark
repository_url: https://github.com/Guoguo828/fliark
homepage: null
description: Streaming-first exploration, annotation, and signal processing for large DAS recordings.
status: included
decision_reason: Reusable DAS-specific Python framework with an MIT license and a packaged module tree.
primary_category: visualization-annotation
capabilities:
- annotation
- processing
- streaming
- visualization
license_spdx: MIT
license_class: osi-approved
forge:
  kind: github
  host: github.com
registries:
  pypi:
  - filark
  conda: []
  julia: []
publications: []
das_focus: das-native
sources:
- github.com/guoguo828/fliark
reviewed_at: '2026-08-28'
provenance:
  agent: das-summarizer
  models:
  - claude-haiku-4-5-20251001
  - claude-sonnet-5
  ran_at: '2026-08-20T08:14:18+00:00'
  duration_seconds: 25.0
  turns: 4
  input_tokens: 8848
  output_tokens: 1793
  cache_read_tokens: 148844
  cache_write_tokens: 2025
  total_tokens: 161510
  api_list_cost_usd: 0.0879
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

## Summary

FiLark (also referred to as "Fiber Lark") is a GUI visualization and analysis tool aimed at Distributed Acoustic/Fiber Optic Sensing (DAS) data, built around VisPy's OpenGL rendering to handle large, streaming DAS arrays that the README says overwhelm conventional plotting workflows. It provides keyboard-driven navigation (pan/zoom, auto-scroll), deterministic low-latency rendering, and lightweight annotation tools for marking and labeling shapes directly on the data. It is intended for researchers and engineers working with high-throughput fiber-optic sensing feeds who need to inspect and annotate large volumes of streaming data rather than static files. The project is explicitly labeled early-stage/experimental, with the README warning that APIs and GUI behavior are still subject to change and some features remain unstabilized.

## Details

- **Interface:** GUI application, launched via a command-line entry point (`filark`)
- **Data formats:** not stated (the `h5py` dependency suggests possible HDF5 handling, but no specific DAS/fiber file format is named in the README)
- **Key dependencies:** numpy, matplotlib, vispy, PySide6, h5py, scipy
- **Scope signals:** Version 0.0.1, README self-describes as early-stage/experimental with changing APIs; repository shows minimal activity (1 commit, 0 stars/forks)
- **Source visible:** yes — repository contains a `/filark` package directory, `pyproject.toml`, `LICENSE`, `README.md`, and `TODO`, not just a description
- **Sources read:** https://github.com/Guoguo828/fliark, https://github.com/Guoguo828/fliark/blob/main/pyproject.toml
