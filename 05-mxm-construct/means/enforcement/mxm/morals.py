from __future__ import annotations

from typing import Any

from .types import Action, PRIVILEGED_EFFECTS


def effect_of(action: Action) -> str | None:
    if action.effect:
        return action.effect
    if action.type == "memory_write":
        return "memory_write"
    if action.tool:
        return action.tool
    return action.type


def _field(action: Action, key: str) -> Any:
    return {
        "tool": action.tool,
        "effect": effect_of(action),
        "channel": action.channel,
        "env": action.env,
        "target": action.target,
        "actor": action.actor,
        "type": action.type,
        "memory_kind": action.memory_kind,
    }.get(key)


def rule_hits(rule: dict[str, Any], action: Action) -> bool:
    """A rule hits when every listed constraint matches the action."""
    constraints = dict(rule)
    rule_effect = constraints.pop("effect", None)
    if rule_effect is not None:
        actual = effect_of(action)
        if actual != rule_effect and action.tool != rule_effect:
            return False
    for key, expected in constraints.items():
        actual = _field(action, key)
        if isinstance(expected, list):
            if actual not in expected:
                return False
        elif actual != expected:
            return False
    return True


def check(morals: dict, action: Action) -> str:
    """Return DENY | CONFIRM | ALLOW. Operator is not exempt from hard stops
    except when operator_ok is set on a soft stop or on a privileged grant.
    Hard stops always deny, including for the operator — publish a new
    constitution instead of punching through a hard stop.
    """
    hard = morals.get("hard_stops") or []
    soft = morals.get("soft_stops") or []
    scope = morals.get("trust_scope") or {}
    tools = list(scope.get("tools") or [])
    identities = list(scope.get("identities") or ["assistant", "advisor"])
    if "operator" not in identities:
        identities.append("operator")

    for rule in hard:
        if rule_hits(rule, action):
            return "DENY"

    if action.actor not in identities:
        return "DENY"

    if action.type == "tool" and action.tool and tools and action.tool not in tools:
        if action.actor != "operator":
            return "DENY"

    for rule in soft:
        if rule_hits(rule, action):
            return "ALLOW" if action.operator_ok and action.actor == "operator" else "CONFIRM"

    if effect_of(action) in PRIVILEGED_EFFECTS and not (
        action.operator_ok and action.actor == "operator"
    ):
        return "DENY"

    return "ALLOW"
