---
key: pypi/ndx-fiber-photometry
source: pypi
name: ndx-fiber-photometry
package: ndx-fiber-photometry
description: This is an NWB extension for storing fiber photometry recordings and associated metadata.
registry_url: https://pypi.org/project/ndx-fiber-photometry/
version: 0.2.3
last_release: '2026-01-23'
repository_url: https://github.com/organization/ndx-fiber-photometry
repository_declared_in_metadata: true
license_stated: BSD-3
author: Alessandra Trapani <alessandra.trapani@catalystneuro.com>, Luiz Tauffer <luiz.tauffer@catalystneuro.com>,
  Paul Adkisson <paul.adkisson@catalystneuro.com>, Szonja Weigl <szonja.weigl@catalystneuro.com>
probes:
- pypi:simple-index-sweep
probe_class: domain-specific
found_by:
- search
first_seen: '2026-08-28'
---

# ndx-fiber-photometry Extension for NWB

This is an NWB extension for storing fiber photometry recordings and associated metadata.
It replaces the deprecated [ndx-photometry](https://github.com/catalystneuro/ndx-photometry) extension.

## Neurodata Types

This extension provides neurodata types for documenting fiber photometry experiments, including excitation sources,
photodetectors, optical indicators, and fiber optics, as well as the fiber photometry response series.

### Device Specification Types (ndx-ophys-devices)

This extension depends on `ndx-ophys-devices`, which provides the foundational device types for specifying the physical hardware and biological components used in optical physiology experiments, which include but are not limited to fiber photometry.
These types follow a model-instance pattern where device models define specifications and device instances represent actual hardware with specific configurations.

#### ExcitationSource & ExcitationSourceModel
**ExcitationSourceModel**: Template specifications for light sources
- `source_type`: Type of light source (e.g., "laser", "LED")
- `excitation_mode`: Mode of excitation (e.g., "one-photon")
- `wavelength_range_in_nm`: Supported wavelength range [min, max]

**ExcitationSource**: Specific light source instance
- `power_in_W`: Maximum power output
- `intensity_in_W_per_m2`: Light intensity at the fiber tip
- `exposure_time_in_s`: Typical exposure duration
- Links to its corresponding `ExcitationSourceModel`

#### OpticalFiber & OpticalFiberModel
**OpticalFiberModel**: Template specifications for optical fibers
- `numerical_aperture`: Numerical aperture value
- `core_diameter_in_um`: Core diameter in micrometers
- `active_length_in_mm`: Active length for tapered fibers
- Ferrule specifications (name, model, diameter)

**OpticalFiber**: Specific fiber instance with implantation details
- `serial_number`: Unique identifier for this fiber
- `fiber_insertion`: Container with stereotactic coordinates and angles
- Links to its corresponding `OpticalFiberModel`

#### FiberInsertion
Detailed implantation information for optical fibers:
- Stereotactic coordinates (`insertion_position_ap_in_mm`, `insertion_position_ml_in_mm`, `insertion_position_dv_in_mm`)
- `depth_in_mm`: Insertion depth
- `position_reference`: Reference point for coordinates (e.g., "Bregma")
- `hemisphere`: Target hemisphere
- Insertion angles (`insertion_angle_pitch_in_deg`, `insertion_angle_yaw_in_deg`, `insertion_angle_roll_in_deg`)

#### ViralVector & ViralVectorInjection
**ViralVector**: Viral construct specifications
- `construct_name`: Name of the viral construct/vector
- `description`: Detailed description of the construct
- `manufacturer`: Source of the viral vector
- `titer_in_vg_per_ml`: Viral titer in genomes per mL

**ViralVectorInjection**: Injection procedure details
- Stereotactic coordinates and angles
- `volume_in_uL`: Volume injected
- `injection_date`: Date of injection procedure
- `location`: Target brain region
- `hemisphere`: Target hemisphere
- Links to the corresponding `ViralVector`

#### Indicator
Fluorescent indicator/reporter specifications:
- `label`: Name of the fluorescent indicator (e.g., "GCaMP6f", "Tdtomato")
- `description`: Detailed description of the indicator
- `viral_vector_injection`: Links to the `ViralVectorInjection` used to deliver this indicator
- Used to specify calcium indicators, voltage indicators, or other fluorescent reporters

#### Photodetector & PhotodetectorModel
**PhotodetectorModel**: Template specifications for photodetectors
- `detector_type`: Type of detector (e.g., "PMT", "photodiode", "CMOS")
- `wavelength_range_in_nm`: Detection wavelength range [min, max]
- `gain`: Base gain value for the detector
- `gain_unit`: Units for the gain measurement (e.g., "A/W")

**Photodetector**: Specific photodetector instance
- `serial_number`: Unique identifier for this detector
- `description`: Detailed description of the detector's role
- Links to its corresponding `PhotodetectorModel`

#### DichroicMirror & DichroicMirrorModel
**DichroicMirrorModel**: Template specifications for dichroic mirrors
- `cut_on_wavelength_in_nm`: Wavelength where transmission begins to increase
- `cut_off_wavelength_in_nm`: Wavelength where transmission begins to decrease
- `reflection_band_in_nm`: Wavelength range that is primarily reflected [min, max]
- `transmission_band_in_nm`: Wavelength range that is primarily transmitted [min, max]
- `angle_of_incidence_in_degrees`: Designed angle of incidence for the mirror

**DichroicMirror**: Specific dichroic mirror instance
- `serial_number`: Unique identifier for this mirror
- `description`: Detailed description of the mirror's role in the optical path
- Links to its corresponding `DichroicMirrorModel`

#### BandOpticalFilter & BandOpticalFilterModel
**BandOpticalFilterModel**: Template specifications for bandpass/bandstop filters
- `filter_type`: Type of filter (e.g., "Bandpass", "Bandstop")
- `center_wavelength_in_nm`: Center wavelength of the filter
- `bandwidth_in_nm`: Full width at half maximum (FWHM) bandwidth
- Typically used for emission or excitation filtering

**BandOpticalFilter**: Specific band filter instance
- `serial_number`: Unique identifier for this filter
- `description`: Detailed description of the filter's role
- Links to its corresponding `BandOpticalFilterModel`

#### EdgeOpticalFilter & EdgeOpticalFilterModel
**EdgeOpticalFilterModel**: Template specifications for edge filters
- `filter_type`: Type of edge filter (e.g., "Longpass", "Shortpass")
- `cut_wavelength_in_nm`: Wavelength at which the filter transitions
- `slope_in_percent_cut_wavelength`: Steepness of the transition as percentage of cut wavelength
- `slope_starting_transmission_in_percent`: Transmission percentage at start of transition
- `slope_ending_transmission_in_percent`: Transmission percentage at end of transition

**EdgeOpticalFilter**: Specific edge filter instance
- `serial_number`: Unique ident
