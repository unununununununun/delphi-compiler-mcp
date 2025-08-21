"""Delphi MCP Server for Cursor IDE.

A Model Context Protocol (MCP) server that enables compilation of Delphi/Object Pascal 
projects within Cursor IDE, providing seamless integration with RAD Studio compilers.
"""

__version__ = "1.0.0"
__author__ = "Delphi MCP Team"
__email__ = "support@delphi-mcp.dev"

from .server import DelphiMCPServer
from .main import main

__all__ = ["DelphiMCPServer", "main"]
