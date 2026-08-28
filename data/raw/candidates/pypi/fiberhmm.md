---
key: pypi/fiberhmm
source: pypi
name: fiberhmm
package: fiberhmm
description: Hidden Markov Model for calling chromatin footprints from fiber-seq and DAF-seq data
registry_url: https://pypi.org/project/fiberhmm/
version: 2.16.8
last_release: '2026-08-25'
repository_url: https://github.com/fiberseq/FiberHMM
repository_declared_in_metadata: true
license_stated: MIT
author: FiberHMM Authors
probes:
- pypi:simple-index-sweep
probe_class: broad-acronym
found_by:
- search
first_seen: '2026-08-28'
---

# FiberHMM

Hidden Markov Model toolkit for calling chromatin footprints from Fiber-seq,
DAF-seq, and other single-molecule footprinting data.

FiberHMM identifies protected regions (nucleosomes, TF/Pol II footprints) and
accessible regions (methylase-sensitive patches, MSPs) from single-molecule DNA
modification data — m6A methylation (fiber-seq) and deamination marks (DAF-seq).

> **Current release: v2.16.8.** File-based DddA/DddB calls now mark PCR
> duplicates automatically and nondestructively, screen adequately covered
> samples for recurrent C→T/G→A SNPs after duplicate marking, and run bounded
> assay-matched QC after footprint calling. `fiberhmm-qc` also accepts multiple
> BAMs for per-sample panels plus a combined comparison report. Use
> `--no-dedup`, `--no-daf-call-snps`, or `--no-qc` to disable an automatic
> stage; only `--dedup-collapse` removes duplicate reads.

- [Installation](#installation)
- [Quick start](#quick-start)
- [Choosing a command](#choosing-a-command)
- [Workflows](#workflows)
- [Command reference](#command-reference)
- [Output tags](#output-tags)
- [Pre-trained models](#pre-trained-models)
- [Performance tips](#performance-tips)
- [Deep reference](docs/reference.md) — MA/AQ schema, LLR scoring model, tag glossary

## Key features

- **`fiberhmm-call`** — recommended one-command pipeline: nucleosome/MSP HMM +
  nucleosome recall + TF recall fused in one process, with region-parallel
  scaling. Coordinate-sorted input → sorted + indexed output, no separate sort.
- **Nucleosome recaller (on by default)** — splits over-merged nucleosomes on
  accessible evidence, refines edges, runs an evidence-gated periodicity prior.
- **DAF duplicate marking + SNP masking** — file-based DddA/DddB calls
  automatically mark endpoint-concordant deamination-fingerprint duplicates,
  retain every read, then mask well-supported recurrent SNPs from HMM
  observations. The original sequence and `MD` tag are preserved.
- **Bounded QC** — assay-aware signal rate, nucleosome-scale periodicity,
  footprint sizes, example molecules, duplication, and SNP diagnostics with
  terminal PASS/WARN/FAIL scores and Illustrator-editable vector PDFs.
- **No genome context files** — hexamer context computed from read sequences.
- **Spec-compliant tags** — `ns`/`nl`/`as`/`al` legacy tags plus `MA`/`AQ`
  [Molecular-annotation spec](https://github.com/fiberseq/Molecular-annotation-spec)
  tags with `nuc.QQQ` / `tf.QQQ` scoring.
- **Validated workflows** — PacBio and Nanopore Hia5 fiber-seq, plus DAF-seq
  with DddB and DddA.
- **Native, fast** — no hmmlearn dependency; Numba JIT for ~10× speedup.

GpC/CpG methylase workflows (including M.CviPI/M.SssI-style data) are not yet
fully implemented or validated, and no bundled model is provided. The control
datasets we found were from much older Nanopore generations and were not
suitable for reliable current calibration, so these chemistries should
currently be treated as unsupported rather than assuming a Hia5 model will
transfer.

## Installation

```bash
pip install fiberhmm
```

From source:

```bash
git clone https://github.com/fiberseq/FiberHMM.git
cd FiberHMM && pip install -e .
```

Optional extras:

```bash
pip install numba        # ~10x faster HMM computation (recommended)
pip install matplotlib   # --stats visualization
pip install h5py         # HDF5 posteriors export
```

For bigBed output, install [UCSC tools](https://hgdownload.soe.ucsc.edu/admin/exe/)
(`bedToBigBed`, and `bigBedInfo`/`bigBedToBed` for `fiberhmm-utils fix-bigbed`).

## Quick start

`fiberhmm-call` is the entry point for almost everything. Pre-trained models are
bundled — `--enzyme` selects the chemistry and `--seq` selects the platform when
applicable; `-m` is only for custom models.

```bash
# Fiber-seq (Hia5), sorted+indexed BAM — region-parallel is fastest
fiberhmm-call -i sorted.bam -o calls.bam --enzyme hia5 --seq pacbio \
              -c 8 --region-parallel --skip-scaffolds

# DAF-seq (DddB), aligned BAM with MD tags; the enzyme selects DAF mode
fiberhmm-call -i aligned.bam -o calls.bam --enzyme dddb \
              -c 8 --region-parallel

# DAF-seq amplicons (DddA): duplicate marking, SNP screening, and QC are automatic
fiberhmm-call -i aligned.bam -o calls.bam --enzyme ddda \
              -c 8 --region-parallel

# Compare several completed datasets in one QC report
fiberhmm-qc -i embryo.bam spatial_1.bam spatial_2.bam -o qc_comparison/

# Unaligned / stdin → streaming mode, pipe straight into FIRE
fiberhmm-call -i unaligned.bam -o - --enzyme hia5 --seq pacbio -c 8 \
    | ft fire - final.bam

# Extract calls to BED12 / bigBed for browsing
fiberhmm-extract -i calls.bam --nucleosome --msp --tf
```

## Choosing a command

| Situation | Command |
|-----------|---------|
| **Full pipeline, sorted+indexed BAM** (default) | `fiberhmm-call --region-parallel` |
| Unaligned/unsorted BAM, or reading from stdin | `fiberhmm-call` (streaming, no `--region-parallel`) |
| File-based DddA/DddB call | `fiberhmm-call` (automatic nondestructive dedup → SNP mask → footprint call → QC) |
| Compare one or more completed BAMs | `fiberhmm-qc -i sample1.bam [sample2.bam …]` |
| Only nucleosome/MSP calls, no TF recall | `fiberhmm-apply` |
| Already have an apply-tagged BAM, add TF calls | `fiberhmm-recall-tfs` |
| Apply-tagged BAM, full recall without re-running the HMM | `fiberhmm-recall-nucs` |
| Calls → BED12 / bigBed | `fiberhmm-extract` |

`fiberhmm-call` has two execution strategies: **region-parallel**
(`--region-parallel`, requires a coordinate-sorted + indexed BAM; near-linear
scaling up to chromosome count, writes sorted+indexed output) and **streaming**
(default; accepts unaligned/unsorted BAM or stdin `-i -`, and pipes to stdout
`-o -` for `ft fire`). The observation mode is selected automatically from
`--enzyme` and, for Hia5, `--seq`.

> `fiberhmm-run` was removed in 2.8.0 — it chained apply + recall + fire as
> separate piped subprocesses. `fiberhmm-call` fuses those stages i
