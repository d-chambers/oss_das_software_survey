---
key: pypi/ccstudiodss
source: pypi
name: ccstudiodss
package: ccstudiodss
description: Build and load Code Composer Studio projects from the command line using the Java DSS library.
registry_url: https://pypi.org/project/ccstudiodss/
version: 0.4.3
last_release: '2021-02-13'
repository_url: null
repository_declared_in_metadata: false
license_stated: null
author: null
probes:
- pypi:simple-index-sweep
probe_class: broad-acronym
found_by:
- search
first_seen: '2026-08-28'
---

CCStudio DSS
============

|PyPI| |Pythons| |Travis| |GitHub|

Build and load Code Composer Studio projects from the command line using the Java DSS library.

Presently this is in use with Python 3.7.  It likely works with other versions.  In general I am often willing to support as far as 2.7 and 3.4+.  There are no tests presently but we could likely make some leveraging the `altendky/docker-ccstudio8`_ repository.

.. |PyPI| image:: https://img.shields.io/pypi/v/ccstudiodss.svg
   :alt: PyPI version
   :target: https://pypi.org/project/ccstudiodss/

.. |Pythons| image:: https://img.shields.io/pypi/pyversions/ccstudiodss.svg
   :alt: supported Python versions
   :target: https://pypi.org/project/ccstudiodss/

.. |Travis| image:: https://travis-ci.org/altendky/ccstudiodss.svg?branch=develop
   :alt: Travis build status
   :target: https://travis-ci.org/altendky/ccstudiodss

.. |GitHub| image:: https://img.shields.io/github/last-commit/altendky/ccstudiodss/develop.svg
   :alt: source on GitHub
   :target: https://github.com/altendky/ccstudiodss

.. _`altendky/docker-ccstudio8`: https://github.com/altendky/docker-ccstudio8
