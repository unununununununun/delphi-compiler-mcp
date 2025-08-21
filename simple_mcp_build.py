#!/usr/bin/env python
"""Simple script to call MCP server commands directly."""

import subprocess
import sys
import json

def call_mcp_command(command, **kwargs):
    """Call MCP command using mcp CLI."""
    # Build the command
    cmd = [
        sys.executable, "-m", "mcp", "call",
        "--server", "delphi-compiler",
        command
    ]
    
    # Add arguments
    for key, value in kwargs.items():
        if value is not None:
            cmd.extend(["--arg", f"{key}={value}"])
    
    # Execute
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    
    print(result.stdout)
    return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Simple MCP build caller")
    parser.add_argument("command", choices=["compile", "build"])
    parser.add_argument("--project", help="Project file path")
    parser.add_argument("--platform", choices=["Win32", "Win64"], default="Win32")
    parser.add_argument("--config", choices=["Debug", "Release"])
    
    args = parser.parse_args()
    
    # Build kwargs
    kwargs = {}
    if args.project:
        kwargs["project"] = args.project
    if args.platform:
        kwargs["platform"] = args.platform
    if args.command == "compile" and args.config:
        kwargs["config"] = args.config
    
    # Call the command
    success = call_mcp_command(args.command, **kwargs)
    sys.exit(0 if success else 1)