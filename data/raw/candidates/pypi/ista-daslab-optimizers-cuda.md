---
key: pypi/ista-daslab-optimizers-cuda
source: pypi
name: ista-daslab-optimizers-cuda
package: ista-daslab-optimizers-cuda
description: CUDA kernels for ISTA-DASLab-Optimizers project developed in the Distributed Algorithms and
  Systems group (DASLab) @ Institute of Science and Technology Austria (ISTA)
registry_url: https://pypi.org/project/ista-daslab-optimizers-cuda/
version: 1.1.0
last_release: '2026-02-05'
repository_url: https://github.com/IST-DASLab/ISTA-DASLab-Optimizers-CUDA
repository_declared_in_metadata: true
license_stated: "MIT License\n        \n        Copyright (c) 2026 IST Austria Distributed Algorithms\
  \ and Systems Lab\n        \n        Permission is hereby granted, free of charge, to any person obtaining\
  \ a copy\n        of this software and associated documentation files (the \"Software\"), to deal\n\
  \        in the Software without restriction, including without limitation the rights\n        to use,\
  \ copy, modify, merge, publish, distribute, sublicense, and/or sell\n        copies of the Software,\
  \ and to permit persons to whom the Software is\n        furnished to do so, subject to the following\
  \ conditions:\n        \n        The above copyright notice and this permission notice shall be included\
  \ in all\n        copies or substantial portions of the Software.\n        \n        THE SOFTWARE IS\
  \ PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\n        IMPLIED, INCLUDING BUT NOT LIMITED\
  \ TO THE WARRANTIES OF MERCHANTABILITY,\n        FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.\
  \ IN NO EVENT SHALL THE\n        AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\n\
  \        LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\n        OUT\
  \ OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE\n        SOFTWARE.\n   \
  \     "
author: Ionut-Vlad Modoranu <ionut-vlad.modoranu@ist.ac.at>
probes:
- pypi:simple-index-sweep
probe_class: broad-acronym
found_by:
- search
first_seen: '2026-08-28'
---

# Core dependency of ISTA DAS Lab Optimization Package containing CUDA kernels
This project contains CUDA kernels designed for [ISTA-DASLab-Optimizers](https://github.com/IST-DASLab/ISTA-DASLab-Optimizers) as a 
dependency.

# Versions summary:
- **1.1.0** @ February 5th, 2026:
  - added kernels for the Sparse M-FAC Pruner
- **1.0.0** @ February 5th, 2026:
  - created this repository to decouple the CUDA kernels from the mai **ISTA-DASLab-Optimizers** project
