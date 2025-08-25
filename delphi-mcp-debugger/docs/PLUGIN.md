# Плагин RAD Studio

## Дизайн
- Design-time пакет `DelphiMcpDebugger`.
- Wizard `TMcpDebuggerWizard` регистрируется при загрузке IDE.
- Поднимает TCP JSON-RPC сервер (Indy) и слушает команды.
- Добавляет кнопку-индикатор MCP на тулбар IDE (зелёный/красный).

## OTAPI
- `IOTADebuggerServices.Run`, `StepOver` — выполнение/шаги.
- `IOTABreakpointServices.AddSourceBreakpoint` — добавление брейкпоинта.
- `IOTABreakpointServices.DeleteBreakpoint` — удаление.
- `IOTADebuggerNotifier` — события жизненного цикла: `ProcessCreated/Destroyed`, `DebuggerStateChange`.

## Примечания совместимости
- Сигнатуры методов в OTAPI могут отличаться по версиям RAD Studio — при ошибках компиляции сверяйте `ToolsAPI.pas` вашей версии.
- Если добавление кнопки в тулбар не удалось, можно отключить его и оставить только логику отладки.