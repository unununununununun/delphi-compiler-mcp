# Setup & Troubleshooting

## Установка плагина
1. Откройте `rad_plugin/DelphiMcpDebugger.dproj` (Win32, Design-time).
2. Убедитесь, что подключены пакеты: `rtl`, `vcl`, `vclimg`, `vclactnband`, `designide`, `IndyCore`, `IndySystem`, `IndyProtocols`.
3. Соберите и установите пакет.

Переменные окружения для IDE (опционально):
- `RAD_PLUGIN_PORT` (по умолчанию 5645)
- `RAD_PLUGIN_TOKEN`

## Настройка MCP сервера
- Установите Python пакет, добавьте в `.cursor/mcp.json` как в SERVER.md.

## Частые проблемы
- AV в `delphicoreide*.bpl` при сборке:
  - Проверьте, что пакет — design‑time, инициализация TCP/GUI отложена (в нашем коде используется `TThread.ForceQueue`).
  - Убедитесь, что нет старых BPL/DCP, удалите их из OutputDir и из путей IDE.
  - Пересоберите Indy пакеты под текущую версию IDE, если нужны кастомные сборки.
- Не собирается `AddSourceBreakpoint`:
  - Проверьте сигнатуру в вашей `ToolsAPI.pas` и подберите корректную перегрузку/аргументы.
- Кнопка‑индикатор не появляется:
  - IDE могла не иметь `TActionToolBar` на главной форме; это не критично. Логика отладки работает без кнопки.