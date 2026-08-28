---
key: pypi/nrel-altdss-schema
source: pypi
name: NREL-altdss-schema
package: nrel-altdss-schema
description: Pydantic data models for OpenDSS.
registry_url: https://pypi.org/project/nrel-altdss-schema/
version: 0.0.3
last_release: '2026-03-30'
repository_url: https://github.com/NREL-Distribution-Suites/altdss-schema
repository_declared_in_metadata: true
license_stated: BSD-3-Clause
author: Paulo Meira <pmeira@ieee.org>, Tarek Elgindy <tarek.elgindy@nrel.gov>, Aadil Latif <aadil.latif@nrel.gov>
probes:
- pypi:simple-index-sweep
probe_class: broad-acronym
found_by:
- search
first_seen: '2026-08-28'
---

This repository builds upon the original work by [PMeira](https://github.com/PMeira) at [AltDSS-Schema](https://github.com/dss-extensions/AltDSS-Schema), which aimed to define a structured JSON-based schema for DSS circuit representation. The schema has been packaged in this repository with slight modifications, enabling users to add the package as a dependency for downstream applications. This repository is actively maintained by [Tarek Elgindy](https://github.com/tarekelgindy)
