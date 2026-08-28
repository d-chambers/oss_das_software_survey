---
key: pypi/pyhecdss
source: pypi
name: pyhecdss
package: pyhecdss
description: For reading/writing HEC-DSS files
registry_url: https://pypi.org/project/pyhecdss/
version: 1.5.12
last_release: '2024-12-20'
repository_url: https://github.com/dwr-psandhu/pyhecdss
repository_declared_in_metadata: true
license_stated: MIT
author: Nicky Sandhu <psandhu@water.ca.gov>
probes:
- pypi:simple-index-sweep
probe_class: broad-acronym
found_by:
- search
first_seen: '2026-08-28'
---

========
pyhecdss
========

>  **Note:** This project only supports **DSS version 6** and now recommends users to `HEC-DSS Python`_ version 7 and higher

For reading/writing HEC-DSS files [https://www.hec.usace.army.mil/software/hec-dss/]
HEC-DSS is an ancient database used by the Army Corps of Engineers and prevalent
in water related models. This module is a bridge to read and write time series
data from this data format and read it into pandas DataFrame

* Free software: MIT license
* Documentation: https://cadwrdeltamodeling.github.io/pyhecdss/


Features
--------

* Open and close DSS files
* Read catalog of DSS files as pandas DataFrame
* Read and write time series from DSS files

Limitations
-----------

* Only support for Python 3 - 64 bit for windows and linux
* Relies on pre-compiled libraries the source distribution of which is not allowed

Credits
-------

This package wraps the `HEC-DSS Software`_ using the `Swig`_ library.

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _`HEC-DSS Software`: https://www.hec.usace.army.mil/software/hec-dss/
.. _`HEC-DSS Python`: https://github.com/HydrologicEngineeringCenter/hec-dss-python
.. _Swig: http://www.swig.org/
