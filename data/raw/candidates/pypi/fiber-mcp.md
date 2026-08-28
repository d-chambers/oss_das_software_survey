---
key: pypi/fiber-mcp
source: pypi
name: fiber-mcp
package: fiber-mcp
description: FIBER — Optical operations platform MCP server for AI datacenters (gNMI telemetry, ML predictions,
  Digital Twin, NCCL-optical correlation, SPARQL semantic queries).
registry_url: https://pypi.org/project/fiber-mcp/
version: 1.1.0
last_release: '2026-05-13'
repository_url: https://github.com/liveplex-cpu/hikari
repository_declared_in_metadata: true
license_stated: MIT
author: Satoshi Holdings <contact@fiber.ac>
probes:
- pypi:simple-index-sweep
probe_class: broad-acronym
found_by:
- search
first_seen: '2026-08-28'
---

# FIBER MCP Server

<!-- MCP Registry ownership verification (required by registry.modelcontextprotocol.io) -->
mcp-name: io.github.liveplex-cpu/fiber

Model Context Protocol (MCP) server for the **FIBER AI Infrastructure Reliability Platform**.

Expose 24 curated FIBER endpoints as MCP tools (+ 3 write tools behind a flag) so Claude Code / Cursor / Claude Desktop / VS Code Copilot can query optical telemetry, run Digital Twin what-if scenarios, fetch ML predictions, and generate postmortems — directly from developer IDEs.

## Why MCP?

Until now, using FIBER meant opening the dashboard or calling the REST API. With MCP, your AI assistant just… knows.

```
User (in Claude Code): "leaf-010 Ethernet1/43 의 72시간 RUL 어떻게 돼?"

Claude  → calls tool: fiber_ml_predict_rul(switch_name="leaf-010", port_name="Ethernet1/43")
         → returns: {"rul_hours": 0.01, "urgency": "imminent", "val_mae_hours": 2.99}

Claude (to user): "LSTM 모델이 잔존 수명을 0.01시간으로 예측합니다 —
                 즉시 교체 필요 (urgency: imminent). 모델 검증 MAE는 2.99h입니다."
```

## Tools (24 read + 3 write)

| Category | Tools |
|---|---|
| Discovery | `fiber_health`, `fiber_info`, `fiber_cluster_overview`, `fiber_list_ports`, `fiber_port_detail_history`, `fiber_list_alerts`, `fiber_top_risky_ports` |
| ML | `fiber_ml_rul_info`, `fiber_ml_predict_rul`, `fiber_ml_anomaly_scan` |
| CPO | `fiber_cpo_bank_status` |
| Digital Twin | `fiber_simulate_link_failure`, `fiber_digital_twin_monte_carlo`, `fiber_digital_twin_compare` |
| Counterfactual | `fiber_counterfactual_port`, `fiber_counterfactual_cluster` |
| NCCL | `fiber_nccl_summary`, `fiber_nccl_optical_correlation` |
| Benchmark | `fiber_run_benchmark_harness` |
| Sustainability | `fiber_sustainability`, `fiber_checkpoint_aware_windows` |
| Diagnosis | `fiber_list_diagnosis_reports`, `fiber_get_diagnosis_report`, `fiber_postmortem_timeline` |
| **Write (optional)** | `fiber_trigger_demo_scenario`, `fiber_ingest_nccl_events`, `fiber_create_rma` |

**Safety model**: all tools are read-only by default. Write tools only activate when `FIBER_ENABLE_WRITE=1` env var is set. The server uses the same API key / RBAC as the underlying FIBER REST API, so giving an MCP client a `viewer`-role key is strictly safer than handing out admin credentials.

## Install

### Quick
```bash
./setup.sh
```

### Manual
```bash
python3 -m venv ~/.fiber-mcp-venv
source ~/.fiber-mcp-venv/bin/activate
pip install -r requirements.txt
```

## Configure

### Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "fiber": {
      "command": "/Users/you/.fiber-mcp-venv/bin/python3",
      "args": ["/path/to/hikari/sdks/mcp/fiber_mcp_server.py"],
      "env": {
        "FIBER_API_URL": "https://api.fiber.ac",
        "FIBER_API_KEY": "your-key-here",
        "FIBER_ENABLE_WRITE": "0"
      }
    }
  }
}
```

Restart Claude Desktop. In a new conversation ask: *"What's FIBER's current cluster overview?"* — Claude should call `fiber_cluster_overview` and respond with live data.

### Claude Code (CLI)

Claude Code auto-discovers MCP servers configured in `~/.claude/mcp_servers.json`:

```json
{
  "fiber": {
    "command": "python3",
    "args": ["/path/to/fiber_mcp_server.py"],
    "env": {
      "FIBER_API_URL": "https://api.fiber.ac",
      "FIBER_API_KEY": "your-key"
    }
  }
}
```

### Cursor

Cursor follows the same MCP spec. Add the server under *Settings → MCP → Edit Config*.

## Test locally with MCP Inspector

```bash
npx -y @modelcontextprotocol/inspector python3 fiber_mcp_server.py
```

Opens a web UI where you can list tools and invoke them interactively.

## Environment variables

| Variable | Default | Purpose |
|---|---|---|
| `FIBER_API_URL` | `https://api.fiber.ac` | Base URL of your FIBER deployment |
| `FIBER_API_KEY` | `fiber-dev-key-change-in-production` | Bearer token (get via admin API) |
| `FIBER_ENABLE_WRITE` | `0` | Set to `1` to expose write tools |
| `FIBER_HTTP_TIMEOUT` | `30` | Per-request seconds |

## RBAC hints

- For AI assistants on an engineer's laptop, create a **`viewer`** role API key. All 22 read tools work; no accidental mutations.
- For an autonomous agent (e.g., oncall runbook runner), use **`operator`** + `FIBER_ENABLE_WRITE=1`.
- For demo environments, pair `admin` + `FIBER_ENABLE_WRITE=1` to unlock `fiber_trigger_demo_scenario`.

## User flow examples

Natural-language queries your AI assistant now handles:

- "How many CPO banks are in critical state?"
- "Show me the top 10 risky ports by risk score"
- "If we lose all 10 spine uplinks of leaf-010, how many GPUs go offline?"
- "Run the benchmark harness with seed 42 and summarize"
- "What's the checkpoint-aware maintenance window for the next 6 hours?"
- "Correlate NCCL bandwidth drops with optical anomalies over the last 15 minutes"
- "Generate a postmortem timeline for leaf-039 Ethernet1/43 covering the past 24h"

## Architecture

```
 Claude Code / Cursor / Claude Desktop
              │
              │  MCP stdio (JSON-RPC)
              ▼
 ┌──────────────────────────┐
 │  fiber_mcp_server.py     │ ── Python stdio MCP server
 │                          │    (25 tools, httpx client)
 └────────────┬─────────────┘
              │  HTTPS Bearer auth
              ▼
 ┌──────────────────────────┐
 │  https://api.fiber.ac    │ ── FIBER FastAPI (~45 endpoints)
 │  or localhost:8000       │
 └──────────────────────────┘
```

## Status

- Curated 27 tools (24 read + 3 write)
- stdio transport (SSE transport planned for remote/cloud use)
- Read-only by default; write tools guarded by env var
- Verified with `@modelcontextprotocol/inspector`

## Roadmap

- Streaming SSE endpoint for cloud deployment
- OAuth device flow (replace long-lived API keys)
- GraphQL subscription tool (live port updates)

## License

Same as FIBER — see repo root.
