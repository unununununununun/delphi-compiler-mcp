import argparse
import sys
from pathlib import Path

from .server import DebuggerMCPServer


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Delphi MCP Debugger (MVP)",
    )
    parser.add_argument("--transport", choices=["stdio", "http"], default="stdio")
    parser.add_argument("--host", default=None, help="RAD plugin host (override env)")
    parser.add_argument("--port", type=int, default=None, help="RAD plugin port (override env)")
    parser.add_argument("--token", default=None, help="Shared secret for plugin")
    parser.add_argument("--http-host", default="127.0.0.1")
    parser.add_argument("--http-port", type=int, default=8090)
    parser.add_argument("--debug", action="store_true")

    args = parser.parse_args()

    server = DebuggerMCPServer(
        plugin_host=args.host,
        plugin_port=args.port,
        plugin_token=args.token,
        debug=args.debug,
    )
    if args.transport == "stdio":
        server.run_stdio()
    else:
        server.run_http(host=args.http_host, port=args.http_port)


if __name__ == "__main__":
    main()

