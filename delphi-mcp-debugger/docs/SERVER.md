# MCP сервер (Python)

Пакет: `delphi-mcp-debugger`

## Установка

```bash
pip install -e ./delphi-mcp-debugger
```

В Cursor: добавить в `.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "delphi-debugger": {
      "command": "delphi-mcp-debugger",
      "env": {
        "RAD_PLUGIN_HOST": "127.0.0.1",
        "RAD_PLUGIN_PORT": "5645",
        "RAD_PLUGIN_TOKEN": "secret"
      }
    }
  }
}
```

## Инструменты
- `run(project?: string, args?: string[])`
- `cont()`
- `step_over()`
- `set_breakpoint(file, line)`
- `remove_breakpoint(file?, line?, breakpoint_id?)`
- `poll_events(max_items=50)`

## События
- `debug/output`, `debug/stopped`, `debug/exited` — приходят из плагина, накапливаются в очереди и выдаются `poll_events`.