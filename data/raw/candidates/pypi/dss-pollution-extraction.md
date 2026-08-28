---
key: pypi/dss-pollution-extraction
source: pypi
name: dss-pollution-extraction
package: dss-pollution-extraction
description: A package for analyzing pollution data from NetCDF files
registry_url: https://pypi.org/project/dss-pollution-extraction/
version: 1.0.3
last_release: '2025-06-04'
repository_url: https://github.com/MuhammadShafeeque/dss-pollution-extraction
repository_declared_in_metadata: true
license_stated: "MIT License\n        \n        Copyright (c) 2025 DSS Pollution Extraction Contributors\n\
  \        \n        Permission is hereby granted, free of charge, to any person obtaining a copy\n  \
  \      of this software and associated documentation files (the \"Software\"), to deal\n        in the\
  \ Software without restriction, including without limitation the rights\n        to use, copy, modify,\
  \ merge, publish, distribute, sublicense, and/or sell\n        copies of the Software, and to permit\
  \ persons to whom the Software is\n        furnished to do so, subject to the following conditions:\n\
  \        \n        The above copyright notice and this permission notice shall be included in all\n\
  \        copies or substantial portions of the Software.\n        \n        THE SOFTWARE IS PROVIDED\
  \ \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\n        IMPLIED, INCLUDING BUT NOT LIMITED TO\
  \ THE WARRANTIES OF MERCHANTABILITY,\n        FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.\
  \ IN NO EVENT SHALL THE\n        AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\n\
  \        LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\n        OUT\
  \ OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE\n        SOFTWARE."
author: Muhammad Shafeeque <muhammad.shafeeque@awi.de>
probes:
- pypi:simple-index-sweep
probe_class: broad-acronym
found_by:
- search
first_seen: '2026-08-28'
---

# DSS Pollution Extraction

<p align="center">
  <img src="docs/logo.png" alt="DSS Pollution Extraction Logo" width="300">
</p>

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Development Status](https://img.shields.io/badge/Development%20Status-Beta-orange.svg)](https://pypi.org/project/dss-pollution-extraction/)

A comprehensive Python package for analyzing pollution data from NetCDF files, developed at the Data Science Support (DSS), Alfred Wegener Institute (AWI). This package provides tools for temporal aggregations, spatial extractions, visualizations, and health threshold analysis of atmospheric pollution data.

## Features

### Data Analysis
- **Multi-pollutant support**: Black Carbon (BC), NO₂, PM₂.₅, PM₁₀
- **Temporal aggregations**: Monthly, seasonal, annual, and custom period averages
- **Spatial extractions**: Point-based, polygon-based, and NUTS3 region analysis
- **Statistical analysis**: Comprehensive data statistics and quality control

### Visualization
- **Spatial maps**: Interactive and publication-ready maps with Cartopy support
- **Time series plots**: Domain averages and location-specific trends
- **Seasonal cycles**: Annual pattern analysis and visualization
- **Distribution analysis**: Histograms and box plots for data exploration
- **Spatial statistics**: Mean, maximum, minimum, and standard deviation maps

### Data Export
- **Multiple formats**: NetCDF, GeoTIFF, CSV, GeoJSON, Shapefile
- **Flexible subsetting**: Temporal and spatial data subsetting
- **Batch processing**: Multi-file analysis workflows
- **Compression support**: Optimized file sizes for large datasets

### Health Analysis
- **WHO guidelines**: Air quality threshold analysis
- **EU standards**: Compliance checking with European regulations
- **Exceedance mapping**: Spatial distribution of threshold violations
- **Health impact assessment**: Tools for public health research

## Quick Start

### Installation

```bash
# Install from PyPI (when available)
pip install dss-pollution-extraction

# Or install from source
git clone https://github.com/MuhammadShafeeque/dss-pollution-extraction.git
cd dss-pollution-extraction
pip install -e .
```

### Basic Usage

```python
from pollution_extraction import PollutionAnalyzer

# Initialize analyzer
analyzer = PollutionAnalyzer("your_pollution_data.nc", pollution_type="pm25")

# Print dataset summary
analyzer.print_summary()

# Create visualizations
analyzer.plot_map(time_index=0, save_path="spatial_map.png")
analyzer.plot_time_series(save_path="time_series.png")
analyzer.plot_seasonal_cycle(save_path="seasonal_cycle.png")

# Temporal analysis
monthly_avg = analyzer.get_monthly_averages()
annual_avg = analyzer.get_annual_averages()

# Spatial extraction
point_locations = [(4321000, 3210000), (4500000, 3400000)]
point_data = analyzer.extract_at_points(point_locations)

# Export data
analyzer.export_to_geotiff("pm25_annual.tif", aggregation_method="mean")
analyzer.export_to_csv("pm25_data.csv")
```

## Project Structure

```
dss-pollution-extraction/
├── pollution_extraction/                  # Main package
│   ├── __init__.py                       # Package initialization
│   ├── analyzer.py                       # Main analysis interface
│   ├── cli.py                           # Command-line interface
│   ├── config.py                        # Configuration management
│   ├── utils.py                         # Utility functions
│   ├── examples.py                      # Usage examples
│   └── core/                            # Core functionality modules
│       ├── __init__.py                  # Core package initialization
│       ├── data_reader.py               # NetCDF data reading
│       ├── temporal_aggregator.py       # Time-based analysis
│       ├── spatial_extractor.py         # Spatial data extraction
│       ├── data_visualizer.py           # Plotting and visualization
│       ├── data_exporter.py             # Multi-format data export
│       ├── logging_utils.py             # Logging configuration
│       └── exporters/                   # Export format handlers
│           ├── __init__.py              # Exporters package init
│           ├── _base.py                 # Base exporter (private)
│           ├── _main.py                 # Main export coordinator (private)
│           ├── _raster.py               # Raster format exports (private)
│           ├── _spatial.py              # Vector format exports (private)
│           ├── _tabular.py              # Tabular format exports (private)
│           ├── base.py                  # Base exporter class (public)
│           ├── main.py                  # Main export coordinator (public)
│           ├── raster.py                # Raster format exports (public)
│           ├── spatial.py               # Vector format exports (public)
│           ├── tabular.py               # Tabular format exports (public)
│           └── types.py                 # Export type definitions
├── examples/                            # Example data and scripts
│   ├── data/                            # Sample datasets
│   │   ├── sample_pm25.nc               # Sample PM2.5 data
│   │   ├── sample_points.csv            # Sample monitoring points
│   │   └── sample_regions.geojson       # Sample regions
│   ├── notebooks/                       # Jupyter notebooks
│   │   ├── advanced_spatial_analysis.ipynb
│   │   ├── data_extraction_analysis.ipynb
│   │   ├── temporal_pattern_analysis.ipynb
│   │   └── test_data_read_example.ipynb
│   └── scripts/                         # Example Python scripts
│       ├── basic_workflow.py            # Basic usage examples
│       ├── batch_processing.py          # Batch processing example
│       ├── data_read_example.py         # Data reading example
│       ├── nuts3_analysis.py            # NUTS3 region analysis
│       └── te
