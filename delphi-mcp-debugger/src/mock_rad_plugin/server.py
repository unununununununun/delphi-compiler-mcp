from __future__ import annotations

import asyncio
import json
import random
import time
from typing import Any


class MockRadPluginServer:
    def __init__(self, host: str = "127.0.0.1", port: int = 5645, token: str | None = None) -> None:
        self._host = host
        self._port = port
        self._token = token

    async def start(self) -> None:
        server = await asyncio.start_server(self._handle_client, self._host, self._port)
        async with server:
            await server.serve_forever()

    async def _handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        authed = self._token is None
        while True:
            line = await reader.readline()
            if not line:
                break
            try:
                msg = json.loads(line.decode("utf-8", errors="ignore"))
            except Exception:
                continue
            if msg.get("method") == "auth/handshake":
                authed = (self._token is None) or (msg.get("params", {}).get("token") == self._token)
                continue
            if not authed:
                await self._send(writer, {"jsonrpc": "2.0", "id": msg.get("id"), "error": {"code": 401, "message": "unauthorized"}})
                continue
            method = msg.get("method")
            params = msg.get("params", {})
            if method == "debug/run":
                await self._send(writer, {"jsonrpc": "2.0", "id": msg.get("id"), "result": {"status": "running"}})
                await self._notify(writer, "debug/output", {"category": "stdout", "text": "Program started\n"})
                # Simulate breakpoint stop
                await asyncio.sleep(0.1)
                await self._notify(writer, "debug/stopped", {"reason": "breakpoint", "threadId": 1})
            elif method == "debug/continue":
                await self._send(writer, {"jsonrpc": "2.0", "id": msg.get("id"), "result": {"status": "continued"}})
                await self._notify(writer, "debug/output", {"category": "stdout", "text": "Continued\n"})
            elif method == "debug/stepOver":
                await self._send(writer, {"jsonrpc": "2.0", "id": msg.get("id"), "result": {"status": "stepped"}})
                await self._notify(writer, "debug/output", {"category": "stdout", "text": "StepOver\n"})
            elif method == "debug/setBreakpoint":
                fid = f"bp-{random.randint(1000,9999)}"
                await self._send(writer, {"jsonrpc": "2.0", "id": msg.get("id"), "result": {"id": fid, "file": params.get("file"), "line": params.get("line")}})
            elif method == "debug/removeBreakpoint":
                await self._send(writer, {"jsonrpc": "2.0", "id": msg.get("id"), "result": {"removed": True}})
            else:
                await self._send(writer, {"jsonrpc": "2.0", "id": msg.get("id"), "error": {"code": -32601, "message": "Method not found"}})

    async def _send(self, writer: asyncio.StreamWriter, payload: dict[str, Any]) -> None:
        writer.write((json.dumps(payload) + "\n").encode("utf-8"))
        await writer.drain()

    async def _notify(self, writer: asyncio.StreamWriter, method: str, params: dict[str, Any]) -> None:
        await self._send(writer, {"jsonrpc": "2.0", "method": method, "params": params})


async def main() -> None:
    server = MockRadPluginServer()
    await server.start()


if __name__ == "__main__":
    asyncio.run(main())

