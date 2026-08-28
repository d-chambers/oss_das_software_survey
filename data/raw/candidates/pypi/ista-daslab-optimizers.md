---
key: pypi/ista-daslab-optimizers
source: pypi
name: ista-daslab-optimizers
package: ista-daslab-optimizers
description: Deep Learning optimizers developed in the Distributed Algorithms and Systems group (DASLab)
  @ Institute of Science and Technology Austria (ISTA)
registry_url: https://pypi.org/project/ista-daslab-optimizers/
version: 1.1.15
last_release: '2026-06-16'
repository_url: https://github.com/IST-DASLab/ISTA-DASLab-Optimizers
repository_declared_in_metadata: true
license_stated: "MIT License\n        \n        Copyright (c) 2026 IST Austria Distributed Algorithms\
  \ and Systems Lab\n        \n        Permission is hereby granted, free of charge, to any person obtaining\
  \ a copy\n        of this software and associated documentation files (the \"Software\"), to deal\n\
  \        in the Software without restriction, including without limitation the rights\n        to use,\
  \ copy, modify, merge, publish, distribute, sublicense, and/or sell\n        copies of the Software,\
  \ and to permit persons to whom the Software is\n        furnished to do so, subject to the following\
  \ conditions:\n        \n        The above copyright notice and this permission notice shall be included\
  \ in all\n        copies or substantial portions of the Software.\n        \n        THE SOFTWARE IS\
  \ PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\n        IMPLIED, INCLUDING BUT NOT LIMITED\
  \ TO THE WARRANTIES OF MERCHANTABILITY,\n        FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.\
  \ IN NO EVENT SHALL THE\n        AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\n\
  \        LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\n        OUT\
  \ OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE\n        SOFTWARE."
author: Ionut-Vlad Modoranu <ionut-vlad.modoranu@ist.ac.at>
probes:
- pypi:simple-index-sweep
probe_class: broad-acronym
found_by:
- search
first_seen: '2026-08-28'
---

# ISTA DAS Lab Optimization Algorithms Package
This repository contains optimization algorithms for Deep Learning developed by 
the Distributed Algorithms and Systems lab at Institute of Science and Technology Austria.

