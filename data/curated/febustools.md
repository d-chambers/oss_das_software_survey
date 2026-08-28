---
id: febustools
name: FebusTools.jl
repository: anowacki/FebusTools.jl
repository_url: https://github.com/anowacki/FebusTools.jl
homepage: null
description: Julia reader and conversion tools for Febus fibre-optic interrogator data.
status: included
decision_reason: Reusable DAS-specific Julia package with an MIT license.
primary_category: data-management
capabilities:
- conversion
- io
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
- github.com/anowacki/febustools.jl
reviewed_at: '2026-08-28'
provenance:
  agent: das-summarizer
  models:
  - claude-haiku-4-5-20251001
  - claude-sonnet-5
  ran_at: '2026-08-20T08:13:36+00:00'
  duration_seconds: 19.9
  turns: 4
  input_tokens: 5911
  output_tokens: 1404
  cache_read_tokens: 142198
  cache_write_tokens: 7728
  total_tokens: 157241
  api_list_cost_usd: 0.1122
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

## Summary

FebusTools.jl is a small Julia library for reading and processing data files produced by Febus fibre-optic sensing equipment, specifically HDF5 output from the Febus A1 distributed acoustic sensing device. It would be used by researchers or engineers working with Febus DAS hardware who need to load raw interrogator output into Julia for downstream analysis, rather than by users seeking a general-purpose DAS toolkit. What distinguishes it from a generic toolkit is its narrow, vendor-specific focus: it targets one manufacturer's HDF5 file layout rather than providing format-agnostic ingestion or processing. The author explicitly describes the code as preliminary and in draft form, with no tests or documentation, offered for use without guarantees of continued maintenance, and states it is not endorsed by Febus.

## Details

- **Interface:** library (Julia package)
- **Data formats:** HDF5 files from the Febus A1 device
- **Key dependencies:** Dates, HDF5, Statistics (from Project.toml `[deps]`)
- **Scope signals:** single contributor, 19 commits, 0 stars/forks, no releases published; author states the code is "preliminary and in draft form, without tests or documentation"; CI and code coverage infrastructure are configured despite the disclaimed lack of tests
- **Source visible:** yes — repository contains `src/`, `test/`, and `docs/` directories alongside `Project.toml`
- **Sources read:**
  - https://github.com/anowacki/FebusTools.jl
  - https://raw.githubusercontent.com/anowacki/FebusTools.jl/main/Project.toml
