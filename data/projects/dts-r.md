---
curated:
  id: dts-r
  name: dts
  repository: jkennel/dts
  repository_url: https://github.com/jkennel/dts
  homepage: null
  description: R tools for reading and exploring distributed temperature sensing datasets.
  status: watchlist
  decision_reason: The only R package found in this domain, but the modality is distributed temperature
    sensing rather than DAS, and no license file is published.
  primary_category: data-management
  capabilities:
  - data-management
  - io
  - temperature-sensing
  license_spdx: null
  license_class: unlicensed
  forge:
    kind: github
    host: github.com
  registries:
    pypi: []
    conda: []
    julia: []
  publications: []
collected:
  scanned_at: '2026-08-28T12:56:23+00:00'
  snapshot: '2026-08-28'
  visibility: public
  language: HTML
  stars: 3
  forks: 1
  contributors: 3
  releases: 0
  commits: 126
  last_commit_at: '2025-11-07T21:09:01Z'
  created_at: '2021-09-01T14:00:34Z'
  archived: false
  lines_of_code_estimate: 188739
  loc_basis: language bytes / 32, notebooks excluded
  dependencies: []
  has_docs: false
  has_tests: true
  has_ci: true
  unavailable:
    pypi_downloads_total: no free source publishes all-time PyPI totals
    conda_downloads_180d: anaconda.org publishes a cumulative count only, with no time series
summary:
  agent: das-summarizer
  models:
  - claude-haiku-4-5-20251001
  - claude-sonnet-5
  ran_at: 2026-08-20 08:13:02+00:00
  duration_seconds: 23.3
  turns: 4
  input_tokens: 6022
  output_tokens: 1729
  cache_read_tokens: 148725
  cache_write_tokens: 2158
  total_tokens: 158634
  api_list_cost_usd: 0.0838
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

# dts

Source: [jkennel/dts](https://github.com/jkennel/dts)

## Summary

`dts` is an R package for reading, writing, and analyzing distributed temperature sensing (DTS) data from borehole deployments. It targets researchers in hydrogeology or geothermal monitoring who need to process raw DTS instrument output (XML files) into usable datasets and automated reports, via a `generate_report()` function that takes a directory of DTS files and produces report output. Unlike a generic time-series or sensor-data toolkit, it is purpose-built around the specific file structures and processing needs of borehole DTS equipment, and links in compiled C++ code (via Rcpp/RcppArmadillo/RcppParallel) alongside R-level tooling for fast columnar I/O (arrow, fst, duckdb) and statistical modeling (glmnet). The README explicitly marks the project "under construction," indicating it is an early-stage, narrowly-scoped research tool rather than a polished general-purpose package.

## Details

- **Interface:** library (R package, installed via `remotes::install_github`)
- **Data formats:** reads DTS XML files (instrument output); no other formats explicitly stated
- **Key dependencies:** Rcpp, RcppArmadillo, RcppParallel (compiled core), XML, data.table, arrow, fst, duckdb, DBI, glmnet, hydrorecipes, purrr, stringi, anytime/fasttime
- **Scope signals:** README states the project is "under construction"; repository has 126 commits, only 3 stars and 1 fork, zero open issues/PRs — an early-stage, low-adoption research tool
- **Source visible:** yes, source code is published (includes an R `src/` directory with compiled code, consistent with the Rcpp/RcppArmadillo dependencies)
- **Sources read:** https://github.com/jkennel/dts, https://raw.githubusercontent.com/jkennel/dts/master/DESCRIPTION
