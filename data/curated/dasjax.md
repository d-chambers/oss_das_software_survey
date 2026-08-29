---
id: dasjax
name: dasjax
repository: DASDAE/dasjax
repository_url: https://github.com/DASDAE/dasjax
homepage: null
description: JAX-compiled processing kernels and pipelines for DASCore.
status: included
decision_reason: Reusable DAS processing package whose LICENSE file states LGPL-3.0, which GitHub does
  not auto-detect.
primary_category: processing
capabilities:
- parallel-computing
- processing
license_spdx: LGPL-3.0-only
license_class: osi-approved
forge:
  kind: github
  host: github.com
registries:
  pypi:
  - dasjax
  conda: []
  julia: []
publications: []
das_focus: das-native
sources:
- github.com/dasdae/dasjax
reviewed_at: '2026-08-28'
provenance:
  agent: das-summarizer
  models:
  - claude-haiku-4-5-20251001
  - claude-sonnet-5
  ran_at: '2026-08-20T08:12:11+00:00'
  duration_seconds: 18.9
  turns: 3
  input_tokens: 6103
  output_tokens: 1373
  cache_read_tokens: 110588
  cache_write_tokens: 1721
  total_tokens: 119785
  api_list_cost_usd: 0.0658
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

## Summary

dasjax is an experimental Python library that accelerates DASCore, the core distributed acoustic sensing (DAS) processing package, using JAX. It lets users build compiled DAS processing pipelines that can execute on CPU, GPU, or TPU, with kernel fusion for performance. The main interface is a `JaxPatchPipeline` class that chains operations (e.g., scaling, detrending, normalizing) into a pipeline object that can then be compiled for repeated, fast execution. It targets researchers and engineers processing DAS data who need higher-throughput signal processing than DASCore's default implementation provides, differentiating itself from a generic signal-processing toolkit by focusing specifically on JAX-based compilation and hardware acceleration of DASCore's patch operations rather than reimplementing DAS analysis from scratch.

## Details

- **Interface:** library (Python package, installed via pip; used through a `JaxPatchPipeline` class)
- **Data formats:** not stated (works on DASCore `Patch` objects; no specific DAS file formats mentioned)
- **Key dependencies:** DASCore, JAX
- **Scope signals:** described as "experimental"; repository shows 0 stars/forks/watchers, ~5 commits, 1 open pull request — early-stage, low-activity project
- **Source visible:** yes — source code is present under `/src/dasjax/`, with `/tests/` and `/benchmarks/` directories, implementing operations such as real/imaginary/conjugate, flip, roll, pad, standardize, differentiate, integrate, DFT, Hilbert transform, envelope, taper, and whiten
- **Sources read:** https://github.com/DASDAE/dasjax
