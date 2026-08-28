---
id: distpy
name: distpy
repository: Schlumberger/distpy
repository_url: https://github.com/Schlumberger/distpy
homepage: null
description: Branched, scalable processing flows for distributed fiber-optic sensor data.
status: included
decision_reason: Reusable DAS processing package with an MIT license and PyPI releases.
primary_category: processing
capabilities:
- parallel-computing
- pipelines
- processing
- visualization
license_spdx: MIT
license_class: osi-approved
forge:
  kind: github
  host: github.com
registries:
  pypi:
  - distpy
  conda: []
  julia: []
publications: []
das_focus: das-native
sources:
- github.com/schlumberger/distpy
reviewed_at: '2026-08-28'
provenance:
  agent: das-summarizer
  models:
  - claude-haiku-4-5-20251001
  - claude-sonnet-5
  ran_at: '2026-08-20T08:13:02+00:00'
  duration_seconds: 32.0
  turns: 7
  input_tokens: 16784
  output_tokens: 2838
  cache_read_tokens: 181345
  cache_write_tokens: 9575
  total_tokens: 210542
  api_list_cost_usd: 0.159
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

## Summary

distpy is a Python library for building signal-processing workflows over distributed acoustic sensing (DAS) and distributed temperature sensing (DTS) data, developed by Schlumberger (SLB). It provides an extensible library of 70+ signal-processing operations that users chain into directed-graph ("branched network") workflows, which can be exported as self-describing JSON files so a pipeline built on one machine can be reproduced on another — including cloud, edge, Windows, and Linux deployments. It targets DAS/DTS practitioners in well monitoring and flow-assurance settings, including researchers without a traditional geophysics background, who need to prototype and share processing flows for high-rate fiber-optic sensor data (a 5 km fiber can produce roughly 450 Mb/s). What distinguishes it from a generic signal-processing toolkit is this graph-based, serializable workflow model paired with domain-specific DAS/DTS operations, rather than just a library of raw array/filter functions.

## Details

- **Interface:** library (Python package), with example Jupyter notebooks and standalone Python scripts
- **Data formats:** SEGY (referenced for DAS data handling), WITSML (referenced as an output format); JSON used for workflow/pipeline serialization
- **Key dependencies:** numpy, scipy, numba, matplotlib, h5py, pandas, scikit-learn
- **Scope signals:** listed as "Pre-Alpha" development status in setup.py; ~64 commits, 40 stars, 20 forks; MIT licensed; supports Docker/Kubernetes containerization and GPU acceleration; Python 3.7+
- **Source visible:** yes — the repository publishes source code (`distpy/` core library, `config_examples/`, `python_examples/`, `jupyter_examples/`, `docker/`, `docs/`, `setup.py`)
- **Sources read:** https://github.com/Schlumberger/distpy, https://raw.githubusercontent.com/Schlumberger/distpy/master/README.md, https://github.com/Schlumberger/distpy/wiki, https://github.com/Schlumberger/distpy/blob/master/setup.py
