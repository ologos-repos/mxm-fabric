"""Delegation: the authority context every MCP call is bound to (ADR-MXK-0002).

Authority flows down. A child delegation is derived from its parent and may only narrow:
fewer tools, fewer units, never more. The server refuses every tool call made without a
delegation, and every call outside the delegation's tools or units.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


class DelegationError(PermissionError):
    pass


@dataclass(frozen=True)
class Delegation:
    id: str
    tools: frozenset[str]
    units: frozenset[str] = field(default_factory=frozenset)
    parent: str | None = None
    any_unit: bool = False

    def permits_tool(self, name: str) -> bool:
        return name in self.tools

    def permits_unit(self, unit_id: str) -> bool:
        return self.any_unit or unit_id in self.units

    def narrow(self, child_id: str, tools=None, units=None) -> "Delegation":
        """Derive a child. Asking for anything the parent does not hold is refused."""
        tools = frozenset(self.tools if tools is None else tools)
        if not tools <= self.tools:
            raise DelegationError(f"child asks for tools the parent does not hold: {sorted(tools - self.tools)}")
        if units is None:
            return Delegation(child_id, tools, self.units, self.id, self.any_unit)
        units = frozenset(units)
        if not self.any_unit and not units <= self.units:
            raise DelegationError(f"child asks for units the parent does not hold: {sorted(units - self.units)}")
        return Delegation(child_id, tools, units, self.id, False)

    @classmethod
    def load(cls, path: str | Path) -> "Delegation":
        d = json.loads(Path(path).read_text())
        if not d.get("id") or not isinstance(d.get("tools"), list):
            raise DelegationError("delegation needs an id and a tools list")
        return cls(d["id"], frozenset(d["tools"]), frozenset(d.get("units", [])),
                   d.get("parent"), bool(d.get("any_unit", False)))
