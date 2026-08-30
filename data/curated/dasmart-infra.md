---
id: dasmart-infra
name: DASmartInfra
repository: Pengchao-He/DASmartInfra
repository_url: https://github.com/Pengchao-He/DASmartInfra
homepage: null
description: Algorithms, benchmarks, and edge-inference components for DAS infrastructure monitoring.
status: excluded
decision_reason: The repository publishes governance and documentation scaffolding but no software.
  Every directory it advertises -- algorithms, datasets, edge, examples -- holds only a README placeholder
  or a .gitkeep, and the one Python file is a stdlib-only repository-layout validator. The same reading
  applied to edgedas and dasview - a licence and an intention are not source anyone can review or reuse.
primary_category: out-of-scope
capabilities:
- benchmarking
- detection
- machine-learning
- processing
license_spdx: Apache-2.0
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
- github.com/pengchao-he/dasmartinfra
reviewed_at: '2026-08-28'
provenance:
  agent: das-summarizer
  models:
  - claude-haiku-4-5-20251001
  - claude-sonnet-5
  ran_at: '2026-08-20T08:12:11+00:00'
  duration_seconds: 62.5
  turns: 8
  input_tokens: 21302
  output_tokens: 3400
  cache_read_tokens: 229787
  cache_write_tokens: 3428
  total_tokens: 257917
  api_list_cost_usd: 0.1482
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

## Summary

DASmartInfra is a nascent open-source initiative aiming to build shared infrastructure for distributed acoustic sensing (DAS)-based structural health monitoring across bridges, roads, tunnels, buildings, railways, and slopes. It proposes to host open field datasets, reproducible algorithms, benchmarks linking sensor data to engineering questions, and real-time edge-computing workflows, positioned as a community collaboration hub rather than a single tool. It would be used by researchers and infrastructure engineers looking for shared DAS datasets or benchmark tasks, once such content exists. As of this reading the repository is almost entirely organizational scaffolding — README files, governance and contribution documents, and metadata schemas — with no algorithm implementations, example workflows, or datasets actually present yet. The project itself states it is in an "early testing and community-foundation stage" and not validated for production or safety-critical use.

## Details

- **Interface:** not stated (no implemented interface; scaffolding suggests a future library/dataset repository)
- **Data formats:** not stated as implemented; a JSON Schema for a "dataset card" (`schemas/dataset-card.schema.json`) and a YAML data-card template exist, but no actual DAS/fiber data format readers or writers are present
- **Key dependencies:** none — the only Python file in the repository, `tools/validate_repository.py`, uses only the standard library (`json`, `re`, `sys`, `pathlib`)
- **Scope signals:** repository is 27 KB, created 2026-08-10 and last updated the same day; 0 stargazers; contains `algorithms/`, `datasets/`, `edge/`, `examples/`, `schemas/`, `tools/` directories, but all except `tools/` and `schemas/` contain only README placeholders or `.gitkeep` files; explicitly self-described as "early testing and community-foundation stage"
- **Source visible:** effectively no — the repository publishes governance/documentation scaffolding and one standard-library validation script, but no algorithm, edge-computing, or dataset-processing source code
- **Sources read:** https://github.com/Pengchao-He/DASmartInfra, https://api.github.com/repos/Pengchao-He/DASmartInfra, https://api.github.com/repos/Pengchao-He/DASmartInfra/contents/, https://api.github.com/repos/Pengchao-He/DASmartInfra/git/trees/main?recursive=1, https://raw.githubusercontent.com/Pengchao-He/DASmartInfra/main/tools/validate_repository.py
