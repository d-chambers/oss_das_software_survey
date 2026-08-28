---
key: pypi/openpy-fx-tools-dss
source: pypi
name: openpy-fx-tools-dss
package: openpy-fx-tools-dss
description: Python functions for extracting, executing routines, etc. from projects modeled in OpenDSS
registry_url: https://pypi.org/project/openpy-fx-tools-dss/
version: 0.1.6
last_release: '2022-12-29'
repository_url: https://github.com/jlara6/OpenPy-fx-tools-DSS
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

# OpenPy-fx-tools-DSS
Python functions for extracting, executing routines, etc. from projects modeled in OpenDSS
# Install
With pip

``pip install openpy-fx-tools-dss``

# How to use
First, in the IDE (Integrated Development Environment) of preference, we import the library:

```Python
import openpy_fx_tools_dss as fx_dss
```
## Examples
The library has IEEE example circuits (Table 1), which can be found in the OpenDSS installation files.
For the example files the class ``examples_lib()`` is called: 

**Table 1.** Sample tests

| **Name**   | **Option** | **DSS files** | **xlsx file** |
|------------|------------|---------------|---------------|
| 13BusIEEE  | 1          | x             | x             |
| 37BusIEEE  | 2          | x             | x             |
| 123BusIEEE | 3          | x             | x             |


```Python
test = fx_dss.examples_lib()
```

To use the .DSS files:

``DSS_path = test.load_examples_DSS()``

To use .xlsx file:

``xlsx_path = test.load_examples_xlsx()``

## OpenDSS to xlsx and vice versa 
The functions that generate OpenDSS scripts to a .xlsx file and vice versa are inside the ``xlsx_DSS_xlsx()`` class and are called in the following way:

``xlsx = fx_dss.xlsx_DSS_xlsx()``
### Template xlsx

An .xlsx template with the OpenDSS elements is created by calling the ``create_template_xlsx`` function as follows:

```Python
xlsx.create_template_xlsx(
    path_save: str = None, 
    prj_name: str = 'default', 
    elem_list: list = [], 
    all_elem: bool = True
)
```
### xlsx to OpenDSS
The circuit data is entered in the .xlsx template. Each sheet of the template corresponds to the elements that are modeled in OpenDSS. When generating the OpenDSS scripts, only the cells that are not empty are considered.
For this purpose, the ``xlsx_to_OpenDSS`` function is called as follows:

```Python
xlsx.xlsx_to_OpenDSS(
    xlsx_path=xlsx_path['xlsx_path'],
    path_save=xlsx_path['path_save'],
    prj_name=DSS_path['prj_name']
)
```

**Important:**

* Do not alter the names of the sheets, and columns, since the element will not be taken into account. 
* The form of data entry must coincide with the OpenDSS specifications.




### OpenDSS to xlsx
From an OpenDSS file, the xlsx template can be generated. For this purpose, the ``OpenDSS_to_xlsx`` function is used as follows:

```Python
xlsx.OpenDSS_to_xlsx(
    DSS_path=DSS_path['DSS_path'],
    path_save=DSS_path['path_save'],
    prj_name=DSS_path['prj_name']
)
```

# License
License: CC BY-NC-SA 4.0

<a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png" /></a><br />

This work has a license <a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/">Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License</a>.
