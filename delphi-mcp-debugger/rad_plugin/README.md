# RAD Studio OTAPI плагин: Delphi MCP Debugger (MVP)

Минимальный плагин RAD Studio, который поднимает TCP JSON-RPC сервер и реализует команды отладки: run/continue/stepOver и set/remove breakpoint.

## Сборка

1. Откройте `DelphiMcpDebugger.dproj` в RAD Studio (Win32).
2. Убедитесь, что Indy установлен: пакеты `IndyCore`, `IndySystem`, `IndyProtocols`.
3. Соберите и установите пакет (design-time package).
4. После установки IDE автоматически загрузит Wizard, который поднимет TCP сервер на `127.0.0.1:5645`.

Переменные окружения:
- `RAD_PLUGIN_PORT` — порт (по умолчанию 5645)
- `RAD_PLUGIN_TOKEN` — секрет для рукопожатия (опционально)

## JSON-RPC

Запросы (входящие из MCP-сервера):
- `debug/run` { project?: string, args: string[] }
- `debug/continue` {}
- `debug/stepOver` {}
- `debug/setBreakpoint` { file: string, line: number }
- `debug/removeBreakpoint` { id?: string, file?: string, line?: number }

События (уведомления наружу):
- `debug/output` { category: "stdout"|"stderr", text: string }
- `debug/stopped` { reason: string, threadId?: number }
- `debug/exited` { exitCode?: number }

## Ограничения MVP
- OTAPI вызовы частично заглушены, базовый контроль: Run/StepOver/Continue, брейкпоинты — заготовки.
- Поддерживается один клиент.