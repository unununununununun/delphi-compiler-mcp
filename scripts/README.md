# Build Scripts for Delphi MCP

This folder contains helper scripts for integrating MCP build commands with VS Code/Cursor.

## Scripts

### mcp_build_client.py
- Calls MCP server commands directly
- Output goes to terminal
- Used by Shift+F9 and Ctrl+Shift+F9 shortcuts

### send_to_cursor_chat.py
- Sends MCP commands to Cursor chat
- AI agent executes the command and shows output in chat
- Used by F9 and Ctrl+F9 shortcuts

## Usage

These scripts are called automatically by VS Code tasks when you use keyboard shortcuts:
- **F9** - Send compile command to Cursor chat
- **Ctrl+F9** - Send build command to Cursor chat
- **Shift+F9** - Run compile in terminal
- **Ctrl+Shift+F9** - Run build in terminal

## Requirements

For chat integration:
```bash
pip install pyautogui
```

For MCP client:
```bash
pip install mcp
```