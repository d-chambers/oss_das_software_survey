---
id: spool-processing
name: SpoolProcessing
repository: DASDAE/SpoolProcessing
repository_url: https://github.com/DASDAE/SpoolProcessing
homepage: null
description: Folder-spool downsampling and statistical processing with on-disk output.
status: included
decision_reason: Reusable DAS processing module with an MIT license and worked examples.
primary_category: processing
capabilities:
- data-management
- pipelines
- processing
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
- github.com/dasdae/spoolprocessing
reviewed_at: '2026-08-28'
provenance:
  agent: das-summarizer
  models:
  - claude-haiku-4-5-20251001
  ran_at: '2026-08-20T08:18:56+00:00'
  duration_seconds: 50.5
  turns: 9
  input_tokens: 15122
  output_tokens: 3164
  cache_read_tokens: 250435
  cache_write_tokens: 12876
  total_tokens: 281597
  api_list_cost_usd: 0.0817
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

## Summary

SpoolProcessing is a Python package for processing data from distributed sensor arrays using folder spool organization. It performs direct down-sampling with anti-aliasing filtering or standard deviation processing on streaming data written to disk. The project targets researchers and data engineers working with time-series sensor data that needs preprocessing at scale. Developed by Dr. Ge Jin, it is in active development and explicitly advises caution in production use. The focus on spool-based processing suggests it handles batched or continuously-arriving data files typical in high-volume sensor deployments.

## Details

- **Interface:** library
- **Data formats:** not stated
- **Key dependencies:** not stated
- **Scope signals:** Developmental status (README states "Still under development. Use with caution."). Minimal adoption (0 stars, 2 forks, 2 open issues). No apparent integration with standard DAS frameworks or formats. Examples directory exists but contents are not documented.
- **Source visible:** Yes—repository contains Python source files (`proc.py`, `utils.py`) under MIT license. No package configuration files (setup.py, pyproject.toml, requirements.txt) are visible in the repository structure.
- **Sources read:** https://github.com/DASDAE/SpoolProcessing (main page, fetched twice with different prompts)
