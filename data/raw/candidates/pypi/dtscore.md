---
key: pypi/dtscore
source: pypi
name: dtscore
package: dtscore
description: DTS Core Services
registry_url: https://pypi.org/project/dtscore/
version: 2.5.6
last_release: '2026-08-28'
repository_url: null
repository_declared_in_metadata: false
license_stated: null
author: '"D. Smith" <dgsmith.hpot@gmail.com>'
probes:
- pypi:simple-index-sweep
probe_class: broad-acronym
found_by:
- search
first_seen: '2026-08-28'
---

# Prep

See: https://packaging.python.org/en/latest/tutorials/packaging-projects/

## Setup Testpypi and Pypi (one time only)
 
 .pypirc file in $home (c:/users/dgsmith) directory<br/>

 ```
[testpypi]
username = __token__
password = token from test.pypi.org goes here
 ```

## Project folder structure

```
pyexample
├── src
│   ├── pyexample_USERNAME_HERE
│   │   ├── __init__.py
│   │   ├── module_mpi4py_1.py
│   │   ├── module_numpy_1.py
│   │   └── module_numpy_2.py
│   │-- module2_USERNAME_HERE
│   │   ├── __init__.py
│   │   ├── ...
├── tests
│   ├── test1.py
├── .gitignore
├── LICENSE
├── pyproject.toml
├── README.md
```

## Other Steps

* Create a virtual environment (.venv)
* pip install any dependencies
* pip freeze to create requirements.txt

## Tools install

```
python -m pip install --upgrade pip
python -m pip install --upgrade build
python -m pip install --upgrade twine
```

## Create pyproject.toml
under project folder create pyproject.toml

```
[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"

[project]
name = "dtscore_dsmi"
version = "0.0.2"
authors = [
  { name="D. Smith", email="dgsmith.hpot@gmail.com" },
]
description = "DTS Core Services"
readme = "README.md"
requires-python = ">= 3.10"
dependencies = [
    'requests>=2.31',
    'importlib-metadata; python_version>="3.10"',
    'urllib3>=2.0'
]
classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Microsoft :: Windows :: Windows 11',
        'Programming Language :: Python :: 3.10',
]
```

## Build the distribution

* delete any previous versions from the dist folder
* check version number in pyproject.toml

| Command | Result |
| --- | --- |
| python -m build |builds the application<br/> |
| twine upload --repository testpypi dist/* |upload distribution to testpypi, or<br/> |
| twine upload dist/* |upload distribution to pypi |
