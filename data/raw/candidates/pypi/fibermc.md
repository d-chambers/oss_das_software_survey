---
key: pypi/fibermc
source: pypi
name: fibermc
package: fibermc
description: A Jax-based differentiable Monte Carlo estimator with applications to differentiable simulation,
  computational geometry, and topology optimization.
registry_url: https://pypi.org/project/fibermc/
version: 0.0.4
last_release: '2024-12-10'
repository_url: https://github.com/PrincetonLIPS/fibers-standalone
repository_declared_in_metadata: true
license_stated: MIT
author: Nick Richardson <njkrichardson@princeton.edu>
probes:
- pypi:simple-index-sweep
probe_class: broad-acronym
found_by:
- search
first_seen: '2026-08-28'
---

# Fiber Monte Carlo 

Fiber Monte Carlo (FMC) is a differentiable variant of the [simple Monte Carlo](https://en.wikipedia.org/wiki/Monte_Carlo_method) estimator designed with 
low-dimensional geometric-oriented applications in mind. The methodological and theoretical aspects of FMC are outlined in the accompanying [paper](https://openreview.net/pdf?id=sP1tCl2QBk), but this Python package contains implementations of a variety of general-purpose estimators with FMC as the underlying method, as well as utilities specific applications like computational geometry, differentiable rendering and topology optimization.
