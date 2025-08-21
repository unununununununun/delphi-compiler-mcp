# Delphi Compiler MCP [![Donate](https://img.shields.io/badge/Donate-PayPal-blue.svg)](https://www.paypal.com/donate/?hosted_button_id=QRBTLWT63QBSN)

A lightweight Model Context Protocol (MCP) server that wraps the native Delphi (RAD Studio) compilers. It enables automatic Debug/Release builds for Win32 and Win64 projects written in Object Pascal.

## Installation

### From PyPI
```bash
pip install delphi-compiler-mcp
```

### From local source
```bash
git clone https://github.com/yourusername/delphi-compiler-mcp.git
cd delphi-compiler-mcp/production-package
pip install .
```

## MCP configuration example

Create (or update) your MCP client configuration, e.g. `.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "delphi-compiler": {
      "command": "delphi-compiler-mcp",
      "env": {
        "DELPHI_PATH": "C:\\Program Files (x86)\\Embarcadero\\Studio\\23.0"
      }
    }
  }
}
```

## Usage

### CLI
```bash
# Default compile (Debug / Win32)
mcp call delphi-compiler compile

# Release build for Win64
mcp call delphi-compiler build --platform Win64
```

### Through an AI MCP client
If your MCP client supports natural-language commands (e.g. via an AI assistant), it is enough to say:

* «build project» — to run a Release build
* «compile project» — to run a Debug compile

The client will translate the phrase into the corresponding MCP call shown above.

## License
MIT
