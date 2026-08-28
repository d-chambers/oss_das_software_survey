---
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
das_focus: other-fiber
sources:
- github.com/jkennel/dts
reviewed_at: '2026-08-28'
provenance:
  agent: das-summarizer
  models:
  - claude-haiku-4-5-20251001
  - claude-sonnet-5
  ran_at: '2026-08-20T08:13:02+00:00'
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

## Summary

`dts` is an R package for reading, writing, and analyzing distributed temperature sensing (DTS) data from borehole deployments. It targets researchers in hydrogeology or geothermal monitoring who need to process raw DTS instrument output (XML files) into usable datasets and automated reports, via a `generate_report()` function that takes a directory of DTS files and produces report output. Unlike a generic time-series or sensor-data toolkit, it is purpose-built around the specific file structures and processing needs of borehole DTS equipment, and links in compiled C++ code (via Rcpp/RcppArmadillo/RcppParallel) alongside R-level tooling for fast columnar I/O (arrow, fst, duckdb) and statistical modeling (glmnet). The README explicitly marks the project "under construction," indicating it is an early-stage, narrowly-scoped research tool rather than a polished general-purpose package.

## Details

- **Interface:** library (R package, installed via `remotes::install_github`)
- **Data formats:** reads DTS XML files (instrument output); no other formats explicitly stated
- **Key dependencies:** Rcpp, RcppArmadillo, RcppParallel (compiled core), XML, data.table, arrow, fst, duckdb, DBI, glmnet, hydrorecipes, purrr, stringi, anytime/fasttime
- **Scope signals:** README states the project is "under construction"; repository has 126 commits, only 3 stars and 1 fork, zero open issues/PRs — an early-stage, low-adoption research tool
- **Source visible:** yes, source code is published (includes an R `src/` directory with compiled code, consistent with the Rcpp/RcppArmadillo dependencies)
- **Sources read:** https://github.com/jkennel/dts, https://raw.githubusercontent.com/jkennel/dts/master/DESCRIPTION
