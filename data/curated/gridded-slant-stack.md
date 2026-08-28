---
id: gridded-slant-stack
name: Gridded-SlantStack
repository: zackspica/Gridded-SlantStack
repository_url: https://github.com/zackspica/Gridded-SlantStack
homepage: null
description: MATLAB gridded slant-stack extraction of surface waves from DAS recordings.
status: included
decision_reason: Reusable MATLAB implementation of a DAS-specific method with an MIT license.
primary_category: processing
capabilities:
- processing
- surface-waves
- visualization
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
- github.com/zackspica/gridded-slantstack
reviewed_at: '2026-08-28'
provenance:
  agent: das-summarizer
  models:
  - claude-haiku-4-5-20251001
  - claude-sonnet-5
  ran_at: '2026-08-20T08:14:50+00:00'
  duration_seconds: 30.4
  turns: 4
  input_tokens: 11262
  output_tokens: 2181
  cache_read_tokens: 149006
  cache_write_tokens: 2625
  total_tokens: 165074
  api_list_cost_usd: 0.0964
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

## Summary

Gridded-SlantStack is a MATLAB implementation of a gridded slant-stack beamforming algorithm for extracting surface wave dispersion and velocity information from distributed acoustic sensing (DAS) recordings, developed to support research on subsurface imaging using ocean-bottom DAS and water-phase reverberations. It loads DAS strain-rate data on a distance-time grid, applies cascaded band-pass filtering around reference dispersion frequencies, then tests a range of velocity hypotheses via shift-and-stack beamforming to identify the velocity that maximizes stacking energy at each time-distance window, producing velocity and power images. It would be used by seismologists or geophysicists working with ocean-bottom or onshore DAS arrays who need a specific, research-grade surface-wave velocity picking method rather than a general-purpose DAS processing toolkit; it is a narrow, single-technique script tied to one published methodology rather than a broad framework.

## Details

- **Interface:** collection of MATLAB scripts (script-driven workflow), not a packaged library, CLI, or GUI
- **Data formats:** reads `.npy` (NumPy array) input files via a `readNPY()` helper (external, from the kwikteam/npy-matlab project); writes `.mat` output files (`Slant_Image_Forward.mat`, `Slant_Image_Backward.mat`)
- **Key dependencies:** MATLAB only; relies on the external `readNPY.m` utility and standard MATLAB functions (`meshgrid`, `interp2`, `circshift`, `readtable`); no other third-party libraries stated
- **Scope signals:** early-stage research code tied to a single paper ("Subsurface Imaging with Ocean-Bottom Distributed Acoustic Sensing and Water Phases Reverberations," Spica et al., in prep for Geophysical Research Letters); 8 stars, 1 fork, 17 commits, no releases, no automated tests, MIT license
- **Source visible:** yes — actual `.m` source files and a sample dataset are published in the repository
- **Sources read:** https://github.com/zackspica/Gridded-SlantStack, https://github.com/zackspica/Gridded-SlantStack/blob/main/DAS_Gridded-SlantStack.m
