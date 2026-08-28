---
key: pypi/das-bridge
source: pypi
name: das-bridge
package: das-bridge
description: Python client for DAS Trader Pro CMD API
registry_url: https://pypi.org/project/das-bridge/
version: 1.3.0
last_release: '2026-04-03'
repository_url: https://github.com/jefrnc/das-bridge
repository_declared_in_metadata: true
license_stated: MIT
author: Joseph
probes:
- pypi:simple-index-sweep
probe_class: broad-acronym
found_by:
- search
first_seen: '2026-08-28'
---

# DAS Trader Python API Client

<div align="center">

[![PyPI version](https://img.shields.io/pypi/v/das-bridge.svg)](https://pypi.org/project/das-bridge/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://img.shields.io/pypi/dm/das-bridge.svg)](https://pypi.org/project/das-bridge/)

[English](README.md) | [Español](README.es.md)

</div>

Complete Python client for the DAS Trader Pro CMD API that enables automated trading, real-time order management, position tracking, and market data streaming.

## 🚀 Key Features

### Core Trading Capabilities
- **Complete Trading**: Send, modify, and cancel orders (Market, Limit, Stop, Peg, etc.)
- **Real-Time Market Data**: Level 1, Level 2, and Time & Sales streaming
- **Position Management**: Automatic position tracking and real-time P&L
- **Historical Data**: Access to daily and minute charts
- **Specific Order Queries**: Get pending orders and executed orders separately

### 💰 Risk Management & Strategies (NEW!)
- **Dollar-Based Position Sizing**: Calculate shares to risk exact dollar amounts
- **Pre-Built Strategies**: Long/short with automatic stops and targets
- **Risk/Reward Calculations**: Built-in ratio calculations and validation
- **Scale-Out Support**: Exit positions at multiple target levels
- **Buying Power Validation**: Automatic position size validation
- **Slippage Modeling**: Conservative position sizing with slippage consideration

### Enhanced Features
- **Production-Grade Logging**: Structured logging with rotation and masking
- **Connection Resilience**: Circuit breaker pattern with exponential backoff
- **Configuration Management**: Environment variables and JSON config support
- **Enhanced Error Handling**: Categorized exceptions with recovery guidance
- **Multi-Format Parsing**: Handles various DAS response formats
- **Automatic Reconnection**: Robust connection handling with auto-reconnect
- **Native Asyncio**: High performance with concurrent operations
- **Type Safety**: Fully typed for better IDE support

## 📋 Requirements

- Python 3.8+
- DAS Trader Pro with CMD API enabled
- Valid DAS Trader account

## ⚡ Quick Installation

### From PyPI (Recommended)

```bash
pip install das-bridge
```

### From Source (Development)

```bash
git clone https://github.com/jefrnc/das-bridge.git
cd das-bridge
pip install -e .
```

### Optional Dependencies

```bash
# For notifications
pip install aiohttp

# For data analysis
pip install numpy pandas matplotlib

# For Windows desktop notifications
pip install win10toast  # Windows only

# For configuration management
pip install python-dotenv
```

## 🔧 Configuration

### 1. Environment Variables
```bash
cp .env.example .env
# Edit .env with your credentials
```

### 2. Basic Configuration
```python
# .env
DAS_HOST=localhost
DAS_PORT=9910
DAS_USERNAME=your_das_username
DAS_PASSWORD=your_das_password
DAS_ACCOUNT=your_das_account
```

## 🎯 Basic Usage

```python
import asyncio
from das_trader import DASTraderClient, OrderSide, OrderType, MarketDataLevel

async def main():
    # Create client
    client = DASTraderClient(host="localhost", port=9910)
    
    try:
        # Connect to DAS Trader
        await client.connect("your_username", "your_password", "your_account")
        
        # Get buying power
        bp = await client.get_buying_power()
        print(f"Buying Power: ${bp['buying_power']:,.2f}")
        
        # Subscribe to market data
        await client.subscribe_quote("AAPL", MarketDataLevel.LEVEL1)
        
        # Get quote
        quote = await client.get_quote("AAPL")
        print(f"AAPL: Bid ${quote.bid} | Ask ${quote.ask} | Last ${quote.last}")
        
        # Send order
        order_id = await client.send_order(
            symbol="AAPL",
            side=OrderSide.BUY,
            quantity=100,
            order_type=OrderType.LIMIT,
            price=150.00
        )
        print(f"Order sent: {order_id}")
        
        # Check positions
        positions = client.get_positions()
        for pos in positions:
            if not pos.is_flat():
                print(f"{pos.symbol}: {pos.quantity} shares, "
                      f"P&L: ${pos.unrealized_pnl:.2f}")
        
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

## 🔥 Enhanced Capabilities

### Advanced Order Management
```python
# Get specific order types
pending_orders = await client.get_pending_orders()
executed_orders = await client.get_executed_orders()

# Enhanced market data
level1_data = await client.get_level1_data("AAPL")
montage_data = await client.get_montage_data("AAPL")

# Robust buying power (handles multi-line responses)
bp_data = await client.get_buying_power()
```

### Production-Ready Features
```python
# Enhanced logging with rotation
from das_trader.enhanced_logger import EnhancedDASLogger

logger = EnhancedDASLogger(
    account_id="TRADER123",
    log_dir="logs/production",
    max_log_size=50*1024*1024  # 50MB rotation
)

# Connection resilience
from das_trader.connection_resilience import ConnectionResilientManager

resilient_mgr = ConnectionResilientManager(
    client.connection,
    max_reconnect_attempts=5,
    health_check_interval=60.0
)

# Configuration management
from das_trader.config_manager import load_das_config

config = load_das_config("config.json")
client = DASTraderClient(**config.get_client_config())
```

### Smart Locate Manager

das-bridge includes an intelligent locate manager that helps you analyze and request stock locates for short selling with volume and cost controls.

```python
# Analyze locate cost and availability
analysis = await client.locate_manager.analyze_locate(
    symbol="AAPL",
    desired_shares=500
)

print(f"Recommendation: {analysis['recommendation']}")
print(f"Locate Rate: ${analysis['locate_rate']:
