---
key: pypi/daspack-dev
source: pypi
name: daspack-dev
package: daspack-dev
description: 'DASPack: Controlled data compression for Distributed Acoustic Sensing'
registry_url: https://pypi.org/project/daspack-dev/
version: 0.0.1a0
last_release: '2025-08-09'
repository_url: https://github.com/asleix/daspack
repository_declared_in_metadata: true
license_stated: BSD-3-Clause
author: Aleix Segui
probes:
- pypi:simple-index-sweep
probe_class: domain-specific
found_by:
- search
first_seen: '2026-08-28'
---

<p align="center">
  <img src="docs/assets/logo.svg" alt="DASPack Logo" />
</p>

# DASPack: Controlled data compression for Distributed Acoustic Sensing

DASPack is a fast, open-source compressor for huge Distributed Acoustic Sensing (DAS) datasets.  
It supports **lossless** and **fixed-accuracy lossy** modes, letting you store data with an exact bound on reconstruction error.

The core is written in Rust for speed and safety, with a thin Python API for convenient integration into your workflows.

**DISCLAIMER:** We are testing the code, official release will be by mid-august.

---

## ✨ Highlights

- **Lossless or fixed-accuracy** — pick zero error or a max absolute error and get exactly what you asked for.
- **Multi-threaded** — control the number of threads per encode/decode call.
- **High throughput** — 800 MB/s+ on an 8-core laptop in typical workloads.
- **Self-describing streams** — all parameters (codec, quantizer, shape) are stored in the bitstream; no sidecars needed.
- **Pure Rust core** — no unsafe C buffers exposed to user code.
- **Python bindings** — direct `encode` / `decode` interface for NumPy arrays.

---

## 🚀 Quick start

### 1. Install (Python ≥ 3.9)

```bash
pip install daspack
# or, from source (Rust ≥ 1.74):
# maturin develop --release
```

### 2. Encode and store with h5py

You can store the compressed DASPack bitstream as raw bytes in HDF5:

```python
import numpy as np, h5py
from daspack import DASCoder, Quantizer

# Example: lossless compression with 4 threads
data = np.random.randint(-1000, 1000, size=(4096, 8192), dtype=np.int32)
coder = DASCoder(threads=4)

# Encode in Lossless mode
stream = coder.encode(
    data,
    Quantizer.Lossless(),
    blocksize=(1024, 1024),
    levels=0,
    order=0,
)

with h5py.File("example.h5", "w") as f:
    f.create_dataset("compressed", data=np.frombuffer(stream, dtype=np.uint8))
```

### 3. Read and decode

```python
import numpy as np, h5py
from daspack import DASCoder

coder = DASCoder(threads=4)

with h5py.File("example.h5") as f:
    raw = f["compressed"][:].tobytes()

# Decode: dtype is inferred from the stream
restored = coder.decode(raw)
```


### 4. Lossy example with fixed error bound

```python
import numpy as np
from daspack import DASCoder, Quantizer

# Generate some example data
data = np.random.uniform(-100, 100, size=(6, 8)).astype(np.float64)

coder = DASCoder(threads=2)

# Target: absolute error ≤ step/2
step = 0.5

# Encode with Uniform quantizer (lossy) and given step
stream = coder.encode(
    data,
    Quantizer.Uniform(step=step),
)

# Decode (dtype inferred from stream)
restored = coder.decode(stream)

# Verify bound
tol = step / 2 + 1e-12
max_err = np.max(np.abs(restored - data))
print(f"Max abs error: {max_err:.6f} (tolerance {tol})")
assert max_err <= tol

print("Original data:\n", data)
print("Restored data:\n", restored)
```

The expected output is
```
Max abs error: 0.250000 (tolerance 0.250000)
Original data:
 [[ ... ]]
Restored data:
 [[ ... ]]
```

---


## ⚙️ How it works

```
(float mode) Quantize → Wavelet (5/3) → 2-D LPC → Arithmetic coding
(int mode)   Identity  → Wavelet (5/3) → 2-D LPC → Arithmetic coding
```
The lossy path is bounded-error thanks to uniform quantization; the rest of the chain is perfectly reversible.

Read the paper (see citation below!) for more information 😄


---

## 📄 License

DASPack is released under the 3-Clause BSD License.

---

## 🤝 Contributing

Bug reports and pull requests are welcome.
If you plan a large change, please open an issue first so we can discuss the design.

---

## 📣 Citing

If you use DASPack in academic work, please cite:

> Seguí, A. *et al.* (2025). **DASPack: Controlled Data Compression for Distributed Acoustic Sensing**. *Geophysical Journal International*.\
> DOI: *pending*

Thanks for supporting open science!
