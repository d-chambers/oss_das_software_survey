---
key: pypi/py-open-dsse
source: pypi
name: py-open-dsse
package: py-open-dsse
description: Open source library for state estimation of a distribution network modeled in OpenDSS
registry_url: https://pypi.org/project/py-open-dsse/
version: 0.1.1
last_release: '2022-10-25'
repository_url: https://github.com/jlara6/py_open_dsse
repository_declared_in_metadata: true
license_stated: LICENSE
author: Jorge A. Lara S.
probes:
- pypi:simple-index-sweep
probe_class: broad-acronym
found_by:
- search
first_seen: '2026-08-28'
---

# py_open_dsse

It is an open-source library developed in Python for estimating distribution networks (DSSE). It communicates with the free software for the simulation of electrical networks (OpenDSS) and collects the results of power flow and distribution system parameters and executes the DSSE, obtaining an estimated state according to the type and location of measurements.

It is developed within the framework of the OpenREiD project (Integral software for simulation and optimization of electrical distribution networks), of the Instituto de Energía Eléctrica (IEE), UNSJ - CONICET, San Juan - Argentina.

**Index**

- [Installation](#id1)
- [How to use](#id2)
  - [Measurements](#id3)
    - [Definition and creation of meters](#id4)
    - [Generate metrics from OpenDSS results](#id5)
  - [Run the state estimation algorithm](#id6)
  - [Sample tests](#id7)
- [License](#id8)

<div id='id1' />
## Installation

With pip

``pip install py-open-dsse``

Without pip, clone or download the repository, in the dist folder is the .whl file, copy the location of the file, and in the CMD:

``pip install {path-save-files}/py_open_dsse-{version}-py3-none-any.whl’``

<div id='id2'/>

## How to use  <a name="id1"></a>

First, in the IDE (Integrated Development Environment) of preference, we import the library:

```Python
import py_open_dsse
```

The object class that contains all the functions of the library is activated as follows:

```Python
dsse = py_open_dsse.init_DSSE()
```

The class ``init_DSSE()``, has default values as shown in table 1 and can be modified as appropriate.

**Table 1.** Description and attributes of function ``init_DSSE()``
| **Parameters** | **Description** | **Default value** |
|:---:|---|:---:|
| ``Sbas3ph_MVA`` | Three-phase system base power     | ``30`` |
| ``tolerance`` | Convergence tolerance of selected algorithm | ``1e-3`` |
| ``max_iter`` | Maximum number of iterations of the selected algorithm | ``30`` |
| ``init_values`` | Initial values for state estimation. With ``flat`` start with 1.0 p.u. / 0° on all buses and with ``dss`` start with OpenDSS voltage and angle results| ``flat`` |

Once the class is initialized, we can use the functions described below.

<div id='id3' />

### Measurements

<div id='id4' />

#### Definition and creation of meters

The library supports meters and their respective error variance described in Table 2.

**Tabla 2.** Measurement type of the ``py_open_dsse`` library.

|              **Meter**                 |                                **Description**                |
|:--------------------------------------:|---------------------------------------------------------------|
| $\left\|V_{i}\right\|$                 | Node voltage magnitude.                                       |
| $PQ_{ft}$                              | Branch power flow                                             |
| $\left\|I_{ft}\right\|$                | Magnitude of branch current.                                  |
| $PQ_{i}^{SM}$                          | Injection power or node consumption obtained by a smart meter |
| $PQ_{i}^{0}$                           | Passive node or zero injection power.                         |
| $PQ_{i}^{PSD}$                         | Artificial node injection power known as pseudo-measurement   |
| $\left\|V_{i}\right\|\angle \theta$    | Voltage phasor measurement                                    |
| $\left\|I_{ft}\right\|\angle \delta$   | Current phasor measurement                                              |

The measurement data per phase **𝜌 (1, 2, 3)** and measurement error variance ``Rii`` of a network modeled in OpenDSS. They must be entered in the ``MEAS_Bus_i.json``, ``MEAS_Elem_ft.json``, ``MEAS_Bus_i_PMU.json`` and ``MEAS_Elem_ft_PMU.json`` files. The ``.json`` measurement files without data are generated with the ``empty_MEAS_files()`` function and the parameters from table 3 must be entered.

**Table 3.** Parameters and description of ``empty_file_MEAS()`` function
|    **Parameter**   |                           **Description**                         |**Default value** |
|:------------------:|-------------------------------------------------------------------|:----------------:|
| ``DSS_path``       | A path of the ``.DSS`` files of the circuit modeled in OpenDSS    | ``None ``        |
| ``MEAS_path_save`` | Path where the measurement ``.json`` files will be saved          | ``None ``        |

The description of the identifiers that can be modified is detailed in tables 4, 5, 6, and 7. The other identifiers in the ``.json`` files, are node characteristics or elements extracted from the circuit modeled in OpenDSS, these data should not be modified since they would affect the result of the state estimation algorithm.

**Table 4.** Description of identifiers of the ``MEAS_Bus_i.json`` file.

| **Identifier**     |                                       **Description**                         |
|:---------------------:|-------------------------------------------------------------------------------|
| ``STS_Vm``            | Status (1: Enabled, 0: Disabled)                                              |
| ``Rii_Vm``            | Variance of voltage magnitude measurement error.                              |
| ``Vρm(pu)``           | Measurement of voltage magnitude voltage in phase 𝜌.                          |
| ``STS_PQd(SM)``       | Status (1: Enabled, 0: Disabled)                                              |
| ``Rii_SM``            | Measurement error variance of injection power or consumption of a smart meter.|
| ``STS_PQd(0)``        | Status (1: Enabled, 0: Disabled)                                              |
| ``Rii_0``             | Zero or passive injection power measurement error variance.                   |
| ``STS_PQd(Psd)``      | Status (1: Enabled, 0: Disabled)                                              |
| ``Rii_Psd``           | Measurement error variance of pseudo power injection measur
