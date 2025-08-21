@echo off
REM install_mcp_server.bat - Install delphi_mcp_server package
REM Usage:
REM   install_mcp_server.bat [package_path]
REM If package_path is omitted, installs the package located in this folder.

setlocal

:: Determine source path
set "PKG_PATH=%~1"
if "%PKG_PATH%"=="" (
    set "PKG_PATH=%~dp0."
)

echo Installing delphi_mcp_server from "%PKG_PATH%" ...

:: Ensure latest pip
python -m pip install --upgrade pip

:: Install or upgrade package and its dependencies
python -m pip install --upgrade "%PKG_PATH%"

if %ERRORLEVEL% NEQ 0 (
    echo Installation failed. See messages above.
    exit /b %ERRORLEVEL%
)

echo.
echo Installation completed successfully.
echo You can now run "delphi-compiler-mcp initialize" to test the MCP server.
echo.

endlocal
