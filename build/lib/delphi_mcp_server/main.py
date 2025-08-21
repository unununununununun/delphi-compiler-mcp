"""Main entry point for the Delphi MCP Server."""

import argparse
import sys
from pathlib import Path

from .server import DelphiMCPServer


def main() -> None:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Delphi MCP Server for Cursor IDE",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Start server with stdio transport
  %(prog)s --port 8080        # Start server with HTTP transport on port 8080
  %(prog)s --version          # Show version information
        """,
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0",
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "http"],
        default="stdio",
        help="Transport protocol to use (default: stdio)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port for HTTP transport (default: 8080)",
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="Host for HTTP transport (default: localhost)",
    )
    parser.add_argument(
        "--delphi-path",
        type=Path,
        help="Path to Delphi installation (overrides DELPHI_PATH env var)",
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        help="Path to log file (default: current directory/last_build.log)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )

    args = parser.parse_args()

    try:
        server = DelphiMCPServer(
            delphi_path=args.delphi_path,
            log_file=args.log_file,
            debug=args.debug,
        )
        
        if args.transport == "stdio":
            server.run_stdio()
        elif args.transport == "http":
            server.run_http(host=args.host, port=args.port)
            
    except KeyboardInterrupt:
        print("\nServer stopped by user", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Error starting server: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
