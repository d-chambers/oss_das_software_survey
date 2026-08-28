---
id: idas-convert
name: idas-convert
repository: pyrocko/idas-convert
repository_url: https://github.com/pyrocko/idas-convert
homepage: null
description: Conversion of Silixa iDAS TDMS data into established seismic formats.
status: included
decision_reason: Reusable DAS conversion tool with GPL-3.0 licensing.
primary_category: data-management
capabilities:
- conversion
- data-management
- io
license_spdx: GPL-3.0-only
license_class: osi-approved
forge:
  kind: github
  host: github.com
registries:
  pypi: []
  conda: []
  julia: []
publications:
- doi: 10.5880/gfz.2.1.2021.005
  role: canonical
  note: null
das_focus: das-native
sources:
- github.com/pyrocko/idas-convert
reviewed_at: '2026-08-28'
provenance:
  agent: das-summarizer
  models:
  - claude-haiku-4-5-20251001
  - claude-sonnet-5
  ran_at: '2026-08-20T08:14:50+00:00'
  duration_seconds: 31.2
  turns: 6
  input_tokens: 13326
  output_tokens: 2070
  cache_read_tokens: 226333
  cache_write_tokens: 2679
  total_tokens: 244408
  api_list_cost_usd: 0.1222
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

## Summary

idas-convert is a command-line tool for converting distributed acoustic sensing (DAS) data recorded by Silixa iDAS interrogators from the manufacturer's TDMS format into standard seismological data formats, chiefly MiniSeed. It targets seismologists and DAS researchers who need to move raw high-rate interrogator output into formats consumable by conventional seismic processing tools and archives. Conversions are configured through YAML files (generated via a `dump_config` command) and executed via a `das_convert` CLI, with support for parallel processing, downsampling (e.g. 1 kHz to 200 Hz), and STEIM compression. What distinguishes it from a generic converter is its production orientation: it is built on Pyrocko, an established seismological framework, is maintained by GFZ German Research Centre for Geosciences, cites a throughput benchmark of 200 MB/s on production systems, and includes optional plugins for tape-archive management and Telegram notifications.

## Details

- **Interface:** CLI (`das_convert`), configured via YAML files
- **Data formats:** reads Silixa iDAS TDMS files; writes MiniSeed (and other Pyrocko-supported seismological formats)
- **Key dependencies:** Pyrocko, numpy, telebot (Telegram bot integration for optional notifications)
- **Scope signals:** small project (9 stars, 2 forks, 18 commits at time of reading), GPL-3.0 licensed, maintained by GFZ German Research Centre for Geosciences with a citable DOI; documentation site exists; presented as production-capable (stated throughput benchmarks) rather than experimental
- **Source visible:** yes — repository publishes source code (`src/`, `test/`, `doc/`, `setup.py`, `requirements.txt`)
- **Sources read:** https://github.com/pyrocko/idas-convert, https://github.com/pyrocko/idas-convert/blob/master/requirements.txt
