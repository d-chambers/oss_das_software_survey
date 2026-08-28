---
key: pypi/gfiberspeedtest
source: pypi
name: gfiberspeedtest
package: gfiberspeedtest
description: Run a Google Fiber speedtest via cli
registry_url: https://pypi.org/project/gfiberspeedtest/
version: 1.0.1
last_release: '2017-10-25'
repository_url: https://github.com/johnfrancisgit/gfiberspeedtest_cli
repository_declared_in_metadata: true
license_stated: MIT
author: John Francis
probes:
- pypi:simple-index-sweep
probe_class: broad-acronym
found_by:
- search
first_seen: '2026-08-28'
---

Google Fiber Speedtest cli
==========================

A simple python module to perform a google fiber speedtest, either by running
from the terminal or importing the module into your python project.
This module uses a high-level solution, in which the google fiber speedtest
webpage is loaded and manipulated with selenium. After the speedtest has 
been completed, the results will be scraped and returned.
