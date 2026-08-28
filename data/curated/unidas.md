---
id: unidas
name: unidas
repository: DASDAE/unidas
repository_url: https://github.com/DASDAE/unidas
homepage: null
description: Compatibility adapters between DAS library data structures.
status: included
decision_reason: Reusable DAS interoperability package under the MIT license.
primary_category: interoperability
capabilities:
- data-model
- interoperability
license_spdx: MIT
license_class: osi-approved
forge:
  kind: github
  host: github.com
registries:
  pypi:
  - unidas
  conda: []
  julia: []
publications: []
das_focus: das-native
sources:
- github.com/dasdae/unidas
reviewed_at: '2026-08-28'
provenance:
  agent: das-summarizer
  models:
  - claude-haiku-4-5-20251001
  - claude-sonnet-5
  ran_at: '2026-08-20T08:17:38+00:00'
  duration_seconds: 29.0
  turns: 4
  input_tokens: 8098
  output_tokens: 1988
  cache_read_tokens: 143100
  cache_write_tokens: 8289
  total_tokens: 161475
  api_list_cost_usd: 0.1231
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

## Summary

Unidas is a lightweight Python compatibility layer that lets distributed acoustic sensing (DAS) libraries interoperate without manual data conversion. Rather than being a DAS toolkit itself, it provides an `@adapter()` decorator and a `convert()` function that translate data structures automatically between four established DAS libraries: DASCore, DASPy, Lightguide, and Xdas. This targets package authors and researchers who want to call functions written against one library's data model while working in another, avoiding duplicated conversion glue code across the fragmented DAS software ecosystem. It is deliberately minimal — implemented in a single source file with NumPy as its only hard dependency — so it can be vendored directly into other projects rather than pulled in as a heavyweight dependency. It does not process raw fiber-optic sensor files itself; it operates on the in-memory data structures already produced by the libraries it bridges.

## Details

- **Interface:** library (no CLI, GUI, or notebook interfaces found)
- **Data formats:** not stated — unidas converts between in-memory data structures of DASCore, DASPy, Lightguide, and Xdas rather than reading/writing specific file formats
- **Key dependencies:** NumPy (hard requirement); DASCore, DASPy, Lightguide, and Xdas are optional, installed via `pip install "unidas[extras]"`
- **Scope signals:** small/early-stage project — 2 stars, 1 fork, 4 watchers, 13 commits on main, 0 open issues/PRs; MIT licensed; requires Python 3.11+; core implementation is a single file (`src/unidas.py`) intended to be vendorable; aimed at DAS package developers rather than end users
- **Source visible:** yes — `src/`, `test/`, and `static/` directories are present in the repository
- **Sources read:** https://github.com/DASDAE/unidas, https://raw.githubusercontent.com/DASDAE/unidas/main/README.md
