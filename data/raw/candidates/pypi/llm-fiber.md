---
key: pypi/llm-fiber
source: pypi
name: llm-fiber
package: llm-fiber
description: A thin, fast, observable Python client for LLMs
registry_url: https://pypi.org/project/llm-fiber/
version: 1.0.1
last_release: '2025-09-08'
repository_url: https://github.com/aimlesx/llm-fiber
repository_declared_in_metadata: true
license_stated: MIT
author: Aimless
probes:
- pypi:simple-index-sweep
probe_class: broad-acronym
found_by:
- search
first_seen: '2026-08-28'
---

# <div align="center"> <img alt="llm-fiber logo" src="https://github.com/aimlesx/llm-fiber/blob/main/docs/assets/logo.png" width="140"/> <br/> llm-fiber </div>

<p align="center">
  <strong>A thin, fast, and production-ready Python client for LLMs.</strong>
</p>

<p align="center">
  Async-first with wire-speed streaming, consistent ergonomics across providers, and built-in observability.
</p>

<p align="center">
  <a href="https://pypi.org/project/llm-fiber/"><img alt="PyPI" src="https://img.shields.io/pypi/v/llm-fiber.svg"></a>
  <a href="https://codecov.io/github/aimlesx/llm-fiber" ><img src="https://codecov.io/github/aimlesx/llm-fiber/graph/badge.svg"/></a>
  <a href="./LICENSE"><img alt="License" src="https://img.shields.io/badge/License-MIT-yellow.svg"></a>
</p>

---

`llm-fiber` is designed for developers who need a reliable, high-performance, and observable way to interact with multiple LLM providers. It eliminates boilerplate and provides a robust toolkit for building production-grade applications, with minimal dependencies and a clean, modern API.

## ✨ Features

`llm-fiber` comes packed with features designed for production systems.

#### **Core & Multi-Provider**
- **🔄 Async-first with Sync Wrappers**: Native `async/await` for performance, with convenient sync wrappers for simplicity.
- **🎯 Multi-Provider Support**: Use OpenAI, Anthropic, and Google Gemini models through a single, unified interface.
- **🤖 Smart Provider Routing**: Automatically detects the right provider from the model name (e.g., `"gpt-4o-mini"` → OpenAI).

#### **Performance & Cost Control**
- **🌊 First-Class Streaming**: Consume tokens at wire-speed with a clean, backpressure-friendly event stream.
- **💾 Intelligent Caching**: Reduce latency and cost with built-in, deterministic caching (in-memory LRU+TTL).
- **💰 Budget & Cost Controls**: Enforce token and cost ceilings per-call to prevent runaway spend.
- **🚀 Batch Operations**: Process multiple requests concurrently with configurable rate limiting and error handling.

#### **Reliability & Observability**
- **🔁 Robust Retries**: Automatic, configurable exponential backoff with jitter for transient errors.
- **⏱️ Granular Timeouts**: Control connect, read, and total call time to prevent hangs.
- **🔍 Built-in Observability**: Get immediate insights with structured logging and metrics for latency, TTFB, retries, and token usage.
- **🛠️ Normalized Tool Calling**: A consistent interface for tool/function calls across providers.

## 🚀 Quick Start

Get up and running in minutes.

**1. Installation**
```bash
pip install llm-fiber
```

**2. Set Environment Variables**
```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GEMINI_API_KEY="..."
```

**3. Make your first calls**

```python
import asyncio
from llm_fiber import Fiber, ChatMessage, StreamEventType

# Create a client with auto-detected providers
# The provider is automatically inferred from the model name
fiber = Fiber.from_env()

async def main():
    # Simple text-in, text-out using the best model for the job
    response = await fiber.ask(
        "What is the capital of France?",
        model="gpt-4o-mini" # -> routes to OpenAI
    )
    print(f"Response from GPT: {response}")

    # Full chat with streaming from another provider
    print("\nStreaming response from Claude:")
    async for event in fiber.chat_stream(
        model="claude-3-sonnet-20240229", # -> routes to Anthropic
        messages=[ChatMessage.user("Count from 1 to 5")],
        temperature=0.7
    ):
        if event.type == StreamEventType.CHUNK:
            print(event.delta, end="", flush=True)

# You can also use the sync interface
print("\n\nSync response from Gemini:")
sync_response = fiber.sync.ask(
    "Hello, world!",
    model="gemini-1.5-flash" # -> routes to Google
)
print(sync_response)

asyncio.run(main())
```

## 📖 Documentation

For a deep dive into the architecture, features, and design decisions, check out our **[Full Developer Documentation](./docs/index.md)**.

Key pages include:
- **[Architecture Overview](./docs/index.md)** (C4-lite)
- **[Feature: Retries & Budgets](./docs/features/retries-and-budgets.md)**
- **[Feature: Caching](./docs/features/caching.md)**
- **[Feature: Observability](./docs/features/observability.md)**
- **[Project Roadmap](./docs/roadmap.md)**

## 💡 More Examples

### Tool Calling (normalized)

A concise example of receiving a tool call during streaming, normalizing it, and replying with a tool response message.

```python
import asyncio
from llm_fiber import (
    Fiber,
    ChatMessage,
    StreamEventType,
    extract_tool_calls_from_stream_events,
    create_tool_response_message,
)

async def tool_calling_example():
    fiber = Fiber.from_env()

    tools = [{
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather by city",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"],
            },
        },
    }]

    events = []
    async for ev in fiber.chat_stream(
        model="gpt-4o-mini",
        messages=[ChatMessage.user("What's the weather in Paris?")],
        tools=tools,
    ):
        events.append(ev)

    # Normalize tool calls across providers
    tool_calls = extract_tool_calls_from_stream_events(events)
    for tc in tool_calls:
        # Call your function here; then respond with a tool message
        tool_response = create_tool_response_message(
            tool_call_id=tc.id,
            content='{"temp_c": 21, "condition": "sunny"}',
            name=tc.name,
        )

        final = await fiber.chat(
            model="gpt-4o-mini",
            messages=[ChatMessage.user("What's the weather in Paris?"), tool_response],
        )
        print(final.text)

asyncio.run(tool_calling_example())
```

### Caching

Enable the in-memory cache to instantly return re
