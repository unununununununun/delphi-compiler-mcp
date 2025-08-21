#!/usr/bin/env python
"""MCP Client for calling Delphi build/compile commands."""

import asyncio
import argparse
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def call_mcp_tool(tool_name: str, arguments: dict = None):
    """Call an MCP tool and return the result."""
    # Start the MCP server as subprocess
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "delphi_mcp_server"],
        env=None
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()
            
            # List available tools (optional, for debugging)
            tools = await session.list_tools()
            print(f"Available tools: {[t.name for t in tools.tools]}")
            
            # Call the requested tool
            result = await session.call_tool(tool_name, arguments or {})
            
            return result


async def main():
    parser = argparse.ArgumentParser(description="Call Delphi MCP build/compile commands")
    parser.add_argument(
        "command",
        choices=["compile", "build"],
        help="MCP command to execute"
    )
    parser.add_argument(
        "--project",
        help="Path to project file (.dpr or .dproj)"
    )
    parser.add_argument(
        "--platform",
        choices=["Win32", "Win64"],
        default="Win32",
        help="Target platform (default: Win32)"
    )
    parser.add_argument(
        "--config",
        choices=["Debug", "Release"],
        help="Build configuration (only for compile command)"
    )
    
    args = parser.parse_args()
    
    # Prepare arguments for MCP tool
    tool_args = {}
    if args.project:
        tool_args["project"] = args.project
    if args.platform:
        tool_args["platform"] = args.platform
    if args.command == "compile" and args.config:
        tool_args["config"] = args.config
    
    print(f"Calling MCP {args.command} with args: {tool_args}")
    print("-" * 50)
    
    try:
        result = await call_mcp_tool(args.command, tool_args)
        print(result.content[0].text if result.content else "No output")
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)