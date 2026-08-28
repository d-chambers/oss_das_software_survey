---
key: pypi/dss-python
source: pypi
name: dss-python
package: dss-python
description: Python interface (bindings and tools) for OpenDSS. Based on the AltDSS/DSS C-API project,
  the alternative OpenDSS implementation from DSS-Extensions.org. Multiplatform, API-compatible/drop-in
  replacement for the COM version of OpenDSS.
registry_url: https://pypi.org/project/dss-python/
version: 0.15.7
last_release: '2026-02-26'
repository_url: https://github.com/dss-extensions/DSS-Python
repository_declared_in_metadata: true
license_stated: 'BSD 3-Clause License  Copyright (c) 2017-2023, Paulo Meira Copyright (c) 2017-2023, DSS-Python
  contributors All rights reserved.  Redistribution and use in source and binary forms, with or without
  modification, are permitted provided that the following conditions are met:  * Redistributions of source
  code must retain the above copyright notice, this list of conditions and the following disclaimer.  *
  Redistributions in binary form must reproduce the above copyright notice, this list of conditions and
  the following disclaimer in the documentation and/or other materials provided with the distribution.  *
  Neither the name of the copyright holder nor the names of its contributors may be used to endorse or
  promote products derived from this software without specific prior written permission.  THIS SOFTWARE
  IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
  INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
  PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
  INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT
  OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
  AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
  OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY
  OF SUCH DAMAGE.'
author: Paulo Meira <pmeira@ieee.org>, Dheepak Krishnamurthy <me@kdheepak.com>
probes:
- pypi:simple-index-sweep
probe_class: broad-acronym
found_by:
- search
first_seen: '2026-08-28'
---

[![Builds](https://github.com/dss-extensions/dss_python/actions/workflows/builds.yml/badge.svg)](https://github.com/dss-extensions/dss_python/actions/workflows/builds.yml)
[![PyPI](https://img.shields.io/pypi/v/dss_python)](https://pypi.org/project/dss-python/) 
[![PyPI Download stats](https://static.pepy.tech/badge/dss-python/month)](https://pepy.tech/project/dss-python)
 <img alt="Supports Linux" src="https://img.shields.io/badge/Linux-FCC624?logo=linux&logoColor=black"> <img alt="Supports macOS" src="https://img.shields.io/badge/macOS-000000?logo=apple&logoColor=white"> <img alt="Supports Microsoft Windows" src="https://img.shields.io/badge/Windows-0078D6?logo=windows&logoColor=white">

# DSS-Python: Extended bindings for an alternative implementation of EPRI's OpenDSS

Python bindings and misc tools for using our to [our customized/alternative implementation](https://github.com/dss-extensions/dss_capi) of [OpenDSS](http://smartgrid.epri.com/SimulationTool.aspx), AltDSS/DSS C-API library. OpenDSS is an open-source electric power distribution system simulator [distributed by EPRI](https://sourceforge.net/p/electricdss/). Based on DSS C-API, CFFI and NumPy, aiming for enhanced performance and full compatibility with the official COM object API on Windows, Linux and macOS. Support includes Intel-based (x86 and x64) processors, as well as ARM processors for Linux (including Raspberry Pi devices) and macOS (including Apple M1 and later).

More context about this project and its components (including alternatives in [Julia](https://dss-extensions.org/OpenDSSDirect.jl/latest/), [MATLAB](https://github.com/dss-extensions/dss_matlab/), C++, [C#/.NET](https://github.com/dss-extensions/dss_sharp/), [Go](https://github.com/dss-extensions/AltDSS-Go/), and [Rust](https://github.com/dss-extensions/AltDSS-Rust/)), please check [https://dss-extensions.org/](https://dss-extensions.org/) and our hub repository at [dss-extensions/dss-extensions](https://github.com/dss-extensions/dss-extensions) for more documentation, discussions and the [FAQ](https://dss-extensions.org/faq.html).

This package can be used as a companion to [OpenDSSDirect.py](http://github.com/dss-extensions/OpenDSSDirect.py/), if you don't need COM compatibility, or just would like to check its extra functionalities. Yet another alternative Python package is being developed in [AltDSS-Python](https://dss-extensions.org/AltDSS-Python/). The three packages can be used together, allowing the different API styles to be used in the same program.

While we plan to add a lot more functionality into DSS-Python, the main goal of creating a COM-compatible API has been reached in 2018. If you find an unexpected missing feature, please report it! Currently missing features that will be implemented eventually are interactive features and diakoptics (planned for a future version).

This module mimics the COM structure (as exposed via `win32com` or `comtypes`) — see [The DSS instance](https://dss-extensions.org/DSS-Python/#the-dss-instance) as well as [OpenDSS COM/classic APIs](https://dss-extensions.org/classic_api.html) for some docs — effectively enabling multi-platform compatibility at Python level. Compared to other options, it provides easier migration from code that uses the official OpenDSS through COM. See also [OpenDSS: Python APIs](https://dss-extensions.org/python_apis.html).
Most of the COM documentation can be used as-is, but instead of returning tuples or lists, this module returns/accepts NumPy arrays for numeric data exchange, which is usually preferred by the users. By toggle `DSS.AdvancedTypes`, complex numbers and matrices (shaped arrays) are also used to provide a more modern experience.

The module depends mostly on CFFI, NumPy, typing_extensions and, optionally, SciPy.Sparse for reading the sparse system admittance matrix. Pandas and matplotlib are optional dependencies [to enable plotting](https://github.com/dss-extensions/dss_python/blob/master/docs/examples/Plotting.ipynb) and other features.

## Release history

Check [the Releases page](https://github.com/dss-extensions/dss_python/releases) and [the changelog](https://github.com/dss-extensions/dss_python/blob/master/docs/changelog.md).

## Missing features and limitations

Most limitations are inherited from AltDSS/DSS C-API, i.e., these are not implemented:

- `DSSProgress` from `DLL/ImplDSSProgress.pas`: would need a reimplementation depending on the target UI (GUI, text, headless, etc.). Part of it can already be handled through the callback mechanisms.
- OpenDSS-GIS features are not implemented since they're not open-source.

In general, the DLL from `dss_capi` provides more features than both the official Direct DLL and the COM object.
    
## Extra features

Besides most of the COM methods, some of the unique DDLL methods are also exposed in adapted forms, namely the methods from `DYMatrix.pas`, especially `GetCompressedYMatrix` (check the source files for more information).

Since no GUI components are used in the FreePascal DLL, we map nearly all OpenDSS errors to Python exceptions, which seems a more natural way of working in Python. You can still manually trigger an error check by calling the function `_check_for_error()` from the main class or manually checking the `DSS.Error` interface.

For general engine features, see also: [What are some features from DSS-Extensions not available in EPRI’s OpenDSS?](https://dss-extensions.org/faq.html#what-are-some-features-from-dss-extensions-not-available-in-epris-opendss)

## Installing

On all major platforms, you can install directly from pip:

```
    pip install dss-python
```

For a full experience, install the optional dependencies with:

```
    pip install dss-python[all]
```

Binary wheels are provided for all major platforms (Windows, Linux and MacOS) and many combinations of Python versions (3.7 to 3.12). If you have issues with a specific version, please open an issue about it.

After a successful installation,
