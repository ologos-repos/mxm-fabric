from __future__ import annotations

from .exceptions import BlockedByAdvisor, IllegalTransition, NeedAcceptance, NotOperator
from .types import CHAIN, Acceptance, WorkUnit


def can_advance(unit: WorkUnit, to: str, actor: str, evidence_kinds: set[str]) -> None:
    if to not in CHAIN:
        raise IllegalTransition(unit.state, to)
    if unit.state not in CHAIN:
        raise IllegalTransition(unit.state, to)
    if CHAIN.index(to) != CHAIN.index(unit.state) + 1:
        raise IllegalTransition(unit.state, to)

    if to == "run":
        return

    if to == "evidence":
        if not evidence_kinds.intersection({"receipt", "deny", "confirm", "note", "proposal"}):
            raise IllegalTransition(unit.state, to)
        return

    if to == "acceptance":
        if actor != "operator":
            raise NotOperator()
        if unit.advisor_challenge and not unit.challenge_waived:
            raise BlockedByAdvisor()
        return

    if to == "integration":
        if unit.acceptance is None:
            raise NeedAcceptance()
        return

    if to == "disposition":
        return


def apply_acceptance(unit: WorkUnit, ts: str) -> Acceptance:
    acc = Acceptance(ts=ts, actor="operator", pin=unit.pin)
    unit.acceptance = acc
    unit.state = "acceptance"
    return acc
