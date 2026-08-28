---
curated:
  id: pyrocko
  name: Pyrocko
  repository: pyrocko/pyrocko
  repository_url: https://github.com/pyrocko/pyrocko
  homepage: https://pyrocko.org
  description: Versatile seismology toolkit for Python with built-in readers for two Silixa DAS formats
    and a Snuffler waterfall view for dense recordings.
  status: excluded
  decision_reason: A general seismological toolkit that added DAS support, not DAS-specific software;
    the same reading applied to SeisBench. The support is real rather than incidental - src/io registers
    tdms_idas (Silixa TDMS) and hdf5_idas (Silixa HDF5) as self-contained readers with format autodetection,
    and src/gui/snuffler/pile_viewer_waterfall.py implements the changelog's "waterfall style for dense
    recordings like DAS". A third format, ASN OptoDAS, is an adapter over the third-party simpledas package,
    which pyrocko does not declare as a dependency; without it hdf5_optodas.detect() returns False and
    iload raises ImportError, so OptoDAS is not built-in support and is not counted here. Catalogued and
    classed das-supporting rather than left out of the record.
  primary_category: out-of-scope
  capabilities:
  - io
  - seismology
  - visualization
  license_spdx: GPL-3.0-or-later
  license_class: osi-approved
  forge:
    kind: github
    host: github.com
  registries:
    pypi: []
    conda: []
    julia: []
  publications: []
collected:
  snapshot: '2026-08-28'
  dependencies: []
  unavailable:
    pypi_downloads_total: no free source publishes all-time PyPI totals
    conda_downloads_180d: anaconda.org publishes a cumulative count only, with no time series
---

# Pyrocko

Source: [pyrocko/pyrocko](https://github.com/pyrocko/pyrocko)

_No agent summary has been generated for this project._
