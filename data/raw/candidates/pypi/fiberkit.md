---
key: pypi/fiberkit
source: pypi
name: fiberkit
package: fiberkit
description: Fiber Kit - moment curvature analysis for reinforced concrete, steel, wood, etc.
registry_url: https://pypi.org/project/fiberkit/
version: 2.0.0
last_release: '2025-05-06'
repository_url: https://github.com/wcfrobert/fkit
repository_declared_in_metadata: true
license_stated: null
author: wcfrobert <temprobertdev@gmail.com>
probes:
- pypi:simple-index-sweep
probe_class: broad-acronym
found_by:
- search
first_seen: '2026-08-28'
---

<h1 align="center">
  <br>
  <img src="https://raw.githubusercontent.com/wcfrobert/fkit/refs/heads/master/doc/logo.png" alt="logo" style="zoom:50%;" />
  <br>
  Fiber Section Analysis in Python
  <br>
</h1>
<p align="center">
Define fiber material properties, create section, perform moment-curvature and PM interaction analysis with ease.
</p>


<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/hello_demo.png?raw=true" alt="demo" style="width: 100%;" />
</div>



- [Introduction](#introduction)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [Notes and Assumptions](#notes-and-assumptions)
- [License](#license)




## Introduction

fkit (fiber-kit) is a section analysis program implemented in Python. It is powerful, flexible, and easy-to-use. Perform **moment-curvature** and **P+M interaction** analysis with very few lines of code. Originally meant for reinforced concrete sections, it was later extended to all material type (e.g. wood, steel, FRPs, anything that can be defined by a stress-strain curve). 

Notable Features:

* Large selection of material models (Hognestad, Mander, Todeschini, Ramberg-Osgood, Menegotto-Pinto, Bilinear, Trilinear, Multilinear)
* Moment curvature analysis
* P+M interaction analysis
* Cracked moment of inertia calculations
* Fast, Intuitive to use, and fully transparent. View stress/strain data of every fiber at each load step
* Great looking visualizations


<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/demo.gif?raw=true" alt="demo" style="width: 100%;" />
</div>


**[New in v2.0.0]** Interactive 3D plot powered by Plotly:


<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/demo2.gif?raw=true" alt="demo" style="width: 100%;" />
</div>



<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/steel_demo.png?raw=true" alt="demo" style="width: 100%;" />
</div>





## Quick Start

Run `main_quickstart.py`:

```python
import fiberkit as fkit

# define concrete and steel fibers
fiber_concrete = fkit.patchfiber.Hognestad(fpc=4, take_tension=True)
fiber_steel    = fkit.nodefiber.Bilinear(fy=60, Es=29000)

# create a rectangular beam section with SectionBuilder
section1 = fkit.sectionbuilder.rectangular(width = 18, 
                                           height = 24, 
                                           cover = 2, 
                                           top_bar = [0.6, 4, 1, 0], #[bar_area, nx, ny, y_spacing]
                                           bot_bar = [0.6, 4, 2, 3], #[bar_area, nx, ny, y_spacing] 
                                           concrete_fiber = fiber_concrete, 
                                           steel_fiber = fiber_steel)

# moment curvature
MK_results = section1.run_moment_curvature(phi_target=0.0003)
df_nodefibers, df_patchfibers = section1.get_all_fiber_data()

# cracked moment of inertia
Icr_results = section1.calculate_Icr(Es=29000, Ec=3605)

# PM Interaction surface analysis
PM_results = section1.run_PM_interaction(fpc=4, fy=60, Es=29000)

# plot results
fkit.plotter.plot_MK(section1)
fkit.plotter.plot_PM(section1)
fkit.plotter.plot_Icr(section1)
fkit.plotter.plot_MK_3D(section1) # NEW IN VERSION 2.0.0
```

The script above uses US imperial unit **(kips, in, ksi)**. You may also use SI units **(N, mm, MPa)**. The quick start script produces the following plots:

<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/demo2.png?raw=true" alt="demo" style="width: 80%;" />
</div>

<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/demo3.png?raw=true" alt="demo" style="width: 80%;" />
</div>

<div align="center">
  <img src="https://github.com/wcfrobert/fkit/blob/master/doc/Icr.png?raw=true" alt="demo" style="width: 80%;" />
</div>





## Installation

**Option 1: Anaconda Python**

This is the simplest way to get started.

1. Download Anaconda python distribution: [https://www.anaconda.com/download](https://www.anaconda.com/download)
2. Download this package (click the green "Code" button and download zip file or download the latest release)
3. Open and run "main.py" in Anaconda's Spyder IDE

**Option 2: Regular Python**

1. Download python: [https://www.python.org/](https://www.python.org/)
2. Download this project to a folder of your choosing
    ```
    git clone https://github.com/wcfrobert/fkit.git
    ```
3. Change directory into where you downloaded fkit
    ```
    cd fkit
    ```
4. Create virtual environment
    ```
    py -m venv venv
    ```
4. Activate virtual environment
    ```
    venv\Scripts\activate
    ```
6. Install requirements
    ```
    pip install -r requirements.txt
    ```
7. run fkit
    ```
    py main.py
    ```

Note that pip install is available.

```
pip install fiberkit
```

Fiberkit was developed using python 3.12 (any version above 3.7 will probably work as well) with the following dependencies.

* Numpy
* Matplotlib
* Pandas



## Usage

`main_fiber.py` - illustrates the available material models within fkit. 

* **Hognestad et al (1951)** - General purpose concrete
* **Mander et al (1988)** - Recommended for confined concrete

* **Todeschini et al (1964)** - Recommended for unconfined concrete

* **Bilinear** - Simple bilinear model

* **Multilinear: Rex & Easterling (1996)**  - Six linear regions tracing out the recognizable steel stress-strain curve

* **RambergOsgood** - Smooth power function. Can be used to fit experimental data

* **MenegottoPinto** - Smooth power function. Slightly faster and more robust than RambergOsgood as no Newton-Raphson iteration is needed

* **Custom_Trilinear** - A highly customizable trilinear model defined by three points

Each of the eight material models above can be assigned to either a Node fiber or a Patch fiber. **Patch fibers** have 4 vertices and occupies some area geometrically. On the other hand, **node fibers** are d
