from __future__ import annotations

import asyncio
import json
import logging
import os
import uuid
from dataclasses import dataclass
from typing import Any, Dict, Optional

from mcp.server.fastmcp import FastMCP


@dataclass
class RpcConfig:
    host: str
    port: int
    token: Optional[str]


class JsonRpcClient:
    def __init__(self, config: RpcConfig):
        self._config = config
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._recv_task: asyncio.Task | None = None
        self._pending: Dict[str, asyncio.Future] = {}
        self._event_queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()

    @property
    def event_queue(self) -> asyncio.Queue:
        return self._event_queue

    async def connect(self) -> None:
        self._reader, self._writer = await asyncio.open_connection(
            self._config.host, self._config.port
        )
        if self._config.token:
            await self._send_notification("auth/handshake", {"token": self._config.token})
        self._recv_task = asyncio.create_task(self._recv_loop())

    async def close(self) -> None:
        if self._writer is not None:
            self._writer.close()
            try:
                await self._writer.wait_closed()
            except Exception:
                pass
        if self._recv_task is not None:
            self._recv_task.cancel()

    async def _recv_loop(self) -> None:
        assert self._reader is not None
        while True:
            line = await self._reader.readline()
            if not line:
                break
            try:
                msg = json.loads(line.decode("utf-8", errors="ignore"))
            except Exception:
                continue
            if "id" in msg and ("result" in msg or "error" in msg):
                fut = self._pending.pop(str(msg["id"]), None)
                if fut is not None and not fut.done():
                    fut.set_result(msg)
            elif "method" in msg:
                await self._event_queue.put(msg)

    async def _send(self, payload: dict[str, Any]) -> None:
        assert self._writer is not None
        data = (json.dumps(payload) + "\n").encode("utf-8")
        self._writer.write(data)
        await self._writer.drain()

    async def _send_notification(self, method: str, params: dict[str, Any] | None = None) -> None:
        await self._send({"jsonrpc": "2.0", "method": method, "params": params or {}})

    async def call(self, method: str, params: dict[str, Any] | None = None, timeout: float = 30.0) -> Any:
        msg_id = str(uuid.uuid4())
        fut: asyncio.Future = asyncio.get_event_loop().create_future()
        self._pending[msg_id] = fut
        await self._send({"jsonrpc": "2.0", "id": msg_id, "method": method, "params": params or {}})
        done = await asyncio.wait_for(fut, timeout)
        if "error" in done:
            raise RuntimeError(done["error"]) 
        return done.get("result")


class DebuggerMCPServer:
    def __init__(self, plugin_host: str | None = None, plugin_port: int | None = None, plugin_token: str | None = None, debug: bool = False) -> None:
        self.mcp = FastMCP("delphi-mcp-debugger")

        host = plugin_host or os.getenv("RAD_PLUGIN_HOST", "127.0.0.1")
        port = int(plugin_port or os.getenv("RAD_PLUGIN_PORT", "5645"))
        token = plugin_token or os.getenv("RAD_PLUGIN_TOKEN")
        self._rpc = JsonRpcClient(RpcConfig(host=host, port=port, token=token))
        self._event_task: asyncio.Task | None = None

        logging.basicConfig(level=logging.DEBUG if debug else logging.INFO)

        self._register_tools()

    def _register_tools(self) -> None:
        @self.mcp.tool()
        async def run(project: str | None = None, args: list[str] | None = None) -> str:
            await self._ensure_connected()
            result = await self._rpc.call("debug/run", {"project": project, "args": args or []})
            return json.dumps(result)

        @self.mcp.tool()
        async def cont() -> str:
            await self._ensure_connected()
            result = await self._rpc.call("debug/continue", {})
            return json.dumps(result)

        @self.mcp.tool(name="step_over")
        async def step_over() -> str:
            await self._ensure_connected()
            result = await self._rpc.call("debug/stepOver", {})
            return json.dumps(result)

        @self.mcp.tool()
        async def set_breakpoint(file: str, line: int) -> str:
            await self._ensure_connected()
            result = await self._rpc.call("debug/setBreakpoint", {"file": file, "line": line})
            return json.dumps(result)

        @self.mcp.tool()
        async def remove_breakpoint(file: str, line: int | None = None, breakpoint_id: str | None = None) -> str:
            await self._ensure_connected()
            result = await self._rpc.call("debug/removeBreakpoint", {"file": file, "line": line, "id": breakpoint_id})
            return json.dumps(result)

        @self.mcp.tool()
        async def poll_events(max_items: int = 50) -> list[dict[str, Any]]:
            await self._ensure_connected()
            items: list[dict[str, Any]] = []
            try:
                for _ in range(max_items):
                    item = self._rpc.event_queue.get_nowait()
                    items.append(item)
            except asyncio.QueueEmpty:
                pass
            return items

    async def _ensure_connected(self) -> None:
        if self._rpc._reader is None:
            await self._rpc.connect()
            if self._event_task is None:
                self._event_task = asyncio.create_task(self._event_logger())

    async def _event_logger(self) -> None:
        while True:
            evt = await self._rpc.event_queue.get()
            logging.info("debug-event: %s", evt)

    def run_stdio(self) -> None:
        self.mcp.run(transport="stdio")

    def run_http(self, host: str = "127.0.0.1", port: int = 8090) -> None:
        self.mcp.run(transport="http", host=host, port=port)

