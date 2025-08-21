# MCP Build Integration for VS Code/Cursor

This setup allows you to run MCP compile/build commands using keyboard shortcuts or buttons in VS Code/Cursor.

## Setup

1. **Ensure MCP server is installed:**
   ```bash
   pip install -e .
   ```

2. **Configure MCP in Cursor** (if not already done):
   - Add the MCP server to your Cursor settings
   - The server name should be `delphi-compiler`

## Usage Methods

### Method 1: Keyboard Shortcuts

The following shortcuts are pre-configured:

- **F9** - Compile project in Debug mode (Win32)
- **Ctrl+F9** - Build project in Release mode (Win32)
- **Shift+F9** - Compile project in Debug mode (Win64)
- **Ctrl+Shift+F9** - Build project in Release mode (Win64)
- **Ctrl+Shift+B** - Run default build task
- **Ctrl+Shift+Alt+B** - Build Release (Win32)

### Method 2: VS Code Tasks

1. Press `Ctrl+Shift+P` to open Command Palette
2. Type "Tasks: Run Task"
3. Select one of:
   - `MCP: Compile (Debug)`
   - `MCP: Build (Release)`
   - `MCP: Compile Win64 (Debug)`
   - `MCP: Build Win64 (Release)`

### Method 3: Direct MCP Commands in Cursor

In Cursor's chat or command input, you can use:

```
@delphi-compiler compile
@delphi-compiler build
@delphi-compiler compile --platform Win64 --config Release
```

### Method 4: Command Line Scripts

Run from terminal:

```bash
# Simple compile
python mcp_build_client.py compile

# Build release
python mcp_build_client.py build

# Compile Win64 Debug
python mcp_build_client.py compile --platform Win64 --config Debug

# Build specific project
python mcp_build_client.py build --project path/to/project.dproj
```

## Customizing Shortcuts

To add or modify keyboard shortcuts:

1. Open `.vscode/keybindings.json`
2. Add new entries following the existing pattern
3. Available task names are defined in `.vscode/tasks.json`

Example:
```json
{
    "key": "alt+b",
    "command": "workbench.action.tasks.runTask",
    "args": "MCP: Build (Release)"
}
```

## Adding Build Buttons

To add build buttons to VS Code:

1. Install the "Task Buttons" extension
2. Add to `.vscode/settings.json`:

```json
{
    "TaskButtons.tasks": [
        {
            "label": "$(play) Compile",
            "task": "MCP: Compile (Debug)"
        },
        {
            "label": "$(package) Build",
            "task": "MCP: Build (Release)"
        }
    ]
}
```

## Troubleshooting

1. **MCP server not found**: Ensure the package is installed with `pip install -e .`
2. **Build fails**: Check that `DELPHI_PATH` environment variable is set
3. **No output**: Check `last_build.log` in your project directory