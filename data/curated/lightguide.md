---
id: lightguide
name: lightguide
repository: pyrocko/lightguide
repository_url: https://github.com/pyrocko/lightguide
homepage: https://pyrocko.org
description: DAS handling, filtering, and forward modeling integrated with Pyrocko.
status: included
decision_reason: Reusable DAS-specific Python library under GPL-3.0.
primary_category: processing
capabilities:
- denoising
- io
- modeling
- processing
- visualization
license_spdx: GPL-3.0-only
license_class: osi-approved
forge:
  kind: github
  host: github.com
registries:
  pypi:
  - lightguide
  conda: []
  julia: []
publications:
- doi: 10.5281/zenodo.6580579
  role: canonical
  note: null
das_focus: das-native
sources:
- github.com/pyrocko/lightguide
reviewed_at: '2026-08-28'
provenance:
  agent: das-summarizer
  models:
  - claude-haiku-4-5-20251001
  - claude-sonnet-5
  ran_at: '2026-08-20T08:14:51+00:00'
  duration_seconds: 165.4
  turns: 5
  input_tokens: 7698
  output_tokens: 2026
  cache_read_tokens: 181562
  cache_write_tokens: 8220
  total_tokens: 199506
  api_list_cost_usd: 0.1359
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

## Summary

Lightguide is a Python library for processing and modeling distributed acoustic sensing (DAS) data, built on top of the Pyrocko seismological framework. It reads strain measurements from fiber-optic interrogator formats (Silixa iDAS/TDMS, ASN OptoDAS) and MiniSEED, and provides an adaptive frequency-wavenumber filter for suppressing common DAS noise patterns, alongside Green's-function-based forward modeling of seismic sources in layered or homogeneous half-spaces. It is aimed at seismologists and DAS researchers who need format-specific I/O and denoising tools rather than a general signal-processing toolkit, and its tight coupling to Pyrocko's data model and I/O engine distinguishes it from standalone DAS packages. Performance-sensitive routines are implemented in Rust and exposed to Python via Maturin. The project explicitly labels itself Beta software, so interfaces are expected to change.

## Details

- **Interface:** library (Python, imported and called directly; e.g. `Blast.from_miniseed()`)
- **Data formats:** reads MiniSEED, Silixa iDAS (TDMS), and ASN OptoDAS; specific write formats not stated beyond "Pyrocko's I/O engine"
- **Key dependencies:** pyrocko (>=2022.4.28), numpy (>=1.20.0), requests (>=2.20.0); built with maturin/setuptools-rust (Rust extension)
- **Scope signals:** README states "The framework is still in Beta. Expect changes throughout all functions."; includes a test suite and documentation build tooling (Sphinx/myst-nb), suggesting active but early-stage development
- **Source visible:** yes — repository contains Python and Rust source (`lightguide/` and `src/` directories) with tests
- **Sources read:** https://github.com/pyrocko/lightguide, https://raw.githubusercontent.com/pyrocko/lightguide/master/pyproject.toml (docs site at pyrocko.org was unreachable — connection refused)