The repository contains code for the following optimizers published by DASLab @ ISTA:
- **AC/DC**:
  - paper: [AC/DC: Alternating Compressed/DeCompressed Training of Deep Neural Networks](https://arxiv.org/abs/2106.12379)
  - official repository: [GitHub](https://github.com/IST-DASLab/ACDC)
- **M-FAC**:
  - paper: [M-FAC: Efficient Matrix-Free Approximations of Second-Order Information](https://arxiv.org/abs/2107.03356)
  - official repository: [GitHub](https://github.com/IST-DASLab/M-FAC)
- **Sparse M-FAC with Error Feedback**:
  - paper: [Error Feedback Can Accurately Compress Preconditioners](https://arxiv.org/abs/2306.06098)
  - official repository: [GitHub](https://github.com/IST-DASLab/EFCP/)
- **MicroAdam**:
  - paper: [MicroAdam: Accurate Adaptive Optimization with Low Space Overhead and Provable Convergence](https://arxiv.org/abs/2405.15593)
  - official repository: [GitHub](https://github.com/IST-DASLab/MicroAdam)
- **Trion / DCT-AdamW**:
  - paper: [FFT-based Dynamic Subspace Selection for Low-Rank Adaptive Optimization of Large Language Models](https://arxiv.org/abs/2505.17967v3)
  - code: [GitHub](https://github.com/IST-DASLab/ISTA-DASLab-Optimizers/tree/main/ista_daslab_optimizers/fft_low_rank)
- **DASH**:
  - paper: [DASH: Faster Shampoo via Batched Block Preconditioning and Efficient Inverse-Root Solvers](https://arxiv.org/pdf/2602.02016)
  - code: [GitHub](https://github.com/IST-DASLab/DASH)

## CUDA Kernels
Please visit the repository [ISTA-DASLab-Optimizers-CUDA](https://github.com/IST-DASLab/ISTA-DASLab-Optimizers-CUDA) containing the CUDA 
support for **M-FAC**, **Sparse M-FAC** and **MicroAdam** optimizers.

### Installation
To use the latest stable version of this repository, you can install via pip:

```shell
pip3 install ista-daslab-optimizers
```

and you can also visit the [PyPi page](https://pypi.org/project/ista-daslab-optimizers/).

We also provide a script `install.sh` that creates a new environment, installs requirements
and then installs the project as a Python package following these steps:

```shell
git clone git@github.com:IST-DASLab/ISTA-DASLab-Optimizers.git
cd ISTA-DASLab-Optimizers
source install.sh
```

## How to use optimizers?

In this repository we provide a minimal working example for CIFAR-10 for optimizers `acdc`,
`dense_mfac`, `sparse_mfac` and `micro_adam`:
```shell
cd examples/cifar10
OPTIMIZER=micro_adam # or any other optimizer listed above
bash run_${OPTIMIZER}.sh
```

To integrate the optimizers into your own pipeline, you can use the following snippets:

### MicroAdam optimizer
```python
from ista_daslab_optimizers import MicroAdam

model = MyCustomModel()

optimizer = MicroAdam(
    model.parameters(), # or some custom parameter groups
    m=10, # sliding window size (number of gradients)
    lr=1e-5, # change accordingly
    quant_block_size=100_000, # 32 or 64 also works
    k_init=0.01, # float between 0 and 1 meaning percentage: 0.01 means 1%
    alpha=0, # 0 means sparse update and 0 < alpha < 1 means we integrate fraction alpha from EF to update and then delete it
)

# from now on, you can use the variable `optimizer` as any other PyTorch optimizer
```

# Versions summary:

---
- **1.1.15** @ June 16th, 2026:
  - added constant `1e-16` to function `_compute_shampoo_direction` for numerical stability as in `DistributedShampoo`
  - this need appeared in the context of using `DASH` in the `modded-nanogpt` project, where the `proj` layers are initialized with 
    zeros, which causes some of the gradients at the first optimization step to be all zero. This makes Power-Iteration return NaNs and 
    Shampoo update be zero, causing `NaNs` because of `0/0` case
  - added a new config parameter called `eps_power_iter` to control the epsilon for Power-Iteration
- **1.1.14** @ March 25th, 2026:
  - added regularization for NewtonDB
- **1.1.13** @ March 3rd, 2026:
  - added support for any layer shape: squeeze parameters, then reshape 3D and 4D layers to 2D
- **1.1.12** @ February 15th, 2026:
  - refactory for DASH: separated entities to different files and implemented **DashGpu**, as well as
  a triton kernel to compute `L_t = beta * L_t-1 + (1-beta) * G @ G.T` and `R_t = beta * R_t-1 + (1-beta) * G.T @ G` in-place
  using the stacked blocks.
- **1.1.11** @ February 6th, 2026:
  - added `triton` as dependency
- **1.1.10** @ February 6th, 2026:
  - removed **fast-hadamard-transform** because 1) it is not used and 2) it raises compilation errors during `pip install`
- **1.1.9** @ February 6th, 2026:
  - added **DASH** optimizer
- **1.1.8** @ February 5th, 2026:
  - moved kernels to [ISTA-DASLab-Optimizers-CUDA](https://github.com/IST-DASLab/ISTA-DASLab-Optimizers-CUDA)
  - building building the package after adding a new optimizer that doesn't require CUDA support would require compiling 
  the kernels from scratch, which is time consuming and not needed
- **1.1.7** @ October 8th, 2025:
  - added code for `Trion & DCT-AdamW`
- **1.1.6** @ February 19th, 2025:
  - do not update the parameters that have `None` gradient in method `update_model` from `tools.py`.
  This is useful when using M-FAC for models with more than one classification head in the Continual Learning framework.
- **1.1.5** @ February 19th, 2025:
  - adapted `DenseMFAC` for a model with multiple classification heads for Continual Learning where 
  we have one feature extractor block and a list of classification heads. The issue was related to
  the model size, which included the feature extractor backbone and all classification heads, but
  in practice only one classification head will be used for training and inference. This caused some
  size mismatch errors at runtime in the `DenseCoreMFAC` module because the gradient at runtime had
  fewer entries than t
