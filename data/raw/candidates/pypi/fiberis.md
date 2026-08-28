---
key: pypi/fiberis
source: pypi
name: fiberis
package: fiberis
description: Fiber Reservoir Integrated Simulator
registry_url: https://pypi.org/project/fiberis/
version: 0.4.1
last_release: '2026-01-13'
repository_url: https://github.com/shenyaojin/fibeRIS
repository_declared_in_metadata: true
license_stated: 'Copyright (c) 2026 Shenyao Jin


  Permission is hereby granted, free of charge, to any person obtaining a copy

  of this software and associated documentation files (the "Software"), to deal

  in the Software without restriction, including without limitation the rights

  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell

  copies of the Software, and to permit persons to whom the Software is

  furnished to do so, subject to the following conditions:


  The above copyright notice and this permission notice shall be included in all

  copies or substantial portions of the Software.


  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR

  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,

  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE

  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER

  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,

  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE

  SOFTWARE.'
author: Shenyao Jin
probes:
- pypi:simple-index-sweep
probe_class: domain-specific
found_by:
- search
first_seen: '2026-08-28'
---

# fibeRIS

**fibeRIS: Fiber Optic Reservoir Integrated Simulator**

`fibeRIS` is a Python-based toolkit for the analysis, simulation, and management of data relevant to reservoir engineering, with a particular focus on Distributed Fiber Optic Sensing (DFOS) data. It is developed by Shenyao Jin for research purposes.

This project provides a suite of modules for handling multi-dimensional datasets, performing signal processing, simulating pressure diffusion, and programmatically controlling the [MOOSE (Multiphysics Object-Oriented Simulation Environment)](https://mooseframework.inl.gov/) framework.

## Core Modules

### Analyzer (`fiberis.analyzer`)
The core of the data processing capabilities, providing specialized classes for different data dimensions:
*   **Data1D**: Handling 1D time-series data (e.g., gauge pressure, pumping curves).
*   **Data2D**: Handling 2D spatiotemporal data (e.g., DAS waterfall plots).
*   **Data3D**: Handling 3D volumetric data or multi-variable datasets.
*   **Data1DG**: Handling 1D geometric/spatial data (e.g., depth profiles).
*   **Geometry3D**: Handling 3D wellbore trajectories and spatial geometries.
*   **TensorProcessor**: Handling tensor data (e.g., stress/strain tensors) over time.

### Utilities (`fiberis.utils`)
A collection of helper functions for:
*   **Signal Processing**: Filtering (Butterworth), spectral analysis, outlier removal.
*   **History Management**: Logging operations and tracking data lineage.
*   **Visualization**: Plotting tools for 1D, 2D, and 3D data.

### Simulation (`fiberis.simulator` & `fiberis.moose`)
*   **Simulator**: A lightweight, independent 1D simulator for quick pressure diffusion modeling.
*   **MOOSE Wrapper**: A programmatic interface to build, run, and analyze complex multiphysics simulations using the MOOSE framework.

## Installation

You can install `fibeRIS` using pip:

```bash
pip install fiberis
```

To install from source for development:

```bash
git clone https://github.com/shenyaojin/fibeRIS.git
cd fibeRIS
pip install -e .
```

## Testing

The repository includes a comprehensive test suite based on `pytest`. To run the tests:

1.  Install test dependencies:
    ```bash
    pip install pytest numpy matplotlib scipy pandas
    ```

2.  Run tests:
    ```bash
    pytest tests/
    ```

## License

This project is licensed under MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For questions or issues, please contact Shenyao Jin at `shenyaojin@mines.edu`.
