#!/usr/bin/env python
"""Quick build script for Delphi MCP Server."""

import asyncio
import sys
import argparse
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from delphi_mcp_server.server import DelphiMCPServer


async def main():
    parser = argparse.ArgumentParser(description="Build Delphi project using MCP Server")
    parser.add_argument(
        "project", 
        nargs="?", 
        help="Path to project file (.dpr or .dproj). If omitted, searches current directory."
    )
    parser.add_argument(
        "--platform", 
        "-p", 
        choices=["Win32", "Win64"], 
        default="Win32",
        help="Target platform (default: Win32)"
    )
    parser.add_argument(
        "--config", 
        "-c", 
        choices=["Debug", "Release"], 
        default="Release",
        help="Build configuration (default: Release)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    args = parser.parse_args()
    
    # Create server instance
    server = DelphiMCPServer(debug=args.debug)
    
    # Run compilation
    print(f"Building project: {args.project or 'auto-discover'}")
    print(f"Platform: {args.platform}, Config: {args.config}")
    print("-" * 50)
    
    result = await server._compile_project(
        project=args.project,
        platform=args.platform,
        config=args.config
    )
    
    print(result)
    
    # Exit with error code if build failed
    if "ERROR" in result:
        sys.exit(1)
    

if __name__ == "__main__":
    asyncio.run(main())