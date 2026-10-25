"""Test support: a kernel whose trust registry holds a test Operator key and a test Advisor
key, and helpers that sign each Operator or Advisor act the way their own surfaces would.
The keys are fixed test values, never for use outside the suites."""
from __future__ import annotations

import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mxm.authz import Signer, Trust, act_of  # noqa: E402
from mxm.constitution import Constitution  # noqa: E402
from mxm.kernel import Kernel  # noqa: E402
from mxm.types import Action  # noqa: E402

CONST = ROOT / "constitutions" / "default.json"
OPERATOR = Signer("op-test", "operator", bytes(range(32)))
ADVISOR = Signer("adv-test", "advisor", bytes(range(32, 64)))


def make_trust(*extra: dict, operator: str = "operator-under-test", advisor: str = "advisor-under-test") -> Trust:
    return Trust.from_entries([OPERATOR.trust_entry(operator), ADVISOR.trust_entry(advisor), *extra])


class Harness:
    def __init__(self, root, const=CONST, anchor=None, trust=None, tools=None):
        self.root, self.const, self.anchor = Path(root), const, anchor
        self.trust = trust if trust is not None else make_trust()
        self.k = Kernel(Constitution.load(const), root, tools=tools, trust=self.trust, anchor_path=anchor)

    def restart(self) -> "Harness":
        """A second kernel on the same log: a restart, or another process."""
        return Harness(self.root, self.const, self.anchor, self.trust)

    def pin(self, unit_id):
        unit = self.k.units.get(unit_id) if unit_id else None
        return unit.pin if unit else self.k.constitution.pin()

    def sign(self, signer: Signer, unit_id, action, **kw) -> dict:
        act = action if isinstance(action, dict) else act_of(action)
        return signer.authorize(unit_id, act, self.pin(unit_id), **kw)

    def open(self, package_id: str = "pkg", **kw) -> str:
        unit_id = uuid.uuid4().hex
        auth = OPERATOR.authorize(unit_id, self.k.opening_act(package_id, **kw), self.k.constitution.pin())
        decision = self.k.open_package(package_id, auth, **kw)
        assert decision.kind == "opened", decision
        return unit_id

    def op(self, unit_id, action: Action):
        return self.k.operator_propose(unit_id, action, self.sign(OPERATOR, unit_id, action))

    def adv(self, unit_id, action: Action):
        return self.k.advisor_propose(unit_id, action, self.sign(ADVISOR, unit_id, action))

    def assist(self, unit_id, **proposal):
        return self.k.assistant_propose(unit_id, proposal)

    def accept(self, unit_id):
        return self.op(unit_id, Action(type="accept", operator_ok=True))

    def waive(self, unit_id, note):
        return self.op(unit_id, Action(type="waive_challenge", operator_ok=True, note=note))

    def abort(self, unit_id):
        return self.op(unit_id, Action(type="abort", operator_ok=True))

    def challenge(self, unit_id, note):
        return self.adv(unit_id, Action(type="challenge", note=note))

    def clear_challenge(self, unit_id):
        return self.adv(unit_id, Action(type="clear_challenge"))

    def clear_halt(self):
        return self.k.clear_halt(OPERATOR.authorize(None, act_of(Action(type="clear_halt")), None))

    def unit(self, unit_id):
        return self.k.units[unit_id]

    def at_unit(self, package_id: str = "probe", **kw) -> str:
        unit_id = self.open(package_id, **kw)
        self.op(unit_id, Action(type="advance", to="unit"))
        return unit_id

    def at_evidence(self, package_id: str = "probe", **kw) -> str:
        unit_id = self.at_unit(package_id, **kw)
        self.assist(unit_id, type="tool", tool="echo", args={"text": "x"})
        self.assist(unit_id, type="advance", to="evidence")
        return unit_id
