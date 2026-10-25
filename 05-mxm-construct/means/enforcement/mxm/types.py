from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Optional


CHAIN = (
    "package",
    "unit",
    "run",
    "evidence",
    "acceptance",
    "integration",
    "disposition",
)

PRIVILEGED_EFFECTS = frozenset({"send", "deploy", "public", "pay", "constitution_write"})

DURABLE_MEMORY = frozenset({"decision", "acceptance", "method"})


@dataclass
class Action:
    type: str
    actor: str = "assistant"
    tool: Optional[str] = None
    effect: Optional[str] = None
    args: dict[str, Any] = field(default_factory=dict)
    channel: Optional[str] = None
    env: Optional[str] = None
    target: Optional[str] = None
    to: Optional[str] = None
    operator_ok: bool = False
    memory_kind: Optional[str] = None
    note: Optional[str] = None
    method_id: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Decision:
    kind: str
    reason: str = ""
    payload: Any = None
    unit_id: Optional[str] = None
    state: Optional[str] = None

    @property
    def ok(self) -> bool:
        return self.kind in {"allow", "advanced", "accepted", "challenged", "waived", "opened", "cleared"}


@dataclass
class Challenge:
    note: str
    ts: str
    actor: str = "advisor"


@dataclass
class Acceptance:
    ts: str
    actor: str
    pin: str


@dataclass
class WorkUnit:
    id: str
    package_id: str
    pin: str
    scope: str
    state: str = "package"
    advisor_challenge: Optional[Challenge] = None
    challenge_waived: bool = False
    acceptance: Optional[Acceptance] = None
    method_id: Optional[str] = None
    ad_hoc: bool = False
    unit_type: str = "generic"
    spec_version: str = "0.1"
    constitution_version: str = ""
