---
key: pypi/readerdas
source: pypi
name: ReaderDAS
package: readerDAS
registry_url: https://pypi.org/project/readerDAS/
version: 1.1.5
last_release: '2025-07-24'
repository_url: null
repository_declared_in_metadata: false
license_stated: null
author: Marco Brunero (marco.brunero@cohaerentia.com)
probes:
- pypi:simple-index-sweep
probe_class: domain-specific
found_by:
- search
first_seen: '2026-08-28'
---

## Evidence

"Package to load files saved by Cohaerentia DAS Interrogator."

## Verified by

sdist ships readerDAS/{main,classes,utils,sottocampionamento}.py with HDF5 section and time-window slicing. README is in Italian.
