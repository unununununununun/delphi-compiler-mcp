#!/usr/bin/env python
"""Send build command to Cursor chat."""

import sys
import subprocess
import pyautogui
import time
import argparse

def send_to_cursor_chat(command: str):
    """Send command to Cursor chat using keyboard automation."""
    # Активировать окно Cursor
    # Фокус на чат (Ctrl+L обычно фокусирует на чат в Cursor)
    pyautogui.hotkey('ctrl', 'l')
    time.sleep(0.2)
    
    # Очистить поле ввода
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.1)
    
    # Ввести команду
    pyautogui.typewrite(command)
    time.sleep(0.1)
    
    # Отправить (Enter)
    pyautogui.press('enter')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--command', default='compile', choices=['compile', 'build'])
    parser.add_argument('--platform', default='Win32')
    parser.add_argument('--config', default='Debug')
    
    args = parser.parse_args()
    
    # Формируем команду для чата
    if args.command == 'compile':
        chat_command = f"@delphi-compiler compile --platform {args.platform} --config {args.config}"
    else:
        chat_command = f"@delphi-compiler build --platform {args.platform}"
    
    # Отправляем в чат
    send_to_cursor_chat(chat_command)

if __name__ == "__main__":
    main()