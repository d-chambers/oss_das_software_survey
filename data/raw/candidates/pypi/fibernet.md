---
key: pypi/fibernet
source: pypi
name: fibernet
package: fibernet
description: A comprehensive fiber network generation, simulation, and ML toolkit for materials science
  research
registry_url: https://pypi.org/project/fibernet/
version: 4.1.7
last_release: '2026-07-23'
repository_url: https://github.com/GellmanSparrowS/fibernet
repository_declared_in_metadata: true
license_stated: MIT
author: FiberNet Contributors
probes:
- pypi:simple-index-sweep
probe_class: broad-acronym
found_by:
- search
first_seen: '2026-08-28'
---

<div align="center">

# 🧬 FiberNet v4

**Python Toolkit for Fiber Network Design, Simulation & Intelligent Optimization**

[![PyPI](https://img.shields.io/pypi/v/fibernet?logo=pypi&logoColor=white)](https://pypi.org/project/fibernet/)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![CI](https://github.com/GellmanSparrowS/fibernet/actions/workflows/ci.yml/badge.svg)](https://github.com/GellmanSparrowS/fibernet/actions)
[![Downloads](https://img.shields.io/pypi/dm/fibernet)](https://pypi.org/project/fibernet/)

[中文文档](README_CN.md) · [PyPI](https://pypi.org/project/fibernet/) · [Tutorial](#-tutorial) · [API Docs](#-api-reference)

*Developed by [ML-BioMat Lab](https://ml-biomat.com/) @ [BMG-FDU](https://github.com/BMG-FDU)*

</div>

---

## Overview

FiberNet is a research-grade Python toolkit for **computational design of fiber network metamaterials**. It provides a complete closed-loop workflow:

```
Generation → Simulation (Mass-Spring / FEM) → Feature Extraction → Machine Learning → Reinforcement Learning
```

| Feature | Description |
|---------|-------------|
| **26 Unit Types** | 12 2D + 14 3D: honeycomb, kagome, reentrant, octet, diamond\_3d, fcc, bcc, gyroid, TPMS… |
| **Parametric Control** | Internal point displacements for RL-ready continuous action spaces |
| **Dual Simulation** | Taichi mass-spring (GPU) + Beam Frame FEM (Euler–Bernoulli) |
| **94-Dim Features** | Structural + pore + contact feature extraction |
| **One-Line ML** | `predict_from_csv()` → train, evaluate, visualize, save |
| **One-Line RL** | `run_bayesian_optimization()` or CEM optimization |

---

## 🖼️ Showcase

<div align="center">
<img src="docs/images/01_2d_gallery.png" width="80%" alt="2D Structure Gallery" />
</div>

*12 2D unit types: square, triangle, hexagon, honeycomb, kagome, voronoi, chiral, reentrant, star, cross, diamond, missing\_rib.*

<div align="center">
<img src="docs/images/voronoi_1.5x_auto.png" width="80%" alt="Voronoi Stretch" />
</div>

*Voronoi structure under 1.5× uniaxial stretch (mass-spring model) — deformation and stress distribution.*

<div align="center">
<img src="docs/images/05_trajectory_dark.png" width="80%" alt="Deformation Trajectory" />
</div>

*8-frame deformation trajectory: honeycomb under stretch, colored by edge stretch ratio.*

<div align="center">
<img src="docs/images/fem_showcase_dark.png" width="80%" alt="FEM Deformation Showcase" />
</div>

*Beam Frame FEM analysis: uniaxial stretch (2×) and compression (0.5×) across multiple topologies and fiber radii. Bright color = high von Mises stress. Structures modeled as welded frames with radius-dependent bending stiffness.*

<div align="center">
<img src="docs/images/09_ml_analysis_dark.png" width="80%" alt="ML Analysis" />
</div>

*ML analysis: confusion matrix, ROC curves, and learning curves.*

<div align="center">
<img src="docs/images/11_rl_reward_dark.png" width="80%" alt="RL Reward" />
</div>

*CEM reinforcement learning: reward per episode and monotonically increasing best reward.*

---

## 🚀 Quick Start

### One-Line API

```python
import fibernet as fn

g = fn.pattern_2d(unit="honeycomb", box=(10, 10), grid=(4, 4))
fn.show(g)  # one-line visualization
```

```python
r = fn.simulate(g, mode="stretch", strain=1.5, backend="spring")
print(f"max_force={r.max_force:.0f} N, max_stretch={r.max_stretch:.3f}")
```

### FEM in 3 Lines

```python
from fibernet.ml import BeamFrameFEM

solver = BeamFrameFEM(E=1e9, nu=0.3)
g = fn.pattern_2d(unit="honeycomb", box=(10, 10), grid=(4, 4), radius=0.05)
result = solver.stretch_test(g, target_stretch=2.0)

print(f"Max stress: {result['sigma_total'].max()/1e6:.1f} MPa")
print(f"Max displacement: {result['max_displacement']:.4f} m")
```

### Complete Pipeline

```python
import fibernet as fn
import numpy as np

# 1. Parametric structure (20 displacement params for RL)
displacements = [(np.random.uniform(-0.3, 0.3), np.random.uniform(-0.3, 0.3))
                 for _ in range(20)]
g = fn.pattern_2d(unit="square", box=(10, 10), grid=(3, 3),
                  n_pts_per_side=5, point_displacements=displacements)

# 2a. Taichi mass-spring simulation
engine = fn.TaichiEngine()
r = engine.stretch_test(g, target_stretch=1.5, stiffness=1e5,
                        damping=0.3, num_steps=1000, save_interval=200)

# 2b. Or Beam Frame FEM (Euler-Bernoulli, welded joints)
from fibernet.ml import BeamFrameFEM
fem = BeamFrameFEM(E=1e9, nu=0.3)
fem_result = fem.stretch_test(g, target_stretch=1.5)
sim_r = fem.to_sim_result(fem_result, graph=g)

# 3. Visualization
fig = fn.render_trajectory(g, r.positions_trajectory, r.edge_stretches,
                           n_frames=6, title="Stretch Process")
fig.savefig("deformation.png", dpi=150)

# 4. Feature extraction (94-dim vector)
ext = fn.GraphFeatureExtractor()
features = ext.extract(g)

# 5. Node manipulation (for RL action space)
internal = g.get_internal_nodes()
g.displace_node(internal[0], [0.1, 0.2])
```

---

## 📦 Installation

```bash
pip install fibernet          # core
pip install fibernet[full]    # ML + RL + viz + simulation
pip install fibernet[ml]      # ML only
pip install fibernet[rl]      # RL only
```

| Optional Group | Packages |
|---------------|----------|
| `ml` | scikit-learn, pandas, tqdm |
| `rl` | gymnasium, scikit-optimize, stable-baselines3 |
| `accel` | taichi (GPU simulation) |
| `viz` | pyvista (3D visualization) |
| `full` | all of the above |

---

## 🔬 Beam Frame FEM

FiberNet v4.1 introduces a production-grade **Beam Frame Finite Element Method** solver based on Euler–Bernoulli beam theory, providing physically accurate mechanical analysis beyond the mass-spring model.

### Physics Model

Unlike mass-spring models where fiber diameter is cosmetic, the FEM solver treats the structure as a **welded frame** — joints are rigidly connected and fiber radius directly determines bending and
