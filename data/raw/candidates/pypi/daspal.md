---
key: pypi/daspal
source: pypi
name: DASPAL
package: daspal
registry_url: https://pypi.org/project/daspal/
version: 1.0.0a1
last_release: '2026-08-03'
repository_url: null
repository_declared_in_metadata: false
license_stated: null
author: null
probes:
- pypi:simple-index-sweep
probe_class: domain-specific
found_by:
- search
first_seen: '2026-08-28'
---

## Evidence

"**DAS Processing & Analysis Library** ... presents a set of tools for **Distibuted Acoustic Sensing (DAS) data processing and analysis**. It aims to leverage on existing widely used py[thon]"

## Verified by

wheel contains daspal/instr/{optodas,apsensing,dxs,dasproc}.py, daspal/io/{h5fc,zarrfc,read,write,finder}.py, daspal/dask_utils/. Three interrogator vendors, so this is a real reader set, not a stub.

## Forge note

No public source located on any host.
