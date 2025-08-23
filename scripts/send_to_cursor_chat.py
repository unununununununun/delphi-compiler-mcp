#!/usr/bin/env python
"""Send MCP command to Cursor chat for AI execution."""

import sys
import time
import argparse
import subprocess
import os

def send_command_via_cursor_cli(command: str):
    """Try to send command using Cursor CLI if available."""
    try:
        # Попытка использовать Cursor CLI API (если есть)
        subprocess.run(["cursor", "chat", "send", command], check=True)
        return True
    except:
        return False

def send_command_via_keyboard():
    """Send command using keyboard automation."""
    try:
        import pyautogui
        
        # Открыть Cursor чат (Cmd+K on Mac, Ctrl+K on Windows/Linux)
        if sys.platform == "darwin":
            pyautogui.hotkey('cmd', 'k')
        else:
            pyautogui.hotkey('ctrl', 'k')
        
        time.sleep(0.5)
        
        # Ввести команду
        pyautogui.typewrite("@delphi-compiler compile")
        
        # Отправить
        pyautogui.press('enter')
        
        return True
    except ImportError:
        print("pyautogui not installed. Run: pip install pyautogui")
        return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--command', default='compile', choices=['compile', 'build'])
    parser.add_argument('--platform', default='Win32')
    parser.add_argument('--config', default='Debug')
    
    args = parser.parse_args()
    
    # Формируем MCP команду
    if args.command == 'compile':
        mcp_command = f"@delphi-compiler compile --platform {args.platform} --config {args.config}"
    else:
        mcp_command = f"@delphi-compiler build --platform {args.platform}"
    
    print(f"Sending to Cursor chat: {mcp_command}")
    
    # Пробуем разные способы отправки
    if not send_command_via_cursor_cli(mcp_command):
        if not send_command_via_keyboard():
            print("Failed to send command to Cursor chat")
            print("Please make sure Cursor is open and focused")
            return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())