---
key: pypi/cimhub-opendss
source: pypi
name: cimhub-opendss
package: cimhub-opendss
description: CIMHub OpenDSS Library
registry_url: https://pypi.org/project/cimhub-opendss/
version: 2.0.0a2
last_release: '2026-08-17'
repository_url: https://github.com/PNNL-CIM-Tools/CIMHub_2_0
repository_declared_in_metadata: true
license_stated: BSD-2-Clause
author: Pacific Northwest National Laboratory <gridappsd@pnnl.gov>
probes:
- pypi:simple-index-sweep
probe_class: broad-acronym
found_by:
- search
first_seen: '2026-08-28'
---

# Cimhub OpenDSS

Bidirectional converter between OpenDSS and CIM (IEC 61968/61970) using the `cimhub_2026` profile.

## Usage

### DSS to CIM (Import)

```python
import os
os.environ['CIMG_USE_UNITS'] = 'TRUE'
os.environ['CIMG_CIM_PROFILE'] = 'cimhub_2026'

from cimhub_opendss.importer.dss_to_cim import dss_to_cim

feeder = dss_to_cim("/path/to/Master.dss")
```

### CIM to DSS (Export)

```python
from cimhub_opendss.exporter.cim_to_dss import cim_to_dss

cim_to_dss(feeder, "/path/to/output_dir")
# Writes Master.dss + per-component .dss files
```

### Roundtrip Validation

A full DSS -> CIM -> DSS roundtrip integration test is provided for the IEEE 13-bus feeder:

```bash
uv run python cimhub_opendss/tests/test_ieee13_roundtrip.py
# or via pytest:
uv run pytest cimhub_opendss/tests/test_ieee13_roundtrip.py -vs
```

The roundtrip parses the IEEE 13-bus DSS model, imports to CIM, exports back to DSS,
solves both models with OpenDSS, and compares total power and bus voltages. Current
accuracy is within 0.14% on active power (4.4 kW on a 3230 kW system).

## Models

### Mandatory

- [x] Power Transformer
- [x] Transformers
- [x] Regulator Controls
- [x] Line Code
- [x] Line
- [x] Capacitor
- [x] Load
- [x] PV System 
- [x] Storage
- [x] Switch
- [x] Fuse
- [x] Recloser
- [x] Breaker
- [x] Generator
- [ ] CNData (importer only)
- [ ] TSData (importer only)
- [ ] Line Geometry (importer only)
- [ ] Line Spacing (importer only)
- [x] Wire Data
- [ ] XY Curve

### As Needed

- [ ] GIC Transformer
- [ ] GIC Line
- [ ] Induction Machine
- [ ] UPFC Device
- [ ] Wind Generator
- [x] Capacitor Control
- [ ] Inverter Control
- [ ] Storage Control
- [ ] Switch Control
- [ ] UPFC Control
