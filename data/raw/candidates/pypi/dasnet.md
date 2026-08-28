---
key: pypi/dasnet
source: pypi
name: DASNet
package: dasnet
registry_url: https://pypi.org/project/dasnet/
version: 0.1.6
last_release: '2026-04-07'
repository_url: null
repository_declared_in_metadata: false
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

"DASNet: Mask R-CNN for event detection in Distributed Acoustic Sensing data"

## Verified by

sdist ships dasnet/model/{dasnet,maskrcnn,fastrcnn,roiheads}.py and dasnet/data/das.py. label_map is {1 Blue whale A, 2 Blue whale B, 3 Fin whale, 4 Others, 5 Blue whale D, 6 T wave, 7 Ship, 8 P wave, 9 S wave} -- a marine-bioacoustics DAS taxonomy.
