---
key: pypi/fiberai
source: pypi
name: fiberai
package: fiberai
description: Official Python SDK for Fiber AI API
registry_url: https://pypi.org/project/fiberai/
version: 0.0.54
last_release: '2026-08-19'
repository_url: https://github.com/fiber-ai/python-sdk
repository_declared_in_metadata: true
license_stated: MIT
author: Fiber AI <adi@fiber.ai>
probes:
- pypi:simple-index-sweep
probe_class: broad-acronym
found_by:
- search
first_seen: '2026-08-28'
---

# Fiber AI Python SDK

Official Python SDK for the [Fiber AI API](https://fiber.ai). Auto-generated from the [OpenAPI specification](https://api.fiber.ai/openapi.json).

[![PyPI version](https://badge.fury.io/py/fiberai.svg)](https://pypi.org/project/fiberai/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
pip install fiberai
```

## Quick Start

```python
from fiberai import Client
from fiberai.api.search import company_search
from fiberai.models import CompanySearchBody

# Create a client
client = Client(base_url="https://api.fiber.ai")

# Search for companies
body = CompanySearchBody.from_dict({
    "apiKey": "YOUR_API_KEY",
    "searchParams": {
        "standardIndustries": ["Software"],
        "employeeCount": {"gte": 50, "lte": 500}
    },
    "pageSize": 10,
})

response = company_search.sync(client=client, body=body)
```

### Async Usage

Every endpoint supports both sync and async usage out of the box:

```python
import asyncio
from fiberai import Client
from fiberai.api.search import company_search
from fiberai.models import CompanySearchBody

async def main():
    client = Client(base_url="https://api.fiber.ai")

    body = CompanySearchBody.from_dict({
        "apiKey": "YOUR_API_KEY",
        "searchParams": {
            "standardIndustries": ["Software"],
        },
        "pageSize": 10,
    })

    response = await company_search.asyncio(client=client, body=body)
    print(response)

asyncio.run(main())
```

### Detailed Responses

If you need access to status codes, headers, or the raw response, use the `_detailed` variants:

```python
from fiberai.api.search import company_search

# Sync
response = company_search.sync_detailed(client=client, body=body)
print(response.status_code)
print(response.headers)
print(response.parsed)  # The parsed response body

# Async
response = await company_search.asyncio_detailed(client=client, body=body)
```

## Available API Modules

The SDK covers all Fiber AI API endpoints, organized by category:

| Module | Description |
|--------|-------------|
| `fiberai.api.search` | Company, people, investor, investment, and job posting search |
| `fiberai.api.company_info` | Get company details by LinkedIn URL or domain |
| `fiberai.api.contact_details` | Fetch emails, phone numbers, and contact details |
| `fiberai.api.live_fetch` | Live enrichment for companies and people |
| `fiberai.api.kitchen_sink` | Combined enrichment endpoints |
| `fiberai.api.google_maps` | Google Maps business search |
| `fiberai.api.ai_research` | AI-powered domain lookup and research |
| `fiberai.api.exclusions` | Manage company and people exclusion lists |
| `fiberai.api.saved_search` | Saved search management |
| `fiberai.api.validation` | Email and phone validation |
| `fiberai.api.email_lookup` | Email-to-LinkedIn reverse lookup |
| `fiberai.api.account` | Organization credits and account info |
| `fiberai.api.enums` | Available enum values (industries, seniority, etc.) |
| `fiberai.api.typeaheads` | Typeahead/autocomplete endpoints |

## Configuration

### Custom Timeout

```python
import httpx
from fiberai import Client

client = Client(
    base_url="https://api.fiber.ai",
    timeout=httpx.Timeout(30.0),  # 30 second timeout
)
```

### Custom Headers

```python
client = Client(
    base_url="https://api.fiber.ai",
    headers={"X-Custom-Header": "value"},
)
```

## Links

- [Fiber AI](https://fiber.ai) — Main website
- [API Documentation](https://docs.fiber.ai) — Full API docs
- [TypeScript SDK](https://github.com/fiber-ai/typescript-sdk) — TypeScript/JavaScript SDK
- [Get API Key](https://fiber.ai/app/api) — Sign up for an API key

## License

MIT — see [LICENSE](./LICENSE) for details.
