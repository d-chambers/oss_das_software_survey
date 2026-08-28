---
curated:
  id: das-metadata
  name: DAS metadata tools
  repository: DAS-RCN/DAS_metadata
  repository_url: https://github.com/DAS-RCN/DAS_metadata
  homepage: null
  description: Community tools and examples for standardizing DAS metadata.
  status: included
  decision_reason: Reusable DAS metadata tooling. The detected CC BY license is a content license that
    does not clearly establish reuse terms for the code, so the class is unknown rather than open.
  primary_category: interoperability
  capabilities:
  - interoperability
  - metadata
  license_spdx: CC-BY-4.0
  license_class: unknown
  forge:
    kind: github
    host: github.com
  registries:
    pypi: []
    conda: []
    julia: []
  publications:
  - doi: 10.1785/0220230325
    role: canonical
    note: null
collected:
  scanned_at: '2026-08-18T06:37:08+00:00'
  snapshot: '2026-08-17'
  visibility: public
  stars: 32
  forks: 4
  contributors: 1
  releases: 0
  commits: 215
  last_commit_at: '2025-02-24T00:14:29Z'
  created_at: '2022-08-23T23:47:50Z'
  archived: false
  canonical_citations: 13
  dependencies: []
  has_docs: false
  has_tests: false
  has_ci: true
  unavailable:
    pypi_downloads_total: no free source publishes all-time PyPI totals
    conda_downloads_180d: anaconda.org publishes a cumulative count only, with no time series
summary:
  agent: das-summarizer
  models:
  - claude-haiku-4-5-20251001
  - claude-sonnet-5
  ran_at: 2026-08-20 08:08:25+00:00
  duration_seconds: 30.9
  turns: 5
  input_tokens: 15977
  output_tokens: 2044
  cache_read_tokens: 181823
  cache_write_tokens: 8374
  total_tokens: 208218
  api_list_cost_usd: 0.1443
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

# DAS metadata tools

Source: [DAS-RCN/DAS_metadata](https://github.com/DAS-RCN/DAS_metadata)

## Summary

DAS metadata tools (DAS-RCN/DAS_metadata) is a documentation project that defines a standardized reporting format for describing distributed acoustic sensing (DAS) experiments, covering five components: interrogator, data acquisition, channels, cable, and fiber characteristics. It is aimed at DAS researchers and data managers who need to document experiment setups consistently so that datasets from different deployments can be compared and integrated, in line with FAIR data principles. Rather than software that processes data, it provides terms and definitions, attribute templates, and an example gallery showing how to fill out the metadata for various deployment scenarios, with JSON recommended as the file format for recording the metadata. What distinguishes it from a generic data-management toolkit is its narrow, DAS-specific schema of experiment attributes rather than any general-purpose functionality. The repository is archived; development has moved to an FDSN DAS metadata repository.

## Details

- **Interface:** not applicable — this is a documentation/schema standard, not software (no library, CLI, GUI, or notebooks)
- **Data formats:** JSON (recommended format for recording the metadata standard, per the template README); no DAS instrument data formats such as miniSEED or HDF5/TDMS are mentioned
- **Key dependencies:** not stated
- **Scope signals:** repository archived on 2025-02-24; final release v1.1.0 dated 2023-09-21; maintainers direct users to the FDSN DAS metadata repository for ongoing work; licensed under CC BY 4.0
- **Source visible:** the repository publishes markdown documentation and one example JSON template (`template/example_poro.json`), but no executable source code — it is a specification/standard, not a software artifact
- **Sources read:** https://github.com/DAS-RCN/DAS_metadata, https://github.com/DAS-RCN/DAS_metadata/tree/master/template
