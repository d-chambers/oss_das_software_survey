---
key: pypi/fiberphotometrydataanalysis
source: pypi
name: FiberPhotometryDataAnalysis
package: fiberphotometrydataanalysis
description: A package for analysis of multi-fiber photmetry data and behaviour.
registry_url: https://pypi.org/project/fiberphotometrydataanalysis/
version: 0.0.9
last_release: '2021-06-18'
repository_url: null
repository_declared_in_metadata: false
license_stated: MIT
author: Kate Martian
probes:
- pypi:simple-index-sweep
probe_class: broad-acronym
found_by:
- search
first_seen: '2026-08-28'
---

========
Overview
========

A package for analysis of multi-fiber photmetry data and behaviour.

* Free software: MIT license

Installation
============

::

    pip install FiberPhotometryDataAnalysis

You can also install the in-development version with::

    pip install git+ssh://git@https://github.com/katemartian/FiberPhotometryDataAnalysis.git@master

Documentation
=============


https://FiberPhotometryDataAnalysis.readthedocs.io/


Development
===========

To run all the tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox


Changelog
=========

0.0.1 (2021-06-17)
------------------

* First release on PyPI.
