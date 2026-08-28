---
key: pypi/pydsstools
source: pypi
name: pydsstools
package: pydsstools
description: Python library to read-write HEC-DSS database file
registry_url: https://pypi.org/project/pydsstools/
version: 3.1.0
last_release: '2026-06-06'
repository_url: https://github.com/gyanz/pydsstools
repository_declared_in_metadata: true
license_stated: "MIT License\n        \n        Copyright (c) 2018 Gyan Basyal\n        \n        Permission\
  \ is hereby granted, free of charge, to any person obtaining a copy\n        of this software and associated\
  \ documentation files (the \"Software\"), to deal\n        in the Software without restriction, including\
  \ without limitation the rights\n        to use, copy, modify, merge, publish, distribute, sublicense,\
  \ and/or sell\n        copies of the Software, and to permit persons to whom the Software is\n     \
  \   furnished to do so, subject to the following conditions:\n        \n        The above copyright\
  \ notice and this permission notice shall be included in all\n        copies or substantial portions\
  \ of the Software.\n        \n        THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND,\
  \ EXPRESS OR\n        IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\n   \
  \     FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\n        AUTHORS OR\
  \ COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\n        LIABILITY, WHETHER IN AN ACTION\
  \ OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\n        OUT OF OR IN CONNECTION WITH THE SOFTWARE OR\
  \ THE USE OR OTHER DEALINGS IN THE\n        SOFTWARE.\n        "
author: Gyan Basyal <gyanBasyalz@gmail.com>
probes:
- pypi:simple-index-sweep
probe_class: broad-acronym
found_by:
- search
first_seen: '2026-08-28'
---

# pydsstools

[![Documentation Status](https://readthedocs.org/projects/pydsstools/badge/?version=latest)](https://pydsstools.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/pydsstools.svg)](https://badge.fury.io/py/pydsstools)
[![Python versions](https://img.shields.io/pypi/pyversions/pydsstools?logo=python)](https://pypi.org/project/pydsstools/)
[![NumPy](https://img.shields.io/badge/NumPy-1.x%20%7C%202.x-blue?logo=numpy)](https://numpy.org)

A Cython-based Python library for reading and writing [HEC-DSS](http://www.hec.usace.army.mil/software/hec-dssvue/) database files.

## Features

- Regular and irregular time-series
- Paired data series
- Array records
- Text records
- Binary records (FILE, IMAGE, BLOB)
- Spatial grid records (HRAP, Albers/SHG, Specified, Undefined)
- Location and Vertical Datum information
- Compatible with 64-bit Python on Windows and Linux

## Related Projects

- [dssvue](https://github.com/gyanz/dssvue) — GUI for HEC-DSS
- [hecdss-rs](https://github.com/gyanz/hecdss-rs) — Rust bindings for HEC-DSS

## Changes

See the [changelog](https://github.com/gyanz/pydsstools/blob/master/CHANGES.MD).

## Documentation

Read the full documentation at [pydsstools.readthedocs.io](https://pydsstools.readthedocs.io/).

## Installation

See the [installation guide](docs/source/installation.md).

## Contributing

All contributions, bug reports, bug fixes, documentation improvements, enhancements, and ideas are welcome.
See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines, the versioning policy, and how to report bugs or request features.
Feel free to ask questions via [email](mailto:gyanBasyalz@gmail.com).

## License

This program is free software: you can modify and/or redistribute it under the [MIT](LICENSE) license.

## Sponsorship

If pydsstools is useful in your work, consider sponsoring its development via GitHub Sponsors.
Support helps with adding new featues, ongoing maintenance, testing, and compatibility with new Python/NumPy releases.
