---
key: pypi/opendss-mcp-server
source: pypi
name: opendss-mcp-server
package: opendss-mcp-server
description: Model Context Protocol server for EPRI's OpenDSS power system simulator - enabling AI-powered
  distribution system analysis
registry_url: https://pypi.org/project/opendss-mcp-server/
version: 1.0.0
last_release: '2025-10-20'
repository_url: https://github.com/ahmedelshazly27/opendss-mcp-server
repository_declared_in_metadata: true
license_stated: MIT
author: Ahmed Elshazly <ahmedelshazly27@gmail.com>
probes:
- pypi:simple-index-sweep
probe_class: broad-acronym
found_by:
- search
first_seen: '2026-08-28'
---

# OpenDSS MCP Server

<div align="center">

**Conversational Power System Analysis with AI**

*Reduce distribution planning studies from weeks to minutes through natural language interaction*

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](tests/)
[![Code Coverage](https://img.shields.io/badge/coverage-41%25-yellow.svg)](tests/)
[![OpenDSS](https://img.shields.io/badge/OpenDSS-9.8%2B-orange.svg)](https://www.epri.com/OpenDSS)
[![MCP](https://img.shields.io/badge/MCP-1.0-purple.svg)](https://modelcontextprotocol.io/)

[Features](#features) •
[Installation](docs/INSTALLATION.md) •
[Quick Start](#quick-start) •
[Documentation](#documentation) •
[Examples](#examples) •
[Contributing](#contributing)

</div>

---

## Overview

The **OpenDSS MCP Server** is a Model Context Protocol (MCP) server that connects Claude AI with EPRI's OpenDSS power system simulator. It enables distribution planning engineers, utilities, and researchers to perform sophisticated power system analysis through **conversational natural language** instead of complex scripting.

### The Problem

Traditional distribution system analysis requires:
- ⏱️ **2-3 weeks** per study
- 💻 Complex Python/DSS scripting
- 📊 Manual data processing
- 🎨 Custom visualization code
- 📝 Extensive documentation

### The Solution

With OpenDSS MCP Server:
- ⚡ **30 minutes** per study (100x faster)
- 💬 Natural language commands via Claude
- 🤖 Automatic analysis and insights
- 📈 Professional visualizations generated automatically
- 📋 Instant report generation

**Example:**
```
You: "Load IEEE13 feeder, optimize 2MW solar placement, and show voltage improvements"

Claude: ✓ Loaded IEEE13 (13 buses)
        ✓ Optimized solar placement → Bus 675
        ✓ Loss reduction: 32.4%
        ✓ Voltage violations fixed: 3
        [Voltage profile visualization shown]
```

---

## Features

### 🎯 Core Capabilities

#### **7 Comprehensive MCP Tools**

1. **🔌 IEEE Feeder Loading**
   - IEEE 13, 34, and 123 bus test systems
   - Official EPRI test cases
   - On-the-fly circuit modifications
   - Full topology and component data

2. **⚡ Power Flow Analysis**
   - Snapshot, daily, and yearly modes
   - Convergence checking
   - Harmonic frequency analysis
   - Loss calculations and voltage profiles

3. **📊 Voltage Quality Assessment**
   - ANSI C84.1 compliance checking
   - Violation identification and reporting
   - Phase-specific analysis
   - Before/after comparisons

4. **🌞 DER Placement Optimization**
   - Solar, battery, wind, and EV chargers
   - Multiple objectives (minimize losses, maximize capacity, reduce violations)
   - Smart inverter volt-var control
   - Ranked candidate bus comparison

5. **📈 Hosting Capacity Analysis**
   - Incremental capacity testing
   - Voltage and thermal constraint identification
   - Capacity curves generation
   - Multi-location assessment

6. **⏰ Time-Series Simulation**
   - Daily/seasonal load profiles
   - Solar/wind generation patterns
   - Energy analysis (kWh, not just kW)
   - Convergence tracking

7. **🎨 Professional Visualization**
   - Voltage profile bar charts
   - Network topology diagrams
   - Time-series multi-panel plots
   - Capacity curves
   - Harmonics spectrum analysis

### ⚙️ Advanced Features

#### **🎼 Harmonics Analysis**
- IEEE 519 compliance checking
- Total Harmonic Distortion (THD) calculation
- Individual harmonic magnitudes (3rd, 5th, 7th, etc.)
- Frequency scan support
- Multi-bus harmonic spectrum visualization

#### **🔄 Smart Inverter Control**
- IEEE 1547-2018 compliant volt-var curves
- California Rule 21 support
- Custom control curve definition
- Volt-watt curtailment
- Real-time inverter status monitoring

#### **🧪 IEEE Test Feeders**
- **IEEE 13-bus**: Small system, ideal for testing
- **IEEE 34-bus**: Medium system with multiple regulators
- **IEEE 123-bus**: Large system for comprehensive studies
- Official EPRI-validated models
- Complete DSS source files included

#### **🔗 MCP Integration**
- Seamless Claude Desktop integration
- Natural language command interface
- Automatic tool selection
- Structured JSON responses
- Error handling and recovery

---

## Installation

### Quick Install

```bash
# Clone the repository
git clone https://github.com/ahmedelshazly27/opendss-mcp-server.git
cd opendss-mcp-server

# Install the package
pip install -e .

# Verify installation
python -c "from opendss_mcp import server; print('✓ OpenDSS MCP Server installed successfully!')"
```

### Claude Desktop Configuration

Add to your Claude Desktop config file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

**Linux:** `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "opendss": {
      "command": "python",
      "args": ["-m", "opendss_mcp.server"],
      "env": {
        "PYTHONPATH": "/absolute/path/to/opendss-mcp-server/src"
      }
    }
  }
}
```

📖 **For detailed installation instructions, see [INSTALLATION.md](docs/INSTALLATION.md)**

---

## Quick Start

### 1. Basic Power Flow Analysis

**Ask Claude:**
```
Load the IEEE13 feeder and run a power flow analysis. Show me the voltage range and total losses.
```

**Result:**
```
✓ IEEE13 feeder loaded (13 buses, 11 lines)
✓ Power flow converged in 8 iterations

Voltage Range: 0.9542 - 1.0500 pu
Total Losses: 116.2 kW + 68.3 kVAr
```

### 2. DER Integration Study

**Ask Claude:**
```
Optimize placement of 2000 kW solar to minimize losses on the IEEE13 feeder.
Show the optimal location and improvement metrics.
```

**Result:**
```
✓ Optimal Location: Bus 675

Improvements:
  • Loss Reduction: 37.7 kW (32.4%)
  • Voltage Improvement: +0.017 pu
  • Violations Fixed: 3

[Voltage profile visualization shown]
```

### 3. Hosting
