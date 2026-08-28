---
id: fosanalysis
name: fosanalysis
repository: TUD-IMB/fosanalysis
repository_url: https://github.com/TUD-IMB/fosanalysis
homepage: https://tud-imb.github.io/fosanalysis/
description: Python framework for evaluating distributed fibre optic strain measurements and calculating
  crack widths in concrete structures.
status: watchlist
decision_reason: OSI-licensed, PyPI-published DFOS package with a documented pre-processing pipeline,
  but distributed strain sensing is a different modality from DAS and is held out of the headline comparison,
  as python-dts-calibration is.
primary_category: processing
capabilities:
- io
- processing
- strain-sensing
license_spdx: GPL-3.0-only
license_class: osi-approved
forge:
  kind: github
  host: github.com
registries:
  pypi:
  - fosanalysis
  conda: []
  julia: []
publications:
- doi: 10.1002/suco.202300100
  role: canonical
  note: Introduces the framework.
- doi: 10.3390/s24237454
  role: related
  note: Pre-processing methods added in the framework, with the code availability statement.
das_focus: other-fiber
sources:
- github.com/tud-imb/fosanalysis
reviewed_at: '2026-08-28'
---
