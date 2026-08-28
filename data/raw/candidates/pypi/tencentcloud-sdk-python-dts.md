---
key: pypi/tencentcloud-sdk-python-dts
source: pypi
name: tencentcloud-sdk-python-dts
package: tencentcloud-sdk-python-dts
description: Tencent Cloud Dts SDK for Python
registry_url: https://pypi.org/project/tencentcloud-sdk-python-dts/
version: 3.1.157
last_release: '2026-08-17'
repository_url: https://github.com/TencentCloud/tencentcloud-sdk-python
repository_declared_in_metadata: true
license_stated: Apache License 2.0
author: Tencent Cloud
probes:
- pypi:simple-index-sweep
probe_class: broad-acronym
found_by:
- search
first_seen: '2026-08-28'
---

============================
Tencent Cloud SDK for Python
============================

Tencent Cloud Python Dts SDK is the official software development kit, which allows Python developers to write software that makes use of Tencent Cloud services like CVM and CBS.
The SDK works on Python versions:

   * 2.7 and greater, including 3.x

Quick Start
-----------

First, install the library:

.. code-block:: sh

    $ pip install tencentcloud-sdk-python-common
    $ pip install tencentcloud-sdk-python-dts

or download source code from github and install:

.. code-block:: sh

    $ git clone https://github.com/tencentcloud/tencentcloud-sdk-python.git
    $ cd tencentcloud-sdk-python
    $ python package.py --components common dts
