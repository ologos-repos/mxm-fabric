from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Callable

from .morals import check
from .types import Action


ToolFn = Callable[[dict], Any]


@dataclass
class ToolSpec:
    name: str
    fn: ToolFn
    privileged: bool = False
    scope_optional: bool = True
    allowed_actors: tuple[str, ...] = ("assistant", "operator")


class Broker:
    def __init__(self, morals: dict, tools: dict[str, ToolSpec] | None = None):
        self.morals = morals
        self.tools = tools or {}

    def register(self, spec: ToolSpec) -> None:
        self.tools[spec.name] = spec

    def decide(self, action: Action) -> tuple[str, str]:
        """Policy only: (kind, reason). Never runs the tool, never mutates the action."""
        if action.tool not in self.tools:
            return "deny", "unknown_tool"
        spec = self.tools[action.tool]
        if action.actor not in spec.allowed_actors:
            return "deny", "actor_not_permitted_for_tool"
        if spec.privileged and not action.effect:
            action = replace(action, effect="send")
        verdict = check(self.morals, action)
        if verdict == "DENY":
            return "deny", "morals.hard_stop"
        if verdict == "CONFIRM":
            return "confirm", "morals.soft_stop"
        return "allow", "ok"

    def execute(self, action: Action) -> dict:
        """Run a tool the kernel has already allowed and recorded."""
        spec = self.tools[action.tool]
        return {"tool": spec.name, "receipt": spec.fn(action.args or {})}
