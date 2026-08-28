---
curated:
  id: xpick
  name: Xpick
  repository: xdas-dev/xpick
  repository_url: https://github.com/xdas-dev/xpick
  homepage: null
  description: Web application for manual arrival picking across thousands of DAS channels.
  status: included
  decision_reason: Reusable DAS picking application with GPL-3.0 licensing and an archived release. The
    PyPI name xpick belongs to an unrelated project, so no registry name is declared.
  primary_category: visualization-annotation
  capabilities:
  - annotation
  - phase-picking
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
  publications:
  - doi: 10.5281/zenodo.10678341
    role: canonical
    note: null
collected:
  scanned_at: '2026-08-18T06:39:25+00:00'
  snapshot: '2026-08-17'
  visibility: public
  language: Python
  stars: 5
  forks: 0
  contributors: 1
  releases: 2
  commits: 52
  last_commit_at: '2024-11-15T10:32:31Z'
  created_at: '2024-01-17T13:41:23Z'
  latest_release_at: '2024-09-02T11:38:52Z'
  archived: false
  lines_of_code_estimate: 672
  loc_basis: language bytes / 32, notebooks excluded
  canonical_citations: 0
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
  ran_at: 2026-08-20 08:18:05+00:00
  duration_seconds: 31.3
  turns: 4
  input_tokens: 8927
  output_tokens: 2011
  cache_read_tokens: 143030
  cache_write_tokens: 8217
  total_tokens: 162185
  api_list_cost_usd: 0.1238
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

# Xpick

Source: [xdas-dev/xpick](https://github.com/xdas-dev/xpick)

## Summary

Xpick is a browser-based annotation tool for manually picking seismic phase arrivals on Distributed Acoustic Sensing (DAS) data. It runs as a Bokeh web application, launched from the command line and viewed in a local browser (including on remote machines via port forwarding), and lets a user freely draw arrival picks across 2D time-distance DAS records, making manual picking of thousands of traces tractable. It would be used by seismologists or DAS researchers who need labeled arrival-time data, for example to build training sets or validate automated phase pickers. What sets it apart from a generic plotting or annotation toolkit is that it is purpose-built around the Xdas ecosystem's data model (time/distance arrays) and workflow, with dedicated tools for phase labeling, pick management, and CSV export tailored to seismic picking rather than general-purpose image or time-series annotation.

## Details

- **Interface:** GUI application (Bokeh web app), launched via a CLI command (`xpick <data_paths>`)
- **Data formats:** reads Xdas's native NetCDF format (2D arrays with `time` and `distance` dimensions, built via `da.to_netcdf()` or `xdas.open_mfdatatree()`); writes picks out as CSV
- **Key dependencies:** Xdas, Bokeh, Node.js (>=18, required for the Bokeh/JS frontend build)
- **Scope signals:** small project (repository reported ~52 commits, 5 stars), has a Zenodo DOI (10.5281/zenodo.10678341), GPL-3.0 licensed, installed directly from GitHub (`pip install git+...`) rather than published to PyPI — indicates a research-tool stage rather than a widely adopted package
- **Source visible:** yes, the repository publishes actual implementation code (`xpick/` package), not just a description
- **Sources read:** https://github.com/xdas-dev/xpick, https://raw.githubusercontent.com/xdas-dev/xpick/main/README.md
