---
key: pypi/fiberfusing
source: pypi
name: FiberFusing
package: fiberfusing
description: A package fiber fusing configuration simulating the transverse fusion of fiber optics.
registry_url: https://pypi.org/project/fiberfusing/
version: 1.9.5
last_release: '2025-08-27'
repository_url: https://github.com/MartinPdeS/FiberFusing
repository_declared_in_metadata: true
license_stated: "MIT License\n        \n        Copyright (c) 2020 Martin de Sivry\n        \n       \
  \ Permission is hereby granted, free of charge, to any person obtaining a copy\n        of this software\
  \ and associated documentation files (the \"Software\"), to deal\n        in the Software without restriction,\
  \ including without limitation the rights\n        to use, copy, modify, merge, publish, distribute,\
  \ sublicense, and/or sell\n        copies of the Software, and to permit persons to whom the Software\
  \ is\n        furnished to do so, subject to the following conditions:\n        \n        The above\
  \ copyright notice and this permission notice shall be included in all\n        copies or substantial\
  \ portions of the Software.\n        \n        THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY\
  \ OF ANY KIND, EXPRESS OR\n        IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\n\
  \        FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\n        AUTHORS\
  \ OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\n        LIABILITY, WHETHER IN AN ACTION\
  \ OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\n        OUT OF OR IN CONNECTION WITH THE SOFTWARE OR\
  \ THE USE OR OTHER DEALINGS IN THE\n        SOFTWARE.\n        "
author: Martin Poinsinet de Sivry-Houle <martin.poinsinet.de.sivry@gmail.com>
probes:
- pypi:simple-index-sweep
probe_class: domain-specific
found_by:
- search
first_seen: '2026-08-28'
---

FiberFusing
===========

|logo|


.. list-table::
   :widths: 10 25 25 25
   :header-rows: 0

   * - Meta
     - |python|
     - |docs|
     - |colab|
   * - Testing
     - |ci/cd|
     - |coverage|
     -
   * - PyPi
     - |PyPi|
     - |PyPi_download|
     -
   * - Anaconda
     - |anaconda|
     - |anaconda_download|
     -


FiberFusing is a Python package designed for simulating the fiber fusing process. With this tool, users can define an initial fiber configuration and simulate the fusion process as a function of the fusion degree parameter.


As follows, an example of 3x3 fused fiber.

.. code-block:: python


   from FiberFusing import Geometry, DomainAlignment, BackGround
   from FiberFusing.fiber import FiberLoader
   from FiberFusing.profile import Profile, StructureType

   air_background = BackGround(refractive_index=1.0)

   profile = Profile()

   profile.add_structure(
      structure_type=StructureType.CIRCULAR,
      number_of_fibers=3,
      fusion_degree=0.4,
      fiber_radius=62.5e-6
   )

   profile.refractive_index = 1.4444

   fiber_loader = FiberLoader()
   fibers = [
      fiber_loader.load_fiber('SMF28', clad_refractive_index=profile.refractive_index, position=core_position)
      for core_position in profile.cores
   ]

   # Set up the geometry with the defined background, profile structure, and resolution
   geometry = Geometry(
      x_bounds=DomainAlignment.CENTERING,
      y_bounds=DomainAlignment.CENTERING,
      resolution=350
   )

   # Add the fibers to the geometry
   geometry.add_structure(air_background, profile, *fibers)

   geometry.initialize()

   # Plot the resulting geometry
   geometry.plot()

|example_3x3|


----

Documentation
**************
For the most up-to-date documentation, visit the official `FiberFusing Docs <https://martinpdes.github.io/FiberFusing/latest/>`_ or click the badge below:

|docs|

----

Installation
************
Getting started with FiberFusing is easy. Simply install via `pip`:

.. code-block:: bash

    pip install FiberFusing

|PyPi|

----

Testing
*******
To run tests locally after cloning the GitHub repository, you’ll need to install the dependencies and run the following commands:

.. code-block:: bash

    git clone https://github.com/MartinPdeS/FiberFusing.git
    cd FiberFusing
    pip install FiberFusing[testing]
    pytest

For more detailed testing instructions, consult the documentation.

----

Coding examples
***************
Explore a wide range of examples demonstrating the usage of FiberFusing in the `Examples section <https://martinpdes.github.io/FiberFusing/gallery/index.html>`_ of the documentation.

----

Contributing & Contact
***********************
FiberFusing is an open project and collaboration is encouraged! If you're interested in contributing or have any questions, feel free to reach out.

**Author:** `Martin Poinsinet de Sivry-Houle <https://github.com/MartinPdeS>`_
**Email:** `martin.poinsinet-de-sivry@polymtl.ca <mailto:martin.poinsinet-de-sivry@polymtl.ca?subject=FiberFusing>`_

We welcome feedback and contributions to improve FiberFusing and expand its capabilities.

----

.. |python| image:: https://img.shields.io/pypi/pyversions/fiberfusing.svg
   :target: https://www.python.org/
   :alt: Python version

.. |PyPi| image:: https://badge.fury.io/py/FiberFusing.svg
   :target: https://pypi.org/project/FiberFusing/
   :alt: PyPi

.. |PyPi_download| image:: https://img.shields.io/pypi/dm/fiberfusing.svg
   :target: https://pypistats.org/packages/fiberfusing
   :alt: PyPi download statistics

.. |logo| image:: https://github.com/MartinPdeS/FiberFusing/raw/master/docs/images/logo.png
   :alt: FiberFusing's logo

.. |docs| image:: https://github.com/martinpdes/fiberfusing/actions/workflows/deploy_documentation.yml/badge.svg
   :target: https://martinpdes.github.io/FiberFusing/
   :alt: Documentation Status

.. |coverage| image:: https://raw.githubusercontent.com/MartinPdeS/FiberFusing/python-coverage-comment-action-data/badge.svg
   :target: https://htmlpreview.github.io/?https://github.com/MartinPdeS/FiberFusing/blob/python-coverage-comment-action-data/htmlcov/index.html
   :alt: Unittest coverage

.. |ci/cd| image:: https://github.com/martinpdes/fiberfusing/actions/workflows/deploy_coverage.yml/badge.svg
   :target: https://martinpdes.github.io/FiberFusing/actions
   :alt: Unittest Status

.. |anaconda_download| image:: https://anaconda.org/martinpdes/fiberfusing/badges/downloads.svg
   :alt: Anaconda downloads
   :target: https://anaconda.org/martinpdes/fiberfusing

.. |anaconda| image:: https://anaconda.org/martinpdes/fiberfusing/badges/version.svg
   :alt: Anaconda version
   :target: https://anaconda.org/martinpdes/fiberfusing

.. |example_3x3| image:: https://github.com/MartinPdeS/FiberFusing/raw/master/docs/images/example_3x3.png
   :alt: Example for 3 fiber structure

.. |colab| image:: https://colab.research.google.com/assets/colab-badge.svg
   :target: https://colab.research.google.com/github/MartinPdeS/FiberFusing/blob/master/notebook.ipynb
