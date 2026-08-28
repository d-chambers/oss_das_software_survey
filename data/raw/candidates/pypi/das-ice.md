---
key: pypi/das-ice
source: pypi
name: DAS_Ice
package: das-ice
registry_url: https://pypi.org/project/das-ice/
version: 0.3.10
last_release: '2025-12-05'
repository_url: https://gricad-gitlab.univ-grenoble-alpes.fr/mecaiceige/tools/lib_python/das_ice
repository_declared_in_metadata: false
license_stated: GPL-3.0 (stated on the docs site; no license classifier on PyPI)
author: Thomas Chauve (IGE, Universite Grenoble Alpes)
probes:
- pypi:simple-index-sweep
probe_class: domain-specific
found_by:
- search
first_seen: '2026-08-28'
---

## Evidence

"DAS_Ice is a python librairy to process DAS data. It is based on `xarray` and `dask` in order to allow processing of large dataset."

## Verified by

sdist ships das_ice/{io,mfp,plot,processes,metadata}.py and das_ice/signal/{filter,picker}.py; depends on xdas.

## Forge note

Grenoble institutional GitLab, behind an Anubis anti-bot wall. The URL was recovered from the GitLab Pages docs site, not from the package metadata. A crawler that already knew the URL would still be blocked.
