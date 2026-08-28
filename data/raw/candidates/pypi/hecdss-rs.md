---
key: pypi/hecdss-rs
source: pypi
name: hecdss-rs
package: hecdss-rs
description: Pure Rust HEC-DSS version 7 file reader/writer with Python bindings
registry_url: https://pypi.org/project/hecdss-rs/
version: 0.1.0
last_release: '2026-03-24'
repository_url: https://github.com/hatch-tyler/hec-dss-rs
repository_declared_in_metadata: true
license_stated: MIT
author: Tyler Hatch
probes:
- pypi:simple-index-sweep
probe_class: broad-acronym
found_by:
- search
first_seen: '2026-08-28'
---

# dss-python

PyO3 native Python module for HEC-DSS version 7 files. Zero C library dependency.

## Installation

```bash
cd crates/dss-python
pip install maturin
maturin build --release
pip install ../../target/wheels/dss_python-*.whl
```

## Quick Start

```python
import hecdss_rs
import numpy as np

with hecdss_rs.DssFile.create("example.dss") as dss:
    # Time series
    dss.write_ts("/A/B/FLOW/01JAN2020/1HOUR/SIM/",
                 np.array([100.0, 200.0, 300.0]), "CFS", "INST-VAL")
    values = dss.read_ts("/A/B/FLOW/01JAN2020/1HOUR/SIM/")  # numpy array

    # Catalog with wildcards
    entries = dss.catalog(filter="/*/*/FLOW///*/")

    # Date conversion
    j = hecdss_rs.DssFile.date_to_julian("15MAR2020")
    y, m, d = hecdss_rs.DssFile.julian_to_ymd(j)
```

## All Operations

35+ methods covering: text, regular/irregular time series, paired data, arrays, location, grids, delete/undelete, squeeze, copy, aliases, CRC tracking, date utilities, wildcard catalog filtering.

See [Python API Reference](../../docs/src/api/python.md) for complete documentation.
