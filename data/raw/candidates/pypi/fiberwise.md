---
key: pypi/fiberwise
source: pypi
name: fiberwise
package: fiberwise
description: FiberWise CLI and platform tools
registry_url: https://pypi.org/project/fiberwise/
version: 0.1.8
last_release: '2026-04-14'
repository_url: https://github.com/fiberwise-ai/fiberwise
repository_declared_in_metadata: true
license_stated: MIT
author: FiberWise <dev@fiberwise.ai>
probes:
- pypi:simple-index-sweep
probe_class: broad-acronym
found_by:
- search
first_seen: '2026-08-28'
---

# FiberWise

A comprehensive command line tool and activation system for FiberWise agents with dependency injection support.

## Overview

FiberWise provides:
- **Agent Activation System**: Register, version, and execute agents
- **Dependency Injection**: Automatic service injection into agents
- **SDK Integration**: Seamless integration with `fiberwise_sdk`
- **Multi-Database Support**: SQLite, DuckDB, MySQL, PostgreSQL
- **CLI Interface**: Easy command-line activation and management
- **Web Interface**: Built-in web server for agent management

## Installation

```bash
pip install -e .
```

For the full SDK experience, also install:
```bash
pip install fiberwise-sdk
```

## Default Credentials

**First time setup:**
- Username: `admin`
- Email: `admin@fiberwise.local`
- Password: `fiber2025!`

See [DEFAULT_CREDENTIALS.md](../DEFAULT_CREDENTIALS.md) for complete details.

## Quick Start


### 1. Initialize the FiberWise Environment

```bash
# Initialize FiberWise project (creates config, database, and default admin user)
fiber initialize
```

**Options:**

- `--db-path <path>`: Set custom database file path (default: ./fiberwise.db)
- `--force`: Overwrite existing config/database if present
- `--no-admin`: Skip creation of default admin user
- `--no-web`: Do not launch the web UI after initialization
- `--no-browser`: Do not open browser after starting web UI
- `--host <host>`: Set web server host (default: 127.0.0.1)
- `--port <port>`: Set web server port (default: 8000)

Example:
```bash
fiber initialize --db-path ./mydb.db --no-browser --host 0.0.0.0 --port 3000
```

For details on how instance routing works with initialization and activation, see the [CLI Instance Routing Guide](../CLI_INSTANCE_ROUTING_GUIDE.md).

---

### 2. Start the Web Server

```bash
# Start FiberWise web interface (if not started by initialize)
fiber start
```

### 2. Configure Account and Providers

```bash
# Add your FiberWise API configuration
python -m fiberwise.cli account add-config --name "prod" --api-key "your-api-key" --base-url "https://api.fiberwise.ai" --set-default

# Import providers from your app for dependency injection
python -m fiberwise.cli account import-providers --default

# List available providers
python -m fiberwise.cli account list-providers
```

### 3. Create an Agent with Dependency Injection

```python
def run_agent(input_data, fiber=None, llm_service=None, storage=None, oauth_service=None):
    """Agent with automatic dependency injection"""
    result = {"input": input_data, "services": {}}
    
    # FiberApp SDK automatically injected
    if fiber:
        try:
            agents = await fiber.agents.list()
            result["services"]["fiber"] = f"Connected to FiberApp - {len(agents)} agents available"
        except Exception as e:
            result["services"]["fiber"] = f"FiberApp error: {e}"
    
    # LLM service automatically injected
    if llm_service:
        try:
            response = await llm_service.generate("Test prompt")
            result["services"]["llm"] = "LLM service connected"
        except Exception as e:
            result["services"]["llm"] = f"LLM error: {e}"
    
    # Storage service automatically injected
    if storage:
        result["services"]["storage"] = "Storage service connected"
    
    # OAuth service automatically injected
    if oauth_service:
        try:
            providers = await oauth_service.get_available_providers()
            result["services"]["oauth"] = f"OAuth providers: {providers}"
        except Exception as e:
            result["services"]["oauth"] = f"OAuth error: {e}"
    
    return result
```

### 4. Run the Agent

```bash
# Run locally with dependency injection (default)
fiber activate --input-data '{"query": "test"}' ./my_agent.py

# Run against local server API
fiber activate --input-data '{"query": "test"}' ./my_agent.py --to-instance default

# Run against remote server
fiber activate --input-data '{"query": "test"}' ./my_agent.py --to-instance "production"

# Run with verbose output to see injected services and routing
fiber activate --verbose --input-data '{"query": "test"}' ./my_agent.py --to-instance local
```

## CLI Usage

### Basic Commands

```bash
# Activate an agent (local direct execution - default)
fiber activate --input-data '{"key": "value"}' ./agent.py

# Activate against local server API
fiber activate --input-data '{"key": "value"}' ./agent.py --to-instance default

# Activate against remote server
fiber activate --input-data '{"key": "value"}' ./agent.py --to-instance "production"

# Verbose output for debugging
fiber activate --verbose --input-data '{"key": "value"}' ./agent.py

# Specify version with instance routing
fiber activate --version "2.0.0" --input-data '{"key": "value"}' ./agent.py --to-instance "production"
```

### Web Server Commands

```bash
# Start the FiberWise web server (default: localhost:8000)
fiber start

# Start with custom host and port
fiber start --host 0.0.0.0 --port 3000

# Start with development features
fiber start --reload --no-browser

```

#### Start Command Options

- `--host`: Host address to bind to (default: 127.0.0.1)
- `--port`: Port number to use (default: 8000)  
- `--reload`: Enable auto-reload for development
- `--no-browser`: Disable automatic browser opening

### Account Management Commands

The account management system integrates with `fiberwise-common` to store configurations and providers in the database for dependency injection.

```bash
# Login with configuration file
fiber account login --config ./my-config.json

# Add configuration directly
fiber account add-config --name "prod" --api-key "your-key" --base-url "https://api.fiberwise.ai" --set-default

# Import providers from app (for dependency injection)
fiber account import-providers --app-id your-app-id --default

# List providers (local database)
fiber account list-providers --to-instance local

# List providers (remote server)
fiber account list-providers --to-instance "product
