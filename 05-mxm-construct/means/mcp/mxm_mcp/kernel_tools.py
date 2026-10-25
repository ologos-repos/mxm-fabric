"""The kernel's model-facing tools (ADR-MXK-0002).

Only the Assistant's side of the kernel is exposed: the constitution posture and the
Assistant entrypoint. Operator and Advisor acts are never registered as tools, so no
engine can reach them through MCP, whatever it sends.
"""
from __future__ import annotations

from dataclasses import asdict

from .delegation import Delegation
from .server import Server, ToolRefused

PROPOSE_SCHEMA = {
    "type": "object",
    "properties": {
        "unit_id": {"type": "string", "description": "The WorkUnit this proposal is for."},
        "proposal": {"type": "object", "description": "Action fields, e.g. {\"type\": \"tool\", \"tool\": \"echo\", \"args\": {...}}. Any actor field is ignored."},
    },
    "required": ["unit_id", "proposal"],
}


def bind(server: Server, kernel) -> Server:
    def posture(args: dict, delegation: Delegation):
        return {"posture": kernel.render_posture(), "pin": kernel.constitution.pin()}

    def propose(args: dict, delegation: Delegation):
        unit_id, proposal = args.get("unit_id"), args.get("proposal")
        if not isinstance(unit_id, str) or not isinstance(proposal, dict):
            raise ToolRefused("unit_id (string) and proposal (object) are required")
        if not delegation.permits_unit(unit_id):
            raise ToolRefused(f"unit '{unit_id}' is outside delegation {delegation.id}")
        try:
            decision = kernel.assistant_propose(unit_id, proposal)
        except TypeError as exc:  # unknown Action fields
            raise ToolRefused(f"malformed proposal: {exc}") from None
        return asdict(decision)

    server.tool("mxm_posture", "The pinned MxM constitution (Mind, Mission, Morals) you operate under.",
                {"type": "object", "properties": {}}, posture)
    server.tool("mxm_propose", "Propose an action to the MxM kernel as the Assistant. The kernel decides; "
                "Operator and Advisor acts are not available here.", PROPOSE_SCHEMA, propose)
    return server
