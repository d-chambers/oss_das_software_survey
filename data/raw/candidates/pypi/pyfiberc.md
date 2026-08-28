---
key: pypi/pyfiberc
source: pypi
name: pyfiberc
package: pyfiberc
description: fibred rc sections tool
registry_url: https://pypi.org/project/pyfiberc/
version: 0.0.20
last_release: '2026-07-31'
repository_url: null
repository_declared_in_metadata: false
license_stated: null
author: Marco Melcarne <mmelcarne@systra.com>, Luigi Luis Paone <ppc.luigi.paone@gmail.com>, Claudia Orrico
  <corrico@systra.com>
probes:
- pypi:simple-index-sweep
probe_class: broad-acronym
found_by:
- search
first_seen: '2026-08-28'
---

# pyfiberc

**pyfiberc** is an analysis tool for **Fiber-Reinforced Concrete (FRC)** rectangular
sections. It checks sections under axial force and bending at the Ultimate (ULS/SLU)
and Serviceability (SLS/SLE) limit states, generates N‑M interaction domains, and
produces a LaTeX/PDF calculation report.

It is built on top of [**pycivil**](https://pypi.org/project/pycivil/), which provides
the structural core: section and rebar modelling, loads and limit states, the solver
framework, and the LaTeX report toolchain.

## Features

- **ULS (SLU) N‑M check** — interaction domain for the fibered section, with optional
  shear-driven reduction of the residual tensile strength.
- **SLS (SLE) N‑M check** — domain checks for characteristic and quasi-permanent
  load combinations, with constitutive tension-law support.
- **FRC material laws** per **CNR DT 204 / Linee Guida C.S.LL.PP. 2022**,
  **fib Model Code 2010**, and **EN 1992‑1‑1:2023** — residual design strengths
  (`fFtud`, `fFtld`) and the piecewise tension constitutive law are computed
  automatically from `fR1k`/`fR3k` and the selected code.
- **PDF report** — section geometry plot, interaction domains, and check results
  rendered through pycivil's LaTeX engine.

## Installation

The package targets Python **3.11–3.13** and is managed with
[`uv`](https://docs.astral.sh/uv/).

### 1. Install `uv`

**Windows** (Terminal on Win11, PowerShell on Win10):

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
setx UV_NATIVE_TLS true
```

Restart the terminal so `uv` is on `PATH` and the TLS setting takes effect.

**Linux / macOS**:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Install `pyfiberc`

From the directory where you want the environment to live:

```bash
uv init --python 3.12
uv add pyfiberc
```

> **SYSTRA users**: to pull packages from the internal index, point `UV_INDEX_URL`
> at the group endpoint with your personal access token:
>
> ```powershell
> setx UV_INDEX_URL https://__token__:<YOUR_TOKEN_HERE>@gitlab.com/api/v4/groups/9596324/-/packages/pypi/simple
> ```

## Usage example

### Running the solver on a section model

The typical workflow is: build the input model (a `FrcRecSectionInput`) by hand,
save it as JSON, then run the solver from Python. The `criteria` field of the input selects
which checks run (`"SLU-NM"`, `"SLE-NM"`, ...). Sample inputs live in
[`tests/input_benchmarks/`](tests/input_benchmarks/).

```python
import json
from pathlib import Path

from pyfiberc.solver import FRCSolver
from pyfiberc.tools.models import FrcRecSectionInput, UUIDEncoder

# Load a section model from JSON
data = json.loads(Path("section.json").read_text())
model = FrcRecSectionInput(**data)

# Run the checks; plots and the report are written into the job path
job = Path("job-001")
job.mkdir(exist_ok=True)

solver = FRCSolver(model)
solver.setJobPath(job)
solver.run()

# Inspect or persist the results
output = solver.getModelOutput()
(job / "results.json").write_text(
    json.dumps(output.model_dump(), indent=4, cls=UUIDEncoder)
)

# Build the LaTeX/PDF calculation report
solver.buildReport()
```

After `run()`, the job directory contains the section geometry plot and the
interaction-domain plots; `buildReport()` adds the compiled PDF.

### Defining an FRC material

`FiberConcrete` is a pydantic model: pick a design code (`normativa`), give the
residual flexural strengths `fR1k`/`fR3k` and the code parameters, and the design
values come out as computed fields.

```python
from pyfiberc.tools.models import FiberConcrete
from pyfiberc.materials import LawCode

frc = FiberConcrete(
    description="C25/30 + steel fibers",
    normativa=LawCode.CODE_ITA_LG2022,  # Linee Guida C.S.LL.PP. 2022
    fR1k=8.0,        # residual strength at CMOD = 0.5 mm [MPa]
    fR3k=8.8,        # residual strength at CMOD = 2.5 mm [MPa]
    k0=0.5, kg=1.0,  # LG 2022 parameters
    efu=0.01,        # ultimate tensile strain [-]
    lcs=300.0,       # sectional characteristic length [mm]
    d1=300.0, d2=300.0, d3=300.0,  # FEM analysis parameters [mm]
)

print(frc.fFtud, frc.fFtld)   # design residual tensile strengths [MPa]
print(frc.tensionConstLaw)    # piecewise eps-sigma tension law
```

The input/output schemas live in `pyfiberc.tools.models`; the material law tables
and code mappings live in `pyfiberc.materials`.

## Development

### Set up

```bash
git clone https://gitlab.com/luigi_paone/pyfrc.git
cd pyfrc
uv sync
```

`uv sync` creates `.venv/` from `uv.lock`, installs the package in editable mode,
and pulls in the `dev` dependency group.

### Project layout

```
src/pyfiberc/
├── materials.py            # LawCode, FiberConcrete material, ductility tables
├── solver.py               # FRCSolver: run(), buildReport()
├── solver_lib.py           # FRC_SLU_solver, FRC_SLE_solver, shear reduction
├── tools/models.py         # Pydantic models: FrcRecSectionInput/Output, FiberConcrete
└── templates/latex/        # LaTeX fragments for the FRC material report
tests/
├── input_benchmarks/       # JSON input examples (SLU and SLE)
├── test_materials.py
└── test_solver.py
```

### Tests and type checking

```bash
uv run pytest
uv run pytest --cov       # coverage (configured under [tool.coverage.run])
uv run mypy src/pyfiberc
```

### Releasing

1. Bump `version` in `pyproject.toml`.
2. `uv lock` to refresh the lockfile.
3. Add an entry to [`CHANGELOG.md`](CHANGELOG.md).
4. Commit (`chore: bump version to <version>`) and tag.

## Credits

pyfiberc stands on [**pycivil**](https://pypi.org/project/pycivil/), which supplies
the concrete section model, rebar disposers, loads and limit-state definitions, the
N‑M checking solvers for RC rectangular sections, the plotting helpers, and the
LaTeX report engine used for the PDF output. pyfiberc adds the FRC material laws
and the fibered ULS/SLE solvers on top of that foundation.

## Authors

- Marco Melcarne (SYSTRA)
- Luigi Luis Paone
- Claudia Orrico (SY
