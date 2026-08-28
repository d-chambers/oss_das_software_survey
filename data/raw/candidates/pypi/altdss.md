---
key: pypi/altdss
source: pypi
name: altdss
package: altdss
description: Modern, detailed Python interface/bindings and tools based on the AltDSS/DSS C-API project,
  the alternative OpenDSS implementation from DSS-Extensions.org. Tries to expose all OpenDSS objects,
  bulk operations and many details which previously required using the Text interface, or just weren't
  available.
registry_url: https://pypi.org/project/altdss/
version: 0.2.4
last_release: '2026-02-26'
repository_url: https://github.com/dss-extensions/AltDSS-Python
repository_declared_in_metadata: true
license_stated: 'BSD 3-Clause License  Copyright (c) 2017-2024, Paulo Meira Copyright (c) 2017-2024, AltDSS-Python
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

# AltDSS-Python

*Modern Python bindings for an alternative implementation of EPRI's OpenDSS*

[![PyPI](https://img.shields.io/pypi/v/altdss)](https://pypi.org/project/altdss/) <img alt="Supports Linux" src="https://img.shields.io/badge/Linux-FCC624?logo=linux&logoColor=black"> <img alt="Supports macOS" src="https://img.shields.io/badge/macOS-000000?logo=apple&logoColor=white"> <img alt="Supports Microsoft Windows" src="https://img.shields.io/badge/Windows-0078D6?logo=windows&logoColor=white">

AltDSS-Python, or just `altdss` when used from Python, builds on the DSS-Python backend infrastructure and experience shared in both DSS-Python and OpenDSSDirect.py to cover many aspects that the classic OpenDSS APIs (DSS-Python, OpenDSSDirect.py, official OpenDSS COM implementation, and anything based on the DCSL/OpenDSSDirect.DLL) cannot achieve comfortably or with good performance. Many features are only possible due to our alternative engine (AltDSS), used through the [AltDSS/DSS C-API](https://github.com/dss-extensions/dss_capi) library. 

This package is available for Windows, Linux and macOS, including Intel and ARM processes, both 32 and 64-bit. As such, it enables OpenDSS to run in many environments the official implementation cannot, from a Raspberry Pi to a HPC cluster, and cloud environments like Google Colab (some of our notebooks examples are ready-to-run on Colab).

AltDSS-Python is part of DSS-Extensions, a larger effort to port the original OpenDSS to support more platforms (OSs, processor architectures), programming languages, and extend both the OpenDSS engine and API, represented in the AltDSS engine:

<p align="center">
    <img alt="Overview of related projects" src="https://github.com/dss-extensions/dss-extensions/blob/main/images/repomap.png?raw=true">
</p>

For alternatives for other programming languages, including in MATLAB, C++, C#/.NET, Rust and Go, please check [https://dss-extensions.org/](https://dss-extensions.org/) and our hub repository at [dss-extensions/dss-extensions](https://github.com/dss-extensions/dss-extensions) for more documentation, discussions and the [FAQ](https://github.com/dss-extensions/dss-extensions#faq).

<center>

```mermaid
flowchart TD
    C["AltDSS engine/DSS C-API\n(libdss_capi)"] --> P["DSS-Python: Backend"]
    P --- DSSPY["DSS-Python\n(dss package)"]
    P --- ODDPY["OpenDSSDirect.py\n(opendssdirect package)"]
    P --- ALTDSSPY["AltDSS-Python\n(altdss package)"]
```

</center>

AltDSS-Python is one of three Python projects under DSS-Extensions. See [DSS-Extensions — OpenDSS: Overview of Python APIs](https://dss-extensions.org/python_apis.html) for a brief comparison between these and the official COM API. Both OpenDSSDirect.py and DSS-Python expose the classic OpenDSS API (closer to the COM implementation). AltDSS-Python, on the other hand, exposes all OpenDSS objects, batch operations, and a more intuitive API. If required, users can mix all three packages in the same project to access some of their unique features, or just to avoid changing legacy/stable code.

Since the base code is shared, other features from [DSS-Python such as plotting](https://dss-extensions.org/DSS-Python/examples/Plotting.html) can be used here. Other examples from DSS-Python or OpenDSSDirect.py can be adapted quite easily too.

## What is AltDSS?

To avoid confusion between the official OpenDSS provided by EPRI and the alternative, unofficial implementation provided by the DSS-Extensions group of projects, our implementation of the OpenDSS engine, exposed as a software library (e.g. DLL or shared object), will be slowly renamed to AltDSS engine. The classic parts of our DSS C-API is still in place and will remain for usage in DSS-Python and OpenDSSDirect.py.

The "Alt" prefix tries to encompass a few aspects:
- An alternative implementation
- A new approach for the API
- A more searchable name (just "DSS" is too generic nowadays), and easier to cite.

What didn't change:
- It's the same engine that's been developed since 2018 on DSS-Extensions.
- Our cross-validation with the official OpenDSS implementation continues.
- If you have used DSS C-API, DSS-Python, DSS MATLAB, DSS Sharp, OpenDSSDirect.jl or OpenDSSDirect.py since 2018 or 2019 (depending on the package), you were already using "AltDSS".

If you somehow need compatibility with the official OpenDSS COM implementation at API level, prefer to stay with the classic API implementations such DSS-Python and OpenDSSDirect.py, and avoid anything marked as "API Extension".

## What is AltDSS-Python?

AltDSS-Python is a new Python package that goes along with DSS-Python and OpenDSSDirect.py to provide a further Pythonic experience.

This new package uses many unique aspects of our alternative implementation of the engine and of the API to expose all types of DSS objects currently implemented in AltDSS.

When referring to Python, we will call AltDSS-Python just AltDSS, for short. The same will happen for other future language bindings based on the same concepts.

Notable features are:
- **All DSS objects** implemented in our implementation of the OpenDSS engine are exposed.
- Avoids the active element idiom. Users can interact with multiple objects without requiring to activate them.
- The original separate APIs for general circuit elements, PC elements, PD elements and others are encapsulated together with the access to the DSS properties in a single context. We hope to achieve a better autocomplete experience in IDEs and easier discoverability of the available functions. For example, a [`Line` object](https://dss-extensions.org/AltDSS-Python/apidocs/altdss/altdss.Line.html#altdss.Line.Line) contains all the DSS properties the the Line object (as Python properties), plus inherited methods/properties from common DSS objects, Circuit element objects, and PD element objects.
- Due to duplication, the access to the DSS properties replace many of the old COM-style properties. The names of the properties in Python th
