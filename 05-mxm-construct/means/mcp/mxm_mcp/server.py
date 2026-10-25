"""Minimal MCP server over stdio: newline-delimited JSON-RPC 2.0 (ADR-MXK-0002).

Implements what an engine needs to discover and call tools: `initialize`,
`notifications/initialized`, `ping`, `tools/list` and `tools/call`. Everything else is
answered with JSON-RPC "method not found". Every `tools/call` is checked against the
server's delegation before the handler runs; a server without a delegation refuses all
tool calls.
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from typing import Any, Callable, TextIO

from .delegation import Delegation

SUPPORTED_PROTOCOLS = ("2025-06-18", "2025-03-26", "2024-11-05")
PARSE_ERROR, INVALID_REQUEST, METHOD_NOT_FOUND, INVALID_PARAMS = -32700, -32600, -32601, -32602


@dataclass
class Tool:
    name: str
    description: str
    input_schema: dict
    handler: Callable[[dict, Delegation], Any]


class ToolRefused(Exception):
    """A tool call the delegation or the kernel refuses; reported to the caller as isError."""


class Server:
    def __init__(self, name: str, version: str, delegation: Delegation | None):
        self.name, self.version, self.delegation = name, version, delegation
        self.tools: dict[str, Tool] = {}

    def tool(self, name: str, description: str, input_schema: dict, handler) -> None:
        self.tools[name] = Tool(name, description, input_schema, handler)

    # --- protocol ---

    def handle(self, message: dict) -> dict | None:
        """Return the response for one message, or None for a notification."""
        if not isinstance(message, dict) or message.get("jsonrpc") != "2.0" or "method" not in message:
            return self._error(message.get("id") if isinstance(message, dict) else None, INVALID_REQUEST, "invalid request")
        method, params, mid = message["method"], message.get("params") or {}, message.get("id")
        if mid is None:  # notification: never answered
            return None
        if method == "initialize":
            asked = params.get("protocolVersion")
            version = asked if asked in SUPPORTED_PROTOCOLS else SUPPORTED_PROTOCOLS[0]
            return self._result(mid, {"protocolVersion": version, "capabilities": {"tools": {}},
                                      "serverInfo": {"name": self.name, "version": self.version}})
        if method == "ping":
            return self._result(mid, {})
        if method == "tools/list":
            visible = [t for t in self.tools.values()
                       if self.delegation is not None and self.delegation.permits_tool(t.name)]
            return self._result(mid, {"tools": [{"name": t.name, "description": t.description,
                                                 "inputSchema": t.input_schema} for t in visible]})
        if method == "tools/call":
            return self._call(mid, params)
        return self._error(mid, METHOD_NOT_FOUND, f"method not found: {method}")

    def _call(self, mid, params: dict) -> dict:
        name, args = params.get("name"), params.get("arguments") or {}
        if not isinstance(args, dict):
            return self._error(mid, INVALID_PARAMS, "arguments must be an object")
        if self.delegation is None:
            return self._tool_result(mid, {"refused": "no delegation context"}, error=True)
        if name not in self.tools:
            return self._error(mid, INVALID_PARAMS, f"unknown tool: {name}")
        if not self.delegation.permits_tool(name):
            return self._tool_result(mid, {"refused": f"tool '{name}' is outside delegation {self.delegation.id}"}, error=True)
        try:
            return self._tool_result(mid, self.tools[name].handler(args, self.delegation))
        except ToolRefused as exc:
            return self._tool_result(mid, {"refused": str(exc)}, error=True)

    @staticmethod
    def _tool_result(mid, payload, error=False) -> dict:
        return {"jsonrpc": "2.0", "id": mid, "result": {
            "content": [{"type": "text", "text": json.dumps(payload, default=str, sort_keys=True)}],
            "isError": error}}

    @staticmethod
    def _result(mid, result) -> dict:
        return {"jsonrpc": "2.0", "id": mid, "result": result}

    @staticmethod
    def _error(mid, code, message) -> dict:
        return {"jsonrpc": "2.0", "id": mid, "error": {"code": code, "message": message}}

    # --- transport ---

    def serve(self, reader: TextIO = sys.stdin, writer: TextIO = sys.stdout) -> None:
        for line in reader:
            line = line.strip()
            if not line:
                continue
            try:
                message = json.loads(line)
            except ValueError:
                response = self._error(None, PARSE_ERROR, "parse error")
            else:
                response = self.handle(message)
            if response is not None:
                writer.write(json.dumps(response) + "\n")
                writer.flush()
