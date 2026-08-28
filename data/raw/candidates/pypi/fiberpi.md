---
key: pypi/fiberpi
source: pypi
name: FiberPI
package: fiberpi
description: Package to detect contaminated fiber connectors
registry_url: https://pypi.org/project/fiberpi/
version: 0.0.3
last_release: '2019-06-10'
repository_url: https://github.com/utepnetlab/fiberPI
repository_declared_in_metadata: true
license_stated: null
author: Christopher Mendoza
probes:
- pypi:simple-index-sweep
probe_class: broad-acronym
found_by:
- search
first_seen: '2026-08-28'
---

# FiberPI
Package that automates detecting contaminated fiber connectors between switches using the switch CLIs.
[Github Link](https://github.com/utepnetlab/fiberPI)

## Installation

```bash
pip install FiberPI
```

## Usage
```python
import FiberPI as FPI

#Create the two switches
ubnt = FPI.node('Ubiquiti', '192.168.1.1', 'ubiquiti_edgeswitch', 'user', 'pass')
dlink = FPI.node('D-Link', '192.168.1.2', 'dlink_dgs', 'user', 'pass')

#Create the connection using a context manager to open and close connections
with FPI.connection('conn', ubnt, dlink, 1, 27, 0, 1, 1) as conn:
    #Detect Contamination
    result = conn.DetectContamination()
```
## Contributing
Anyone is welcome to contribute, if you'd like send a pull request for major changes with the changes you'd like to make.

## License
[MIT](https://choosealicense.com/licenses/mit/)
