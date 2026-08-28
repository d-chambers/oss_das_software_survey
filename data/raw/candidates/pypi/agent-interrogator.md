---
key: pypi/agent-interrogator
source: pypi
name: agent-interrogator
package: agent-interrogator
description: An AI agent interrogation framework for identifying attack surface.
registry_url: https://pypi.org/project/agent-interrogator/
version: 0.2.0
last_release: '2026-05-04'
repository_url: https://github.com/qwordsmith/agent-interrogator
repository_declared_in_metadata: true
license_stated: Apache-2.0
author: Michael Samson
probes:
- pypi:simple-index-sweep
probe_class: domain-specific
found_by:
- search
first_seen: '2026-08-28'
---

# Agent Interrogator

<p align="center">
  <img src="https://raw.githubusercontent.com/qwordsmith/agent-interrogator/refs/heads/main/assets/logo.webp" alt="Agent Interrogator Logo" width="400" />
</p>

<p align="center">
  <strong>Systematically discover and map AI agent attack surface for security research</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/agent-interrogator/">
    <img src="https://badge.fury.io/py/agent-interrogator.svg" alt="PyPI version">
  </a>
  <a href="https://www.python.org/downloads/">
    <img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="Python 3.9+">
  </a>
  <a href="https://opensource.org/licenses/Apache-2.0">
    <img src="https://img.shields.io/badge/License-Apache%202.0-yellow.svg" alt="License: Apache 2.0">
  </a>
</p>

---

## What is Agent Interrogator?

Agent Interrogator is a Python library designed for **security researchers** to systematically discover and analyze AI agent attack surface through automated interrogation. It uses iterative discovery cycles to map an agent's available tools (functions).

### Why Use Agent Interrogator?

- **🔍 Attack Surface Discovery**: Automatically discovers agent capabilities and supporting tools without requiring documentation
- **🛡️ Security Research**: Purpose-built for vulnerability assessment and prompt injection testing
- **📊 Structured Output**: Generates structured profiles perfect for integration with other security tools
- **🔄 Iterative Analysis**: Uses smart prompt adaptation to uncover hidden or complex capabilities
- **🚀 Flexible Integrations**: Works with any agent via customizable callback functions

### Perfect For:
- Security researchers testing AI agents for vulnerabilities
- Red teams conducting agent penetration testing
- Security teams auditing agent functionality

---

## Quick Start

### Installation

```bash
pip install agent-interrogator
```

### Basic Usage

Here's a minimal example that interrogates an agent:

```python
import asyncio
from agent_interrogator import AgentInterrogator, InterrogationConfig, LLMConfig, ModelProvider

# Configure the interrogator
config = InterrogationConfig(
    llm=LLMConfig(
        provider=ModelProvider.OPENAI,
        model_name="gpt-4.1",
        api_key="your-openai-api-key"
    ),
    max_iterations=5
)

# Define how to interact with your target agent
async def my_agent_callback(prompt: str) -> str:
    """
    This function defines how to send prompts to your target agent.
    Replace this with your actual agent interaction logic.
    """
    # Example: HTTP API call to your agent
    # response = await call_your_agent_api(prompt)
    # return response.text
    
    # For demo purposes, return a mock response
    return "I can help with web searches, file operations, and calculations."

# Run the interrogation
async def main():
    interrogator = AgentInterrogator(config, my_agent_callback)
    profile = await interrogator.interrogate()
    
    # View discovered capabilities
    print(f"Discovered {len(profile.capabilities)} capabilities:")
    for capability in profile.capabilities:
        print(f"  - {capability.name}: {capability.description}")
        for f in capability.functions:
            print(f"    Function Name: {f.name}")
            print(f"    Function Parameters: {f.parameters}")
            print(f"    Function Return Type: {f.return_type}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Expected Output

```
Discovered 3 capabilities:
  - web_search: Search the internet for information
    Function Name: search_web
    Function Parameters: [ { "name": "query", "type": "string", "description": "The search query", "required": true }, { "name": "max_results", "type": "integer", "description": "Maximum number of results", "required": false, "default": 5 } ]
    Function Return Types: list[SearchResult]
...
```

---

## Installation

### Standard Installation

```bash
pip install agent-interrogator
```

### Development Installation

For contributors or advanced users who want to modify the code:

```bash
git clone https://github.com/qwordsmith/agent-interrogator.git
cd agent-interrogator
pip install -e .[dev]
```

### Requirements

- **Python**: 3.9 or higher
- **OpenAI API Key**: For using GPT models (optional, can use Ollama or any OpenAI-compatible endpoint instead)
- **Dependencies**: Automatically installed with pip

---

## Configuration

Agent Interrogator supports OpenAI, a local Ollama daemon, or any OpenAI-compatible endpoint (vLLM, LM Studio, LocalAI, etc.) for analyzing agent responses:

### OpenAI Configuration

```python
from agent_interrogator import InterrogationConfig, LLMConfig, ModelProvider, OutputMode

config = InterrogationConfig(
    llm=LLMConfig(
        provider=ModelProvider.OPENAI,
        model_name="gpt-4.1",
        api_key="your-openai-api-key"
    ),
    max_iterations=5,  # Maximum discovery cycles
    output_mode=OutputMode.STANDARD  # QUIET, STANDARD, or VERBOSE
)
```

> **Optional:** pass `openai=OpenAIConfig(timeout=180.0)` on `LLMConfig` if you
> want to override the OpenAI client's default request timeout. Provider parity
> with `OllamaConfig` and `OpenAICompatibleConfig`, which both expose `timeout`.

> **Newer OpenAI reasoning models (gpt-5.x, o1, o3, o4):** auto-detected by
> name prefix — the library omits its default `temperature=0.1` for these so
> they fall back to the only value they accept (1.0). No config changes
> needed. To force a temperature anyway (or override for any model), pass
> `model_kwargs={"temperature": ...}` on `LLMConfig`.

### Ollama Configuration (local models)

```python
from agent_interrogator import OllamaConfig

config = InterrogationConfig(
    llm=LLMConfig(
        provider=ModelProvider.OLLAMA,
        model_name="llama3.2:latest",  # Any model pulled into your Ollama daemon
        ollama=OllamaConfig(
            host="http://localhost:11434",
            timeout=120.0,
            options={"temperature": 0.1,
