---
key: pypi/deltaseis
source: pypi
name: DeltaSEIS
package: deltaseis
registry_url: https://pypi.org/project/deltaseis/
version: 0.0.5
last_release: '2024-11-29'
repository_url: https://github.com/Deltares-research/DeltaSEIS
repository_declared_in_metadata: true
license_stated: MIT
author: null
probes:
- pypi:simple-index-sweep
probe_class: domain-specific
found_by:
- search
first_seen: '2026-08-28'
---

## Evidence

"The Deltares Seismic (DeltaSEIS) package is designed to handle all common formats of seismic data. This includes conventional seismic data, DAS fiber optic and simulated data."

## Verified by

deltaseis/readers/reader_seismic_tdms.py is Silixa's iDAS TDMS reader, header "Copyright (c) 2018 Silixa Ltd". Not an advertised feature -- the reader is in the tree.
