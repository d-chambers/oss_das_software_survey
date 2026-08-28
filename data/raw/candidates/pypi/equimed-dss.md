---
key: pypi/equimed-dss
source: pypi
name: equimed-dss
package: equimed-dss
description: A comprehensive Python library for clinical AI fairness assessment with 37 metrics across
  five domains
registry_url: https://pypi.org/project/equimed-dss/
version: 1.9.5
last_release: '2026-06-20'
repository_url: https://github.com/johnmuteba/EquiMed_DSS
repository_declared_in_metadata: true
license_stated: MIT
author: John Muteba <2moi175@gmail.com>
probes:
- pypi:simple-index-sweep
probe_class: broad-acronym
found_by:
- search
first_seen: '2026-08-28'
---

# EquiMed_DSS

<div align="center">

<h3>A Comprehensive Python Library for Clinical AI Fairness Assessment</h3>

<p>Evaluate reliability, equity, governance, and intersectionality in clinical AI systems using <strong>37 metrics across five domains</strong></p>

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/johnmuteba/EquiMed_DSS/blob/master/LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

</div>

---

## Overview

**EquiMed_DSS** (Equitable Medical Decision Support System) provides a systematic framework for evaluating clinical AI systems across multiple dimensions of fairness, reliability, and governance. The library implements **37 metrics across five domains** specifically designed for healthcare applications where equity and safety are paramount.

### Key Features

| Feature | Description |
|---------|-------------|
| **37 Metrics** | Five domains (reliability, equity, governance, representation/robustness, technical-supplement fairness) plus geographic and advanced-appendix metrics |
| **Clinical AI Focus** | Designed specifically for healthcare applications |
| **Statistical Analyses** | HLM, Mediation Analysis, Network Statistics |
| **Publication-Ready Visualizations** | 6 manuscript-quality figure generators |
| **Multi-Format Data Support** | MySQL, CSV, TSV, JSON with automatic standardization |
| **Intersectional Analysis** | Detect bias across demographic combinations |
| **Geographic Equity** | BEMI and GCC measure evidence-burden mismatch and regional concentration |
| **Tidy Reporting Tables** | `export_table` renders metric results as markdown, LaTeX, or HTML |

---

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Data Format](#data-format)
- [Metrics Overview](#metrics-overview)
  - [Domain 1: Reliability & Calibration](#domain-1-reliability--calibration)
  - [Domain 2: Fairness, Equity & Ethics](#domain-2-fairness-equity--ethics)
  - [Domain 3: Governance & Transparency](#domain-3-governance--transparency)
  - [Domain 4: Representation & Robustness](#domain-4-representation--robustness)
  - [Domain 5: Technical-supplement Fairness](#domain-5-technical-supplement-fairness)
  - [Appendix: Advanced Metrics](#appendix-advanced-metrics)
  - Full formulas, clinical meaning, and runnable examples: see [docs/VIGNETTE.md](https://github.com/johnmuteba/EquiMed_DSS/blob/master/docs/VIGNETTE.md)
- [Statistical Analyses](#statistical-analyses)
- [Visualizations](#visualizations)
- [Examples](#examples)
- [Vignette](https://github.com/johnmuteba/EquiMed_DSS/blob/master/docs/VIGNETTE.md)
- [API Reference](#api-reference)
- [Contributing](#contributing)
- [Citation](#citation)
- [License](#license)

---

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Install from Source

```bash
# Clone the repository
git clone https://github.com/johnmuteba/EquiMed_DSS.git
cd EquiMed_DSS

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package with dependencies
pip install -e .
```

### Install via pip

```bash
pip install equimed_dss
```

### Installing inside Jupyter or conda (read this if you hit ModuleNotFoundError)

The most common installation problem is installing into a *different* Python
than the one your notebook or environment actually runs. You see
`Successfully installed equimed_dss` in a terminal, then
`ModuleNotFoundError: No module named 'equimed_dss'` in Jupyter. This is an
environment mismatch, not a package problem. Install into the **running**
interpreter:

In a Jupyter notebook cell (installs into the active kernel, then restart the kernel):

```python
%pip install equimed_dss
```

From a terminal, target a specific interpreter explicitly:

```bash
python -m pip install equimed_dss          # uses THIS python
# conda example:
conda activate myenv && python -m pip install equimed_dss
```

Confirm the install is visible to your interpreter:

```python
import sys; print(sys.executable)          # which python is running
import equimed_dss; print(equimed_dss.__version__)
```

### Dependencies

```
numpy>=1.20.0
pandas>=1.3.0
scipy>=1.7.0
scikit-learn>=1.0.0
matplotlib>=3.5.0
seaborn>=0.11.0
networkx>=2.6.0
statsmodels>=0.13.0
```

---

## Quick Start

### Generate Sample Data

```python
from equimed_dss.utils import SampleDataGenerator

# Generate synthetic clinical AI evaluation data
generator = SampleDataGenerator(random_state=42)
data = generator.generate_fairness_data(n_samples=1000)

print(f"Generated {len(data)} samples with columns: {list(data.columns)}")
# Output: Generated 1000 samples with columns: ['id', 'race', 'gender', 'age_group', 'prediction', 'actual', 'confidence']
```

### Calculate Fairness Metrics

```python
import numpy as np
from equimed_dss.domain2 import HierarchicalEquityRatio, HarmAdjustedFairnessGap

# Example: Calculate Hierarchical Equity Ratio across racial groups
her_metric = HierarchicalEquityRatio()
group_performance = {
    'White': 0.85,
    'Black': 0.78,
    'Hispanic': 0.80,
    'Asian': 0.87
}

her_scores = her_metric.calculate_her(group_performance)
gini = her_metric.calculate_bias_gini(list(group_performance.values()))

print(f"Equity Ratios: {her_scores}")
print(f"Bias-Gini Index: {gini:.4f}")
# Interpretation: Gini < 0.2 indicates low dispersion (good)
```

### Analyze Distributional Fairness

```python
from equimed_dss.appendix import JensenShannonDivergence, WassersteinDistance

# Compare prediction distributions between groups
group_a_predictions = np.array([0.9, 0.85, 0.78, 0.92, 0.88])
group_b_predictions = np.array([0.75, 0.7
