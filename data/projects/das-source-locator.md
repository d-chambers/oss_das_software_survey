---
curated:
  id: das-source-locator
  name: DASSourceLocator
  repository: leabouffaut/DASSourceLocator
  repository_url: https://github.com/leabouffaut/DASSourceLocator
  homepage: null
  description: Time-of-arrival annotation and source location tooling for DAS data.
  status: included
  decision_reason: Reusable DAS annotation application published with no license file, which grants no
    reuse rights.
  primary_category: visualization-annotation
  capabilities:
  - annotation
  - processing
  - visualization
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
  scanned_at: '2026-08-28T12:55:25+00:00'
  snapshot: '2026-08-28'
  visibility: public
  language: Python
  stars: 1
  forks: 0
  contributors: 1
  releases: 0
  commits: 16
  last_commit_at: '2024-11-21T19:08:02Z'
  created_at: '2024-11-21T16:57:38Z'
  archived: false
  lines_of_code_estimate: 3060
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
  ran_at: 2026-08-20 08:10:19+00:00
  duration_seconds: 29.6
  turns: 4
  input_tokens: 7264
  output_tokens: 2248
  cache_read_tokens: 149772
  cache_write_tokens: 1553
  total_tokens: 160837
  api_list_cost_usd: 0.0882
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

# DASSourceLocator

Source: [leabouffaut/DASSourceLocator](https://github.com/leabouffaut/DASSourceLocator)

## Summary

DASSourceLocator is a Streamlit-based GUI tool for manually annotating whale calls recorded on distributed acoustic sensing (DAS) fiber-optic arrays. It lets a researcher overlay theoretical time-of-arrival curves onto spatiotemporal DAS data and interactively adjust parameters — the whale's apex location, its offset distance from the cable, arrival time, and which side of the interrogator the source is on — while a cross-correlation scatter plot gives visual feedback on fit quality. Annotations are exported as CSV. It is built by a bioacoustics researcher at Cornell and is tuned specifically for fin whale calls around 20 Hz, tested against three different DAS interrogator systems. This makes it a narrow, domain-specific labeling utility rather than a general DAS signal-processing or visualization toolkit — it assumes the user already has DAS data and is doing manual, human-in-the-loop source localization for marine bioacoustics.

## Details

- **Interface:** GUI application (Streamlit web app), launched via `streamlit run source_locator_app.py`
- **Data formats:** input DAS data format — not stated in the README; output is CSV annotation files
- **Key dependencies:** streamlit, das4whales (a custom GitHub package for marine mammal/whale detection), numpy, scipy, pandas, plotly
- **Scope signals:** small research tool from Dr. Léa Bouffaut's group at Cornell's Bioacoustics Center; README states it was tested across three DAS interrogator systems and is optimized for fin whale calls at ~20 Hz; includes a demo video (`DASSourceLocatorDemo.mp4`); pinned to Python 3.11.9 with a large (155-package) pinned requirements file, suggesting a research-grade rather than production-hardened environment
- **Source visible:** yes — the repository publishes the actual application code (`source_locator_app.py`, `das_SF_locator/` module folder), not just a description
- **Sources read:** https://github.com/leabouffaut/DASSourceLocator, https://raw.githubusercontent.com/leabouffaut/DASSourceLocator/main/requirements_DAS_Locator.txt
