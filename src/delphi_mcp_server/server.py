"""Delphi MCP Server implementation."""

from __future__ import annotations

import asyncio
import os
import subprocess
from pathlib import Path
from typing import Any
import datetime
import logging
import xml.etree.ElementTree as ET

from mcp.server.fastmcp import FastMCP


class DelphiMCPServer:
    """Delphi MCP Server for compiling Delphi/Object Pascal projects."""
    
    def __init__(
        self, 
        delphi_path: Path | None = None,
        log_file: Path | None = None,
        debug: bool = False
    ):
        """Initialize the Delphi MCP Server.
        
        Args:
            delphi_path: Path to Delphi installation (overrides DELPHI_PATH env var)
            log_file: Path to log file (default: current directory/last_build.log)
            debug: Enable debug logging
        """
        self.mcp = FastMCP("delphi-compiler")
        
        # Setup logging
        self.log_file = log_file or Path.cwd() / "last_build.log"
        log_level = logging.DEBUG if debug else logging.INFO
        logging.basicConfig(
            filename=self.log_file, 
            level=log_level, 
            format="%(asctime)s %(levelname)s %(message)s"
        )
        
        # Set Delphi path if provided
        if delphi_path:
            os.environ["DELPHI_PATH"] = str(delphi_path)
            
        # Register tools
        self._register_tools()
    
    def _register_tools(self) -> None:
        """Register MCP tools."""
        
        @self.mcp.tool()
        async def compile(
            project: str | None = None,
        ) -> str:
            """Compile Delphi project (.dpr or .dproj) in Debug configuration.

            Args:
                project: Path to project file. If omitted, searches current directory.

            Returns:
                Compilation result with error/warning summary.
            """
            return await self._compile_project(project, debug_build=True)

        @self.mcp.tool()
        async def build(
            project: str | None = None,
        ) -> str:
            """Build project in Release configuration (alias for compile with Release config).

            Args:
                project: Path to project file. If omitted, searches current directory.

            Returns:
                Build result with error/warning summary.
            """
            # Pass only Release config; platform resolved automatically
            return await self._compile_project(project, debug_build=False)

    def find_delphi_compiler(self, platform: str) -> str | None:
        """Find Delphi compiler executable for the specified platform."""
        exe = "dcc32.exe" if platform.lower() == "win32" else "dcc64.exe"
        root = os.environ.get("DELPHI_PATH")
        if root:
            root_path = Path(root)
            # If pointing directly to bin directory
            candidates = [root_path, root_path / "bin"] if root_path.name.lower() != "bin" else [root_path]
            for base in candidates:
                cand = base / exe
                if cand.exists():
                    return str(cand)
        # Fallback to PATH
        for p in os.environ.get("PATH", "").split(os.pathsep):
            cand = Path(p) / exe
            if cand.exists():
                return str(cand)
        return None

    def find_msbuild(self) -> str | None:
        """Locate MSBuild.exe next to dcc32.exe/dcc64.exe or in PATH."""
        # Try RAD Studio bin
        for plat in ("Win32", "Win64"):
            comp = self.find_delphi_compiler(plat)
            if comp:
                cand = Path(comp).with_name("msbuild.exe")
                if cand.exists():
                    return str(cand)
        # Fallback PATH
        for p in os.environ.get("PATH", "").split(os.pathsep):
            cand = Path(p) / "msbuild.exe"
            if cand.exists():
                return str(cand)
        return None

    def find_rsvars(self) -> str | None:
        """Locate rsvars.bat using DELPHI_PATH or compiler location."""
        # First, DELPHI_PATH
        root = os.environ.get("DELPHI_PATH")
        if root:
            cand = Path(root) / "bin" / "rsvars.bat"
            if cand.exists():
                return str(cand)
        # Next, same dir where dcc32 was found
        comp = self.find_delphi_compiler("Win32") or self.find_delphi_compiler("Win64")
        if comp:
            cand = Path(comp).with_name("rsvars.bat")
            if cand.exists():
                return str(cand)
        return None

    def discover_project(self) -> Path | None:
        """Find first .dproj or .dpr file in current directory."""
        for ext in ("*.dproj", "*.dpr"):
            matches = list(Path.cwd().rglob(ext))
            if matches:
                return matches[0]
        return None

    async def run_subprocess(self, cmd: list[str]) -> tuple[int, str]:
        """Run subprocess and return exit code and output."""
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        stdout_bytes, _ = await proc.communicate()
        output = stdout_bytes.decode('utf-8', errors='ignore')
        return proc.returncode, output

    def extract_output_dirs(self, dproj_path: Path, platform: str, config: str) -> tuple[str | None, str | None]:
        """Parse .dproj and return (exe_output, dcu_output) for given platform and config."""
        tree = ET.parse(dproj_path)
        root = tree.getroot()
        ns = {'msb': 'http://schemas.microsoft.com/developer/msbuild/2003'}
        exe_output = None
        dcu_output = None
        # Search PropertyGroup with matching conditions
        for pg in root.findall('msb:PropertyGroup', ns):
            cond = pg.attrib.get('Condition', '')
            if platform.lower() in cond.lower() and config.lower() in cond.lower():
                eo = pg.find('msb:DCC_ExeOutput', ns)
                du = pg.find('msb:DCC_DcuOutput', ns)
                if eo is not None and eo.text:
                    exe_output = eo.text
                if du is not None and du.text:
                    dcu_output = du.text
        # Fallback: search without platform/config conditions
        if not exe_output or not dcu_output:
            for pg in root.findall('msb:PropertyGroup', ns):
                eo = pg.find('msb:DCC_ExeOutput', ns)
                du = pg.find('msb:DCC_DcuOutput', ns)
                if not exe_output and eo is not None and eo.text:
                    exe_output = eo.text
                if not dcu_output and du is not None and du.text:
                    dcu_output = du.text
        return exe_output, dcu_output

    async def _compile_project(
        self,
        project: str | None = None,
        *,
        debug_build: bool = True,
    ) -> str:
        """Internal method to compile Delphi project."""
        # Auto-discover project if not provided
        if not project:
            discovered = self.discover_project()
            if not discovered:
                return "ERROR: No Delphi project (.dpr/.dproj) found in current directory"
            project = str(discovered)
            
        proj_path = Path(project)
        if not proj_path.exists():
            return f"ERROR: Project file not found: {project}"

        platform = "Win32"  # default compiler
        config = "Debug" if debug_build else "Release"

        if proj_path.suffix.lower() == ".dproj":
            rsvars = self.find_rsvars()
            if not rsvars:
                return "ERROR: rsvars.bat not found (check DELPHI_PATH)"
            # Build command without embedded quotes
            cmd = [
                "cmd", "/c",
                "call", rsvars, "&&",
                "msbuild.exe", str(proj_path), "/t:Build"
            ]
        else:
            # For .dpr, find linked .dpr file
            dpr_candidates = list(proj_path.parent.glob("*.dpr"))
            if not dpr_candidates:
                return f"ERROR: No .dpr file found next to {proj_path.name}"
            dpr_file = dpr_candidates[0]
            # Choose compiler by platform
            compiler = self.find_delphi_compiler(platform)
            if not compiler:
                return f"ERROR: Delphi compiler for {platform} not found"
            cmd = [compiler, str(dpr_file)]
            cmd.append("-DRELEASE" if not debug_build else "-DDEBUG")

        exit_code, output = await self.run_subprocess(cmd)
        logging.info("Run %s", " ".join(cmd))
        logging.info(output)

        # Build summary
        errors = [l for l in output.splitlines() if " error " in l.lower() or l.lower().startswith("error")]
        warns  = [l for l in output.splitlines() if " warning " in l.lower()]
        if exit_code == 0:
            return f"Build OK. Warnings: {len(warns)}. Full log: {self.log_file}"
        else:
            preview = "\n".join(errors[:5])
            return f"Build FAILED (exit {exit_code}). Errors: {len(errors)}.\n{preview}\nFull log: {self.log_file}"

    def run_stdio(self) -> None:
        """Run server with stdio transport."""
        self.mcp.run(transport="stdio")
        
    def run_http(self, host: str = "localhost", port: int = 8080) -> None:
        """Run server with HTTP transport."""
        self.mcp.run(transport="http", host=host, port=port)
