@echo off
REM uninstall_mcp_server.bat - Uninstall delphi_mcp_server package
REM Usage:
REM   uninstall_mcp_server.bat

setlocal

echo Uninstalling delphi-compiler-mcp ...

python -m pip uninstall -y delphi-compiler-mcp

if %ERRORLEVEL% NEQ 0 (
    echo Uninstallation encountered errors. Review messages above.
    exit /b %ERRORLEVEL%
)

echo.
echo Uninstallation completed.
echo If you need to remove cached wheels, run "pip cache purge" manually.
echo.

endlocal
