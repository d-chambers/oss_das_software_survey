---
key: pypi/dss-projectfutura
source: pypi
name: dss-projectfutura
package: dss-projectfutura
description: Content Generation based on Caches
registry_url: https://pypi.org/project/dss-projectfutura/
version: 0.2.4
last_release: '2023-03-24'
repository_url: https://gitlab.com/project-futura/dss
repository_declared_in_metadata: true
license_stated: null
author: Jan Garcia <jancraft888@jdevstudios.es>, Saula Sanz <sourcepaint@jdevstudios.es>
probes:
- pypi:simple-index-sweep
probe_class: broad-acronym
found_by:
- search
first_seen: '2026-08-28'
---

# DSSv3g
This is the third version of the DSS text generator, but built in a more generic way to allow for any kind of dataset.
Lots of new features have been implemented, helping DSS*v3g* become actually useful.


DSS*v3g* is still built using the caches architecture, but additionally includes a tokenization step that allows any kind of data to be learnt.

## Variants
DSS has had a progression in versions and capability. Here you can explore their branches.
DSS is an architecture for building content generation ML models using caches.

### DSSv1
> Character-by-character text generation using caches. 4 char keys, 1 char values. JSON-encoded.

### DSSv2
> Word-by-word text generation using caches. 1 word keys, 1 word values. JSON-encoded.

### DSSv3
> Word-by word text generation using caches. Variable word keys, 1 word values. JSON-encoded with brotli compression.

#### DSSv3g
The most capable DSS variant to date, capable of text generation, music generation, code completion and (limited) chatting.
> General (integer tokens) version of DSS content generation using caches. Variable token keys, 1 token values. Binary encoded with brotli compression.

#### DSSv3i
Currently highly experimental and only implemented in JavaScript for easy graphics debugging.
> Image generation using the DSS caches architecture. Variable-*k* scalar keys, pixel scalar values. Binary encoded with brotli compression.

## Klarmuz
DSS*v3g* powers Klarmuz, the open platform for AI content generation. This project is possible thanks to jDev Studios and their fantastic Klarmuz compute units.
For examples on running DSS*v3g* models, please check out the [Klarmuz Platform](https://jdevstudios.es/klarmuz).
