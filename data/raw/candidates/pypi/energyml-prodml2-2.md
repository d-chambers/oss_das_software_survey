---
key: pypi/energyml-prodml2-2
source: pypi
name: energyml PRODML 2.x
package: energyml-prodml2-2
registry_url: https://pypi.org/project/energyml-prodml2-2/
version: 1.12.0
last_release: '2024-03-18'
repository_url: https://github.com/geosiris-technologies/energyml-python-generator
repository_declared_in_metadata: true
license_stated: Apache-2.0
author: Valentin Gauthier (Geosiris)
probes:
- pypi:simple-index-sweep
probe_class: domain-specific
found_by:
- search
first_seen: '2026-08-28'
---

## Evidence

class DasAcquisition docstring: "Contains metadata about the DAS acquisition common to the various types of data acquired during the acquisition, which includes DAS measurement instrument data, fiber optical path, time zone, and core acquisition settings like pulse rate and gauge length, measurement start time and whether or not this was a triggered measurement."

## Verified by

wheel contains 18 Das* classes: DasAcquisition, DasRaw, DasRawData, DasFbe, DasFbeData, DasSpectra, DasSpectraData, DasProcessed, DasInstrumentBox, DasTimeArray, DasDimensions, DasCustom, DasExternalDatasetPart, DasCalibrationColumn, DasCalibrationInputPoint, DasCalibrationInputPointKind(+Ext), DasCalibrationTypeExt.
