---
key: pypi/daselement-api
source: pypi
name: daselement-api
package: daselement-api
description: Das Element Python API
registry_url: https://pypi.org/project/daselement-api/
version: 1.1.3
last_release: '2026-05-13'
repository_url: https://github.com/das-element/python-api
repository_declared_in_metadata: true
license_stated: MIT
author: Das Element <tech@das-element.com>
probes:
- pypi:simple-index-sweep
probe_class: broad-acronym
found_by:
- search
first_seen: '2026-08-28'
---

# Das Element Python API

Official Python API for the **Das Element** asset library software.

---

## 🧩 Installation

Install the package using `pip`:

```bash
pip install daselement-api
```

---

## ⚙️ Configuration

The API internally calls the command-line interface (CLI) version of _Das Element_.  
To ensure it works correctly, link the CLI executables by setting the following environment variables:

### Environment Variables

| Variable              | Description                             |
| --------------------- | --------------------------------------- |
| `DASELEMENT_CLI`      | Path to Das Element CLI executable      |
| `DASELEMENT_CLI_FULL` | Path to Das Element CLI full executable |

```bash
export DASELEMENT_CLI=/path/to/das-element
export DASELEMENT_CLI_FULL=/path/to/das-element-full
```

### Alternative Configuration

Directly define the executable paths in your Python script.
Overwrite the values of `daselement_api/manager.py` like this:

```python
from daselement_api import manager as de_manager

de_manager.EXECUTABLE_CLI = '/path/to/das-element-cli_2.2.2_lin'
de_manager.EXECUTABLE_CLI_FULL = '/path/to/das-element-cli-full_2.2.2_lin'
```

---

## 🧠 Example Usage

```python
from daselement_api import api as de

libraries = de.get_libraries()

for library, config in libraries.items():
    print(library)
    print(config)
```

---

## 📚 Documentation

For the full API reference and examples, visit:  
👉 [**docu.api.das-element.com**](http://docu.api.das-element.com)

---

## 🧾 License

This project is distributed under the terms of the license provided with **Das Element**.
