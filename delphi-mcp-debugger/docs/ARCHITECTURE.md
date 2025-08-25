# Архитектура Delphi MCP Debugger (MVP)

## Обзор

Проект состоит из двух основных компонентов:
- MCP сервер (Python, `delphi_mcp_debugger`) — экспортирует инструменты отладки (`run`, `cont`, `step_over`, `set_breakpoint`, `remove_breakpoint`, `poll_events`) и общается с плагином RAD Studio по TCP (JSON-RPC 2.0).
- Плагин RAD Studio (Delphi, OTAPI) — поднимает JSON-RPC сервер, управляет отладчиком через OTAPI (`IOTADebuggerServices`, `IOTABreakpointServices`) и шлёт события наружу.

## Потоки данных
1) MCP клиент (например, Cursor) вызывает MCP инструмент `run` → MCP сервер отправляет JSON-RPC `debug/run` плагину.
2) Плагин выполняет `Run` через OTAPI и отправляет уведомления `debug/output`, `debug/stopped`, `debug/exited`.
3) MCP сервер складывает события в очередь и отдаёт по `poll_events` либо ретранслирует при HTTP транспорте.

## Транспорт и протокол
- TCP localhost, JSON-RPC 2.0, один клиент.
- Handshake: `auth/handshake { token }` (опционально).
- Методы запроса: `debug/run|continue|stepOver|setBreakpoint|removeBreakpoint`.
- Уведомления: `debug/output|stopped|exited`.

## Карта MCP → OTAPI
- `run` → `IOTADebuggerServices.Run`
- `cont` → `IOTADebuggerServices.Run`
- `step_over` → `IOTADebuggerServices.StepOver`
- `set_breakpoint(file,line)` → `IOTABreakpointServices.AddSourceBreakpoint`
- `remove_breakpoint(id|file,line)` → `IOTABreakpointServices.DeleteBreakpoint`

## UI индикатор
Плагин добавляет кнопку в тулбар IDE (зелёный/красный) по статусу подключения клиента к JSON-RPC серверу.

## Ограничения MVP
- Один клиент; обработка ошибок упрощена.
- События остановки определяются эвристически через `DebuggerStateChange`.
- ID брейкпоинтов — ключ `file:line`.