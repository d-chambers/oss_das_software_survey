---
key: pypi/grundig-dss
source: pypi
name: grundig-dss
package: grundig-dss
description: Bit-exact native decoder for Grundig DSS-SP (PH9607) dictation audio — .dss to 16 kHz WAV,
  no Windows and no vendor software.
registry_url: https://pypi.org/project/grundig-dss/
version: 1.0.0
last_release: '2026-06-10'
repository_url: https://github.com/Guillain-RDCDE/DS2-Anywhere
repository_declared_in_metadata: true
license_stated: MIT
author: Guillain-RDCDE
probes:
- pypi:simple-index-sweep
probe_class: broad-acronym
found_by:
- search
first_seen: '2026-08-28'
---

# Grundig DSS-SP native decoder

Pure-Python, bit-exact decoder for **Grundig** `.dss` files (magic `\x06dss`, e.g.
the Digta 415) — the Grundig SP CELP variant that neither FFmpeg's `dss_sp`, the
Olympus-derived open codecs, nor NCH Switch decode correctly.

Reverse-engineered from Grundig's `dss2wav.dll`; output is **byte-for-byte
identical** to the reference on every test sample. The full story and the
recovered bitstream + synthesis spec are in
[`../docs/12-cracking-the-grundig-sp-codec.md`](../docs/12-cracking-the-grundig-sp-codec.md).

## Install

```bash
pip install grundig-dss        # from PyPI (pure-Python, zero dependencies)
```

## Usage

```bash
grundig-dss input.dss [output.wav]    # console command (out defaults to the input stem)
# or, without installing:
python3 -m grundig input.dss output.wav
./decode.sh input.dss output.wav
```

```python
from grundig import decode_dss, write_wav
pcm = decode_dss("recording.dss")     # list[int], 16 kHz mono 16-bit
write_wav("recording.wav", pcm)
```

## Files

| File | What |
|---|---|
| `grundig_dss.py` | the decoder (no Wine, no DLL, stdlib only) |
| `gtables.json` | quantization tables (reflection codebooks, gains, pulse/binomial tables, resample FIR) extracted from `dss2wav.dll`'s `.data` |
| `decode.sh` | thin CLI wrapper |

Olympus DSS/DS2 files (`\x02dss`/`\x03dss`/`\x03ds2`) are handled by the main
chain, not this module.
