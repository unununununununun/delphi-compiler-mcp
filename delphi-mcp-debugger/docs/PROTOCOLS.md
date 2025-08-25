# Протоколы

## JSON-RPC (плагин ⇄ MCP сервер)

Transport: TCP, JSON-RPC 2.0, один клиент.

### Аутентификация (опционально)
- notify: `auth/handshake` { token: string }

### Методы запроса
- `debug/run` { project?: string, args: string[] } → { status: 'running' }
- `debug/continue` {} → { status: 'continued' }
- `debug/stepOver` {} → { status: 'stepped' }
- `debug/setBreakpoint` { file: string, line: number } → { id: string, file, line }
- `debug/removeBreakpoint` { id?: string, file?: string, line?: number } → { removed: boolean }

### Уведомления (plugin → MCP)
- `debug/output` { category: 'stdout'|'stderr', text: string }
- `debug/stopped` { reason: string, threadId?: number }
- `debug/exited` { exitCode?: number }

## MCP инструменты (FastMCP)
- `run(project?: string, args?: string[])` → JSON
- `cont()` → JSON
- `step_over()` → JSON
- `set_breakpoint(file: string, line: int)` → JSON
- `remove_breakpoint(file?: string, line?: int, breakpoint_id?: string)` → JSON
- `poll_events(max_items?: int = 50)` → Array<Event>