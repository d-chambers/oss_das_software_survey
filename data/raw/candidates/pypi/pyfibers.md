---
key: pypi/pyfibers
source: pypi
name: pyfibers
package: pyfibers
description: Modeling stimulation of peripheral nerve fibers
registry_url: https://pypi.org/project/pyfibers/
version: 0.9.2
last_release: '2026-08-20'
repository_url: https://github.com/wmglab-duke/pyfibers
repository_declared_in_metadata: true
license_stated: null
author: Daniel Marshall, Elie Farah, Eric Musselman, Nicole Pelot, Warren Grill
probes:
- pypi:simple-index-sweep
probe_class: broad-acronym
found_by:
- search
first_seen: '2026-08-28'
---

# PyFibers

**PyFibers Paper**: Marshall DP, Farah ES, Musselman ED, Pelot NA, Grill WM (2025) PyFibers: An open-source NEURON-Python package to simulate responses of model nerve fibers to electrical stimulation. PLoS Comput Biol 21(12): e1013764. [https://doi.org/10.1371/journal.pcbi.1013764](https://doi.org/10.1371/journal.pcbi.1013764)

[![Publication](https://img.shields.io/badge/Publication-PLoS%20Comput%20Biol-9cf)](https://doi.org/10.1371/journal.pcbi.1013764)
[![Citations](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fapi.semanticscholar.org%2Fgraph%2Fv1%2Fpaper%2FDOI%3A10.1371%2Fjournal.pcbi.1013764%3Ffields%3DcitationCount&query=%24.citationCount&label=citations)](https://badge.dimensions.ai/details/doi/10.1371/journal.pcbi.1013764)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue?logo=github)](https://github.com/wmglab-duke/pyfibers)
[![Documentation](https://img.shields.io/badge/Documentation-GitHub%20Pages-blue.svg)](https://wmglab-duke.github.io/pyfibers/)
[![DOI](https://zenodo.org/badge/1010198505.svg)](https://doi.org/10.5281/zenodo.17068760)
[![Stars](https://img.shields.io/github/stars/wmglab-duke/pyfibers.svg)](https://github.com/wmglab-duke/pyfibers/stargazers)
[![CI](https://github.com/wmglab-duke/pyfibers/workflows/CI/badge.svg)](https://github.com/wmglab-duke/pyfibers/actions)
[![PyPI](https://img.shields.io/pypi/v/pyfibers.svg)](https://pypi.org/project/pyfibers/)
[![PyPI Downloads](https://static.pepy.tech/personalized-badge/pyfibers?period=month&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads/month)](https://pepy.tech/projects/pyfibers)
[![PyPI Downloads](https://static.pepy.tech/personalized-badge/pyfibers?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads)](https://pepy.tech/projects/pyfibers)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyfibers.svg)](https://pypi.org/project/pyfibers/)

This package implements biophysical models of axons in the NEURON simulation environment using Python.
With our package, you can model the responses of axons to electrical stimulation (e.g., find the minimum current amplitude required to activate or block an action potential).
You can add your own fiber models and simulations protocols.
You can use analytical tools for extracellular potentials, or use outputs from finite element models (FEM) such as COMSOL, ANSYS, or FEniCS.

| Feature | Description |
|---------|-------------|
| **Flexible stimulation** | Support for custom waveforms and extracellular potential distributions |
| **FEM integration** | Easy usage of high-resolution potentials from finite element simulations (COMSOL, ANSYS, or other FEM software) |
| **Resampling tools** | Automatically interpolate potentials to match your fiber geometry |
| **1D and 3D fibers** | Support for both straight and curved fiber geometries |
| **Advanced analysis** | Built-in threshold search, conduction velocity measurement, and comprehensive data recording |
| **Multi-source support** | Combine potentials from multiple electrodes with different waveforms |
| **Extensible** | Add your own fiber models and simulation protocols |
| **Simulate recording** | Simple tools to calculate single fiber action potentials |
| **Library of built-in fiber models** | **MRG** (Myelinated): MRG-discrete, MRG-interpolation, Peña (Small MRG-interpolation)<br>**Sweeney** (Myelinated)<br>**Thio** (Unmyelinated): Autonomic, Cutaneous<br>**Sundt** (Unmyelinated)<br>**Tigerholm** (Unmyelinated)<br>**Rattay** (Unmyelinated)<br>**Schild** (Unmyelinated): Schild 1994, Schild 1997 |

## Installation
Note that these installation instructions are for users. Developer instructions are available in [contributing.md](https://github.com/wmglab-duke/pyfibers/blob/main/contributing.md).

It is recommended (But not required) you create a new virtual environment for PyFibers. For example, using Anaconda/Miniconda:
  - `conda create -n pyfibers`
  - `conda activate pyfibers`
1. Install NEURON and add to PATH ([https://nrn.readthedocs.io/en/latest/](https://nrn.readthedocs.io/en/latest/))
   - Make sure your NEURON and Python versions are compatible ([https://nrn.readthedocs.io/en/latest/changelog.html](https://nrn.readthedocs.io/en/latest/changelog.html))
   - Check your installation by running the following command: `python -c "import neuron; neuron.test(); quit()"`. If successful, test outputs along with "OK" should be printed to the terminal.
2. Install PyFibers from PyPI and compile the `.mod` files.
   ```bash
   pip install pyfibers
   pyfibers_compile
   ```

Some notes for `pyfibers_compile`:
- Check the NEURON output that follows for a message that the mechanisms were compiled successfully (e.g., for Windows: `nrnmech.dll was built successfully.`) While using PyFibers, if you see the `NEURON mechanisms not found in <path>.` message, this is cause for concern, as this means PyFibers cannot find the compiled mechanisms. Failed compiles will commonly cause the error message `Argument not a density mechanism name` to appear when trying to create fibers.
- Careful! Make sure that the correct NEURON installation is in your path, as the first found installation will be used for compilation. The version used for compilation must be the same version used to run PyFibers code.
- If you receive a message that the `pyfibers_compile` command is not found, find the executable for this command in the `Scripts` path of your python directory (e.g. `C:\Users\<username>\Anaconda3\envs\pyfibers\Scripts`) and run the executable (e.g., `pyfibers_compile.exe`).


## Usage
📖 **Documentation**: For detailed information on usage, see our [documentation](https://wmglab-duke.github.io/pyfibers/):
- [Tutorials](https://wmglab-duke.github.io/pyfibers/tutorials/index.html) on various operations.
- [API Documentation](https://wmglab-duke.github.io/pyfibers/autodoc/index.html) on function/class arguments and outputs.

Th
