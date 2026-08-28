---
key: pypi/dascorepy
source: pypi
name: dascorepy
package: dascorepy
description: A DASCore patch bridge to DASPy.
registry_url: https://pypi.org/project/dascorepy/
version: 0.1.0
last_release: '2026-05-08'
repository_url: null
repository_declared_in_metadata: false
license_stated: "MIT License\n        \n        Copyright (c) 2026 DASDAE\n        \n        Permission\
  \ is hereby granted, free of charge, to any person obtaining a copy\n        of this software and associated\
  \ documentation files (the \"Software\"), to deal\n        in the Software without restriction, including\
  \ without limitation the rights\n        to use, copy, modify, merge, publish, distribute, sublicense,\
  \ and/or sell\n        copies of the Software, and to permit persons to whom the Software is\n     \
  \   furnished to do so, subject to the following conditions:\n        \n        The above copyright\
  \ notice and this permission notice shall be included in all\n        copies or substantial portions\
  \ of the Software.\n        \n        THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND,\
  \ EXPRESS OR\n        IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\n   \
  \     FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\n        AUTHORS OR\
  \ COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\n        LIABILITY, WHETHER IN AN ACTION\
  \ OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\n        OUT OF OR IN CONNECTION WITH THE SOFTWARE OR\
  \ THE USE OR OTHER DEALINGS IN THE\n        SOFTWARE.\n        "
author: null
probes:
- pypi:simple-index-sweep
probe_class: broad-acronym
found_by:
- search
first_seen: '2026-08-28'
---

# dascorepy

A DASCore bridge to DASPy.

`dascorepy` exposes selected DASPy functionality on DASCore patches through the `patch.daspy` namespace. It focuses on DASPy operations that DASCore does not already provide, while preserving DASCore semantics.

## Installation

```bash
uv pip install dascorepy
```

## Usage

```python
import dascore as dc

patch = dc.get_example_patch("example_event_1")

denoised = patch.daspy.common_mode_noise_removal()
velocity = patch.daspy.fk_rescaling()
```

## Namespace Methods

| Method | What it adds |
| --- | --- |
| [`to_section`](`~DaspyPatchNamespace.to_section`) | Convert a DASCore patch to a DASPy `Section`. |
| [`common_mode_noise_removal`](`~DaspyPatchNamespace.common_mode_noise_removal`) | Remove common-mode noise with DASPy. |
| [`curvelet_denoising`](`~DaspyPatchNamespace.curvelet_denoising`) | Reduce stochastic noise with curvelet denoising. |
| [`channel_checking`](`~DaspyPatchNamespace.channel_checking`) | Detect bad channels from per-channel energy, or keep only good channels. |
| [`turning_points`](`~DaspyPatchNamespace.turning_points`) | Add a boolean `turning_point` coordinate along distance. |
| [`curvelet_windowing`](`~DaspyPatchNamespace.curvelet_windowing`) | Retain, remove, or decompose energy by apparent velocity. |
| [`fk_rescaling`](`~DaspyPatchNamespace.fk_rescaling`) | Convert strain or strain rate with FK-domain rescaling. |
| [`curvelet_conversion`](`~DaspyPatchNamespace.curvelet_conversion`) | Convert strain or strain rate with DASPy curvelets. |
| [`slant_stacking`](`~DaspyPatchNamespace.slant_stacking`) | Convert strain or strain rate with local slant stacking. |

## DASPy Reference

This package wraps algorithms from DASPy. If you use this package in research, please cite DASPy:

```
Hu, M., & Li, Z. (2024). DASPy: A Python toolbox for DAS seismology. Seismological Research Letters, 95(5), 3055-3066.
doi: 10.1785/0220240124
```

See also the DASPy [Publication page](https://hmz-03.github.io/publications/2024-07-26-DASPy) and [DASPy tutorial](https://daspy-tutorial.readthedocs.io/en/latest/).
