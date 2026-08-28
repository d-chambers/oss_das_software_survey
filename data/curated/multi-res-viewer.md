---
id: multi-res-viewer
name: MultiResViewer
repository: DASDAE/MultiResViewer
repository_url: https://github.com/DASDAE/MultiResViewer
homepage: null
description: Multi-resolution interactive viewer for large DAS datasets.
status: included
decision_reason: Reusable DAS visualization tool with GPL-3.0 licensing.
primary_category: visualization-annotation
capabilities:
- processing
- visualization
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
das_focus: das-native
sources:
- github.com/dasdae/multiresviewer
reviewed_at: '2026-08-28'
provenance:
  agent: das-summarizer
  models:
  - claude-haiku-4-5-20251001
  - claude-sonnet-5
  ran_at: '2026-08-20T08:16:58+00:00'
  duration_seconds: 62.2
  turns: 11
  input_tokens: 14710
  output_tokens: 6648
  cache_read_tokens: 389128
  cache_write_tokens: 7047
  total_tokens: 417533
  api_list_cost_usd: 0.2333
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

## Summary

MultiResViewer is a small interactive tool for exploring distributed acoustic sensing (DAS) waveform data at multiple resolutions inside a matplotlib figure embedded in a Jupyter notebook. It requires a preprocessing step that downsamples a raw DASCore "spool" into a hierarchy of progressively coarser data folders; the viewer then auto-selects the appropriate resolution level for the currently zoomed time window and re-renders a waterfall plot, letting a user zoom in and out with mouse clicks and keyboard shortcuts ('x' to start a zoom, 'o'/'O' to undo/reset, '+/-/=/_' to adjust color scale) without loading an entire large dataset into memory at once. It would be used by DAS researchers who already work with the DASCore ecosystem and need to browse long, high-channel-count recordings interactively rather than render everything at full resolution. It is a single-author research utility (Dr. Ge Jin) rather than a general-purpose visualization toolkit.

## Details

- **Interface:** notebook-based library (two example Jupyter notebooks; classes `MultiResProcess` for preprocessing and `MultiResViewer` for interactive viewing, driven via a matplotlib figure)
- **Data formats:** not stated explicitly; data is read/written through `dascore.spool`, which handles DAS data as DASCore patches/spools, but no specific file format (e.g., TDMS, HDF5, SEG-Y) is named in the code or README
- **Key dependencies:** `dascore`, `pandas`, `numpy`, `matplotlib`; also imports `proc` and `utils` from a package called `SpoolProcessing`, which is not present in this repository and whose source was not located
- **Scope signals:** README is a single paragraph; repository has 2 stars, 1 fork, 13 commits, no releases or packages, and no documentation beyond the README — indicative of an early-stage, single-author research utility rather than a mature or widely adopted tool
- **Source visible:** yes — the repository publishes working source (`process.py`, `viz.py`) plus two example notebooks, not just a description
- **Sources read:** https://github.com/DASDAE/MultiResViewer, https://raw.githubusercontent.com/DASDAE/MultiResViewer/main/README.md, https://api.github.com/repos/DASDAE/MultiResViewer/contents/, https://raw.githubusercontent.com/DASDAE/MultiResViewer/main/process.py, https://raw.githubusercontent.com/DASDAE/MultiResViewer/main/viz.py, https://api.github.com/repos/DASDAE/MultiResViewer/contents/examples
