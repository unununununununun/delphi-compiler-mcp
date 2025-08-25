# Delphi MCP Debugger (MVP)

Minimal MCP server that exposes debugging controls for RAD Studio via a TCP JSON-RPC plugin.

## Overview

- MCP tools: `run`, `continue`, `step_over`, `set_breakpoint`, `remove_breakpoint`.
- Connects to a RAD Studio Open Tools API plugin over TCP (JSON-RPC 2.0).
- Streams debug events from plugin and relays them through MCP server facilities.

## Install (local dev)

```bash
pip install -e .
```

## Run

```bash
# Start mock plugin for local testing
python -m mock_rad_plugin.server

# In another shell, start the MCP debugger server (stdio)
delphi-mcp-debugger --transport stdio

# Example MCP calls
mcp call delphi-mcp-debugger run
mcp call delphi-mcp-debugger step_over
```

## Configuration

Environment variables (optional):

- `RAD_PLUGIN_HOST` default `127.0.0.1`
- `RAD_PLUGIN_PORT` default `5645`
- `RAD_PLUGIN_TOKEN` optional shared secret

## JSON-RPC messages (plugin side)

- Request: `debug/run`, `debug/continue`, `debug/stepOver`, `debug/setBreakpoint`, `debug/removeBreakpoint`
- Event notifications to server: `debug/output`, `debug/stopped`, `debug/exited`

