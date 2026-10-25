"""The MxM enforcement kernel (SPEC.md): the Assistant proposes; the kernel commits.

All state lives in one hash-chained, append-only event log (mxm/eventlog.py). WorkUnits,
challenges, waivers, acceptances, halts and spent authorizations exist only as records in
it, and every kernel sharing a data root rebuilds them by replaying it (ADR-MXK-0003).
Each record passes one validation, ``_check``, before it is appended and again whenever
any kernel replays it:

- an Operator or Advisor record that has effects carries an authorization signed by a
  trusted key for that role, bound to exactly this act, unit and pin, and not spent by an
  earlier record (mxm/authz.py);
- authority-bearing effects (open, acceptance, waiver, abort, challenge, clear_halt) come
  only from the role that owns them;
- state changes are legal steps of the work chain.

A record that fails replay was not written by a conforming kernel, and halts the kernel.
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from . import authz
from . import chain as chainmod
from .authz import Trust
from .constitution import Constitution
from .eventlog import AnchorError, EventLog
from .exceptions import BlockedByAdvisor, IllegalTransition, MxmError, NeedAcceptance, NotOperator
from .means import Broker, ToolSpec
from .memory import Memory
from .methods import MethodRegistry
from .morals import check
from .types import Acceptance, Action, Challenge, Decision, DURABLE_MEMORY, WorkUnit

PRINCIPALS = ("operator", "advisor")
ACTORS = ("assistant", "operator", "advisor")
ACTION_FIELDS = frozenset(Action.__dataclass_fields__)
OPEN_FIELDS = ("package_id", "scope", "unit_type", "ad_hoc", "method_id", "constitution_version")
OPEN_ACTION_FIELDS = frozenset({"type", "actor", *OPEN_FIELDS})
OWNER = {"open": "operator", "acceptance": "operator", "waived": "operator",
         "abort": "operator", "clear_halt": "operator", "challenge": "advisor"}
# The decisions with effects that each action type may record. Any other decision is a deny
# (or a confirm, for tools and memory writes) and records no effects.
EFFECTING = {"tool": {"allow"}, "method_run": {"allow"}, "memory_write": {"allow"},
             "advance": {"advanced", "accepted"}, "accept": {"accepted"}, "abort": {"advanced"},
             "challenge": {"challenged"}, "clear_challenge": {"waived"}, "waive_challenge": {"waived"},
             "clear_halt": {"cleared"}, "open_package": {"opened"}}
EVIDENCE_KINDS = ("receipt", "memory")
EVIDENCE_OF = {"tool": "receipt", "method_run": "receipt", "memory_write": "memory"}
# The logged act's decision is the kernel's authorization of the act. For an act that owes
# evidence, exactly one closing record states what happened: done, failed, not_executed (the
# kernel knowingly skipped it), or unknown (the owning process stopped before recording it).
OUTCOMES = ("done", "failed", "not_executed", "unknown")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _deny(reason: str):
    return "deny", reason, {}, None


class InvalidRecord(Exception):
    pass


def default_tools() -> dict[str, ToolSpec]:
    def echo(args: dict) -> dict:
        return {"echo": args.get("text", "")}

    def write_draft(args: dict) -> dict:
        return {"draft": args.get("text", ""), "bytes": len(str(args.get("text", "")))}

    def search(args: dict) -> dict:
        return {"hits": [], "query": args.get("query", "")}

    def send_email(args: dict) -> dict:
        return {"sent": True, "to": args.get("to"), "subject": args.get("subject")}

    def deploy_prod(args: dict) -> dict:
        return {"deployed": True, "ref": args.get("ref")}

    return {
        "echo": ToolSpec("echo", echo, privileged=False),
        "write_draft": ToolSpec("write_draft", write_draft, privileged=False),
        "search": ToolSpec("search", search, privileged=False),
        "send_email": ToolSpec("send_email", send_email, privileged=True, allowed_actors=("operator",)),
        "deploy_prod": ToolSpec("deploy_prod", deploy_prod, privileged=True, allowed_actors=("operator",)),
    }


class Kernel:
    def __init__(
        self,
        constitution: Constitution,
        data_root: str | Path,
        tools: dict[str, ToolSpec] | None = None,
        trust: Optional[Trust] = None,
        anchor_path: str | Path | None = None,
    ):
        """``trust`` holds the Operator and Advisor public keys; without it, every Operator
        and Advisor act is denied. ``anchor_path`` holds the log's head and must live where
        the engine cannot write. Every kernel sharing ``data_root`` needs the same trust."""
        self.constitution = constitution
        self.data_root = Path(data_root)
        self.data_root.mkdir(parents=True, exist_ok=True)
        self.log = EventLog(self.data_root / "events.jsonl", anchor_path=anchor_path)
        self.memory = Memory(self.data_root / "memory")
        self.methods = MethodRegistry()
        self.broker = Broker(constitution.morals, tools or default_tools())
        self.trust = trust or Trust()
        self.attribution = constitution.morals.get("attribution", "Human-Curated, AI-Enabled")
        self.units: dict[str, WorkUnit] = {}
        self._kinds: dict[str, set[str]] = {}
        self._spent: set[str] = set()
        self._awaiting: dict[int, tuple[str, str]] = {}  # act seq -> (unit, evidence kind) it owes
        self._halts: dict[Optional[str], dict] = {}  # None: kernel scope
        self._fatal: Optional[dict] = None
        self._applied: tuple[int, Optional[str]] = (0, None)
        with self._txn():
            pass

    def render_posture(self) -> str:
        return self.constitution.render()

    def records(self, unit_id: Optional[str] = None) -> list[dict]:
        """Evidence: the log's records, optionally for one unit."""
        with self.log.locked():
            records, _, _ = self.log.scan()
        return [r for r in records if unit_id is None or r.get("unit_id") == unit_id]

    def opening_act(self, package_id: str, scope: Optional[str] = None, unit_type: str = "generic",
                    ad_hoc: bool = False) -> dict:
        """The resolved act an Operator signs to open a unit: every default is filled in here,
        so the signer sees and signs exactly the unit that will exist."""
        required = self.methods.required_for(unit_type)
        return authz.open_act(package_id, scope or self.constitution.mission.get("scope", ""), unit_type, ad_hoc,
                              required if required and not ad_hoc else None, self.constitution.version)

    # --- Transactions and replay ---

    @contextmanager
    def _txn(self):
        with self.log.locked():
            if self._fatal is None:
                self._catch_up()
            yield

    def _catch_up(self) -> None:
        try:
            records, findings, anchor = self.log.scan()
        except OSError as exc:
            return self._set_fatal("log_unreadable", str(exc))
        if findings:
            anchor_classes = {f["class"] for f in findings if f["class"].startswith("anchor_")}
            reason = anchor_classes.pop() if len(anchor_classes) == len(findings) == 1 else "evidence_tampered"
            return self._set_fatal(reason, findings)
        seq, digest = self._applied
        if seq and (len(records) < seq or records[seq - 1].get("hash") != digest):
            return self._set_fatal("evidence_rewritten", {"applied_seq": seq})
        for rec in records[seq:]:
            try:
                self._check(rec)
            except InvalidRecord as exc:
                return self._set_fatal("invalid_record", {"seq": rec.get("seq"), "detail": str(exc)})
            self._apply(rec)
        for act_seq, (unit_id, kind) in sorted(self._awaiting.items()):
            # Within one transaction an act and its evidence are written together, so an
            # obligation still open here belongs to a process that stopped in between.
            self._evidence(unit_id, kind, {"act_seq": act_seq, "outcome": "unknown"})
        if anchor is not None and records and anchor["seq"] < records[-1]["seq"]:
            # A crash between an append and its anchor write leaves the anchor behind a verified,
            # replayed log. Move it forward; if that fails, record the halt.
            try:
                self.log.write_anchor(records[-1])
            except OSError as exc:
                self._record_kernel_halt("anchor_unwritable", str(exc))

    def _set_fatal(self, reason: str, detail: Any) -> None:
        """An integrity failure stops this kernel for the rest of its process. The halt is also
        appended (once) so that it survives a restart."""
        self._fatal = {"reason": reason, "detail": detail}
        last = self.log.last()
        if last and last.get("kind") == "halt" and (last.get("payload") or {}).get("reason") == reason:
            return
        try:
            self.log.append({"kind": "halt", "unit_id": None, "actor": "kernel",
                             "payload": {"scope": "kernel", "reason": reason, "detail": detail}})
        except (OSError, ValueError):
            pass

    def _check(self, rec: dict) -> None:
        """Raise InvalidRecord unless ``rec`` is exactly a record a conforming kernel could
        append at this point of the log. Pure: never mutates state."""
        kind, uid, p = rec.get("kind"), rec.get("unit_id"), rec.get("payload")
        if kind in ("repair", "genesis"):
            return
        if not isinstance(p, dict):
            raise InvalidRecord("payload is not an object")
        if kind == "halt":
            if rec.get("actor") != "kernel" or not isinstance(p.get("reason"), str):
                raise InvalidRecord("a halt is written by the kernel and names its reason")
            if p.get("scope") == "kernel" or (p.get("scope") == "unit" and uid in self.units):
                return
            raise InvalidRecord("halt for an unknown scope or unit")
        if kind in EVIDENCE_KINDS:
            act_seq = p.get("act_seq")
            if rec.get("actor") != "kernel" or self._awaiting.get(act_seq) != (uid, kind):
                raise InvalidRecord(f"{kind} does not answer an act awaiting one")
            outcome = p.get("outcome")
            if outcome not in OUTCOMES or (outcome == "failed") != ("error" in p):
                raise InvalidRecord(f"{kind} must state one outcome, with an error exactly when it failed")
            return
        if kind != "act":
            raise InvalidRecord(f"unknown record kind {kind!r}")

        action, decision, effects = p.get("action"), p.get("decision"), p.get("effects")
        env = p.get("authorization")
        if not (isinstance(action, dict) and isinstance(decision, dict) and isinstance(effects, dict)):
            raise InvalidRecord("malformed act")
        actor, act_type, outcome = action.get("actor"), action.get("type"), decision.get("kind")
        if actor not in ACTORS or actor != rec.get("actor"):
            raise InvalidRecord("record actor is not the action's actor")
        fields = OPEN_ACTION_FIELDS if act_type == "open_package" else ACTION_FIELDS
        if set(action) - fields:
            raise InvalidRecord("action carries fields no action has")

        unit = self.units.get(uid) if uid is not None else None
        if act_type == "open_package":
            if not isinstance(uid, str) or not uid or uid in self.units:
                raise InvalidRecord("open needs a new unit id")
        elif act_type == "clear_halt":
            if uid is not None:
                raise InvalidRecord("clear_halt is kernel-scope")
        elif unit is None:
            raise InvalidRecord("act on an unknown or no unit")

        expected = self._expected_effects(unit, action, outcome, env)
        if effects != expected:
            raise InvalidRecord(f"effects {sorted(effects)} are not what a {act_type} {outcome} produces")

        if env is not None:
            if actor not in PRINCIPALS:
                raise InvalidRecord("authorization on a non-principal act")
            pin = effects["open"]["pin"] if act_type == "open_package" else (unit.pin if unit else None)
            principal, problem = authz.check(env, self.trust, role=actor, unit_id=uid, act=authz.act_of(action),
                                             pin=pin, seq=rec.get("seq", 0), consumed=self._spent)
            if problem:
                raise InvalidRecord(f"authorization {problem}")
            if p.get("principal") != principal:
                raise InvalidRecord("recorded principal is not the signing key's principal")
        elif actor in PRINCIPALS:
            # The one unsigned principal record a kernel writes: its own denial of an act whose
            # authorization failed. Anything else claiming a principal must be signed.
            if not (outcome == "deny" and decision.get("reason") == f"unverified_{actor}"
                    and isinstance(p.get("authorization_problem"), str) and p.get("principal") is None):
                raise InvalidRecord(f"an unsigned {actor} record is only an unverified denial")
        elif p.get("principal") is not None:
            raise InvalidRecord("an Assistant record names no principal")
        for effect, owner in OWNER.items():
            if effect in effects and actor != owner:
                raise InvalidRecord(f"{effect} is the {owner}'s act")
        if unit is not None:
            self._check_transition(unit, actor, effects)

    def _expected_effects(self, unit: Optional[WorkUnit], action: dict, outcome: Any, env: Any) -> dict:
        """The only effects the given action may record with the given decision."""
        act_type = action.get("type")
        if outcome == "deny" or (outcome == "confirm" and act_type in ("tool", "memory_write")):
            return {}
        if outcome not in EFFECTING.get(act_type, ()):
            raise InvalidRecord(f"a {act_type!r} act cannot be recorded as {outcome!r}")
        if act_type == "open_package":
            pin = env.get("body", {}).get("pin") if isinstance(env, dict) and isinstance(env.get("body"), dict) else None
            return {"open": {**{k: action.get(k) for k in OPEN_FIELDS}, "pin": pin}}
        if act_type in ("tool", "method_run"):
            return {"state": "run"} if unit.state == "unit" else {}
        if act_type == "memory_write":
            return {}
        if act_type == "advance":
            to = action.get("to")
            if (to == "acceptance") != (outcome == "accepted"):
                raise InvalidRecord("only an advance to acceptance is recorded as accepted")
            return {"acceptance": True, "state": "acceptance"} if to == "acceptance" else {"state": to}
        if act_type == "accept":
            return {"acceptance": True, "state": "acceptance"}
        if act_type == "abort":
            return {"abort": True, "state": "disposition"}
        if act_type == "challenge":
            return {"challenge": {"note": action.get("note") or ""}}
        if act_type == "clear_challenge":
            if unit.advisor_challenge is not None:
                raise InvalidRecord("clear_challenge recorded against an existing challenge")
            return {}
        if act_type == "waive_challenge":
            if not (action.get("note") or "").strip():
                raise InvalidRecord("waiver without a rationale")
            return {"waived": True}
        if act_type == "clear_halt":
            if None not in self._halts:
                raise InvalidRecord("clear_halt with no kernel halt")
            return {"clear_halt": True}
        raise InvalidRecord(f"no effects are defined for {act_type!r}")

    def _check_transition(self, unit: WorkUnit, actor: str, effects: dict) -> None:
        if "challenge" in effects and unit.state not in ("evidence", "run"):
            raise InvalidRecord("challenge outside the Advisor station")
        if effects.get("waived") and (unit.advisor_challenge is None or unit.challenge_waived):
            raise InvalidRecord("waiver without an open challenge")
        state = effects.get("state")
        if state is None or effects.get("abort"):
            return
        try:
            chainmod.can_advance(unit, state, actor, self._kinds.get(unit.id, set()))
        except MxmError as exc:
            raise InvalidRecord(f"illegal transition {unit.state} -> {state} ({type(exc).__name__})") from None

    def _apply(self, rec: dict) -> None:
        kind, uid, p = rec.get("kind"), rec.get("unit_id"), rec.get("payload") or {}
        if kind == "halt":
            self._halts[None if p.get("scope") == "kernel" else uid] = {
                "reason": p.get("reason"), "detail": p.get("detail")}
        elif kind in EVIDENCE_KINDS:
            self._awaiting.pop(p["act_seq"], None)
            self._kinds[uid].add(kind)
        elif kind == "act":
            self._apply_act(rec, uid, p)
        self._applied = (rec["seq"], rec["hash"])

    def _apply_act(self, rec: dict, uid: Optional[str], p: dict) -> None:
        effects, env, action = p["effects"], p.get("authorization"), p["action"]
        outcome = p["decision"].get("kind")
        if env is not None:
            self._spent.add(authz.spent_id(env))
        opening = effects.get("open")
        if opening is not None:
            self.units[uid] = WorkUnit(
                id=uid, package_id=opening["package_id"], pin=opening["pin"], scope=opening["scope"],
                unit_type=opening["unit_type"], ad_hoc=opening["ad_hoc"], method_id=opening["method_id"],
                constitution_version=opening["constitution_version"])
            self._kinds[uid] = {"note"}
        if effects.get("clear_halt"):
            self._halts.pop(None, None)
        unit = self.units.get(uid) if uid is not None else None
        if unit is None:
            return
        evidence = EVIDENCE_OF.get(action.get("type")) if outcome == "allow" else None
        if effects.get("state") == "disposition":
            evidence = "memory"
        if evidence:
            self._awaiting[rec["seq"]] = (uid, evidence)
        if "challenge" in effects:
            unit.advisor_challenge = Challenge(note=effects["challenge"]["note"], ts=rec["ts"])
            unit.challenge_waived = False
        if effects.get("waived"):
            unit.challenge_waived = True
        if effects.get("acceptance"):
            unit.acceptance = Acceptance(ts=rec["ts"], actor="operator", pin=unit.pin)
        if "state" in effects:
            unit.state = effects["state"]
        kinds = self._kinds[uid]
        kinds.add("proposal")
        if outcome in ("deny", "confirm"):
            kinds.add(outcome)

    def _record(self, fields: dict) -> tuple[Optional[dict], Optional[str]]:
        """Validate, append and apply one record: the only way kernel state changes."""
        try:
            self._check({**fields, "seq": self._applied[0] + 1, "ts": _now()})
        except InvalidRecord as exc:
            return None, f"kernel_invariant: {exc}"
        try:
            rec = self.log.append(fields)
        except AnchorError as exc:
            self._apply(exc.record)
            self._record_kernel_halt("anchor_unwritable", str(exc))
            return exc.record, None
        except OSError as exc:
            return None, f"log_unwritable: {exc}"
        self._apply(rec)
        return rec, None

    def _record_kernel_halt(self, reason: str, detail: Any) -> None:
        fields = {"kind": "halt", "unit_id": None, "actor": "kernel",
                  "payload": {"scope": "kernel", "reason": reason, "detail": detail}}
        try:
            rec = self.log.append(fields)
        except AnchorError as exc:
            rec = exc.record
        except (OSError, ValueError):
            return
        self._apply(rec)

    # --- Ports. The actor is bound by the port, never read from the proposal. ---

    def assistant_propose(self, unit_id: str, proposal: dict) -> Decision:
        """The only entrypoint to expose to a model. Any ``actor`` or ``operator_ok`` in the
        proposal is discarded: the Assistant cannot claim another principal's authority."""
        fields = {k: v for k, v in dict(proposal).items() if k not in {"actor", "operator_ok"}}
        return self._submit(unit_id, Action(**fields, actor="assistant"), None)

    def operator_propose(self, unit_id: str, action: Action, authorization: Optional[dict] = None) -> Decision:
        return self._submit(unit_id, replace(action, actor="operator"), authorization)

    def advisor_propose(self, unit_id: str, action: Action, authorization: Optional[dict] = None) -> Decision:
        return self._submit(unit_id, replace(action, actor="advisor"), authorization)

    def open_package(self, package_id: str, authorization: Optional[dict] = None, scope: Optional[str] = None,
                     unit_type: str = "generic", ad_hoc: bool = False) -> Decision:
        """Operator act. The authorization must sign ``opening_act(...)`` for these arguments,
        and the new unit's id is the one it names."""
        act = self.opening_act(package_id, scope, unit_type, ad_hoc)
        with self._txn():
            stopped = self._stopped(None)
            if stopped:
                return stopped
            try:
                unit_id = authorization["body"]["unit_id"]
            except (TypeError, KeyError):
                unit_id = None
            principal, problem = self._authorize(authorization, "operator", act, unit_id, self.constitution.pin())
            if problem is None and not (isinstance(unit_id, str) and unit_id):
                problem = "malformed"
            if problem:
                return Decision(kind="deny", reason="unverified_operator", payload={"authorization": problem})
            if unit_id in self.units:
                return Decision(kind="deny", reason="unit_exists", unit_id=unit_id)
            opening = {**{k: act[k] for k in OPEN_FIELDS}, "pin": self.constitution.pin()}
            rec, err = self._record({"kind": "act", "unit_id": unit_id, "actor": "operator", "payload": {
                "action": {"actor": "operator", **act}, "authorization": authorization, "principal": principal,
                "decision": {"kind": "opened", "reason": "operator_act"}, "effects": {"open": opening}}})
            if rec is None:
                return Decision(kind="deny", reason=err, unit_id=unit_id)
            return Decision(kind="opened", reason="operator_act", unit_id=unit_id, state="package")

    def clear_halt(self, authorization: Optional[dict] = None) -> Decision:
        """Operator act: clear a recorded kernel halt. An integrity failure cannot be cleared
        in-band; it stops the kernel until the log is repaired out of band."""
        action = Action(type="clear_halt", actor="operator")
        with self._txn():
            if self._fatal:
                return Decision(kind="halt", reason=self._fatal["reason"], payload=self._fatal["detail"])
            principal, problem = self._authorize(authorization, "operator", authz.act_of(action), None, None)
            if problem:
                return self._commit(None, action, None, None, _deny("unverified_operator"), problem)
            if None not in self._halts:
                return self._commit(None, action, authorization, principal, _deny("no_halt"))
            return self._commit(None, action, authorization, principal,
                                ("cleared", "operator_act", {"clear_halt": True}, None))

    def accept(self, unit_id: str, authorization: Optional[dict] = None) -> Decision:
        return self.operator_propose(unit_id, Action(type="accept", operator_ok=True), authorization)

    def waive_challenge(self, unit_id: str, note: str = "", authorization: Optional[dict] = None) -> Decision:
        return self.operator_propose(unit_id, Action(type="waive_challenge", operator_ok=True, note=note),
                                     authorization)

    def abort(self, unit_id: str, authorization: Optional[dict] = None) -> Decision:
        return self.operator_propose(unit_id, Action(type="abort", operator_ok=True), authorization)

    def challenge(self, unit_id: str, note: str, authorization: Optional[dict] = None) -> Decision:
        return self.advisor_propose(unit_id, Action(type="challenge", note=note), authorization)

    def clear_challenge(self, unit_id: str, authorization: Optional[dict] = None) -> Decision:
        return self.advisor_propose(unit_id, Action(type="clear_challenge"), authorization)

    # --- Deciding and committing ---

    def _stopped(self, unit_id: Optional[str]) -> Optional[Decision]:
        if self._fatal:
            return Decision(kind="halt", reason=self._fatal["reason"], payload=self._fatal["detail"], unit_id=unit_id)
        halt = self._halts.get(None) or (self._halts.get(unit_id) if unit_id else None)
        if halt:
            unit = self.units.get(unit_id) if unit_id else None
            return Decision(kind="halt", reason=halt["reason"], payload=halt["detail"], unit_id=unit_id,
                            state=unit.state if unit else None)
        return None

    def _authorize(self, envelope, role: str, act: dict, unit_id: Optional[str], pin: Optional[str]):
        return authz.check(envelope, self.trust, role=role, unit_id=unit_id, act=act, pin=pin,
                           seq=self._applied[0] + 1, now=datetime.now(timezone.utc), consumed=self._spent)

    def _submit(self, unit_id: str, action: Action, envelope: Optional[dict]) -> Decision:
        with self._txn():
            stopped = self._stopped(unit_id)
            if stopped:
                return stopped
            unit = self.units.get(unit_id)
            if unit is None:
                return Decision(kind="deny", reason="unknown_unit", unit_id=unit_id)
            if self.constitution.pin() != unit.pin:
                self._record({"kind": "halt", "unit_id": unit.id, "actor": "kernel",
                              "payload": {"scope": "unit", "reason": "constitution_mismatch", "detail": None}})
                return Decision(kind="halt", reason="constitution_mismatch", unit_id=unit.id, state=unit.state)
            principal = None
            if action.actor in PRINCIPALS:
                principal, problem = self._authorize(envelope, action.actor, authz.act_of(action), unit_id, unit.pin)
                if problem:
                    return self._commit(unit_id, action, None, None, _deny(f"unverified_{action.actor}"), problem)
            else:
                envelope = None
            return self._commit(unit_id, action, envelope, principal, self._decide(unit, action))

    def _commit(self, unit_id, action: Action, envelope, principal, decided, problem=None) -> Decision:
        kind, reason, effects, side = decided
        payload = {"action": action.to_dict(), "authorization": envelope, "principal": principal,
                   "decision": {"kind": kind, "reason": reason}, "effects": effects}
        if problem:
            payload["authorization_problem"] = problem
        halted_before = None in self._halts
        rec, err = self._record({"kind": "act", "unit_id": unit_id, "actor": action.actor, "payload": payload})
        unit = self.units.get(unit_id) if unit_id else None
        state = unit.state if unit else None
        if rec is None:
            return Decision(kind="deny", reason=err, unit_id=unit_id, state=state)
        out: Any = {"authorization": problem} if problem else None
        halted = self._halts.get(None)
        if halted and not halted_before:  # recording this act halted the kernel: its effect does not run
            owed = self._awaiting.get(rec["seq"])
            if owed:
                self._evidence(owed[0], owed[1], {"act_seq": rec["seq"], "outcome": "not_executed"})
            return Decision(kind="halt", reason=halted["reason"], payload=halted["detail"], unit_id=unit_id, state=state)
        if side is not None:
            kind, reason, out = self._side_effect(unit, action, side, rec, kind, reason)
        return Decision(kind=kind, reason=reason, payload=out, unit_id=unit_id, state=state)

    def _evidence(self, unit_id: str, kind: str, payload: dict) -> Optional[str]:
        """Record an act's closing evidence. If it cannot be recorded, the effect's outcome is
        no longer provable from the log, so the kernel stops (``evidence_unwritable``)."""
        rec, err = self._record({"kind": kind, "unit_id": unit_id, "actor": "kernel", "payload": payload})
        if rec is None:
            self._fatal = {"reason": "evidence_unwritable", "detail": err}
        return err

    def _side_effect(self, unit: WorkUnit, action: Action, side: tuple, rec: dict, kind: str, reason: str):
        """Perform an effect the kernel has already recorded, and record its receipt. A failing
        effect is recorded and denied; it never raises past the port."""
        what = side[0]
        evidence = "receipt" if what in ("tool", "method") else "memory"
        try:
            if what == "tool":
                out = self.broker.execute(action)
            elif what == "method":
                out = {"method_id": side[1], "result": self.methods.run(side[1], action.args or {})}
            elif what == "memory_write":
                out = self.memory.write(unit.id, side[1], action.args, accepted=unit.acceptance is not None)
            elif what == "memory_commit":
                kept = self.memory.commit(unit.id)
                out = {"event": "commit", "kept": len(kept)}
            else:  # acceptance: the log is authoritative; the memory row is a projection of it
                try:
                    self.memory.write(unit.id, "acceptance", unit.acceptance.__dict__, accepted=True)
                    return kind, reason, None
                except Exception as exc:
                    return kind, reason, {"memory_error": f"{type(exc).__name__}: {exc}"}
            out = {**out, "outcome": "done"}
        except Exception as exc:
            out, kind, reason = ({"outcome": "failed", "error": f"{type(exc).__name__}: {exc}"},
                                 "deny", f"{what}_failed")
        out = {**out, "attribution": self.attribution}
        err = self._evidence(unit.id, evidence, {"act_seq": rec["seq"], **out})
        if err:
            return "halt", "evidence_unwritable", {"effect": out, "error": err}
        if what == "memory_commit" and kind != "deny":
            return kind, reason, kept
        return kind, reason, out

    def _decide(self, unit: WorkUnit, action: Action):
        """(kind, reason, effects, side effect). Pure: reads state, changes nothing."""
        handler = {"tool": self._decide_tool, "method_run": self._decide_method,
                   "advance": self._decide_advance, "accept": self._decide_accept,
                   "challenge": self._decide_challenge, "clear_challenge": self._decide_clear,
                   "waive_challenge": self._decide_waive, "memory_write": self._decide_memory,
                   "abort": self._decide_abort}.get(action.type)
        return handler(unit, action) if handler else _deny("unknown_action")

    def _mission_ok(self, unit: WorkUnit, action: Action) -> bool:
        if not action.target:
            spec = self.broker.tools.get(action.tool or "")
            return spec is None or spec.scope_optional
        return action.target in unit.scope or unit.scope in action.target

    @staticmethod
    def _to_run(unit: WorkUnit) -> dict:
        return {"state": "run"} if unit.state == "unit" else {}

    def _decide_tool(self, unit: WorkUnit, action: Action):
        if unit.state not in {"unit", "run", "evidence"}:
            return _deny("tools_not_in_this_state")
        if not self._mission_ok(unit, action):
            return _deny("out_of_mission")
        if unit.method_id and not unit.ad_hoc and action.tool != unit.method_id:
            return _deny("method_required")
        kind, reason = self.broker.decide(action)
        if kind != "allow":
            return kind, reason, {}, None
        return "allow", reason, self._to_run(unit), ("tool",)

    def _decide_method(self, unit: WorkUnit, action: Action):
        if unit.state not in {"unit", "run"}:
            return _deny("method_not_in_this_state")
        method_id = action.method_id or unit.method_id
        if not method_id:
            return _deny("no_method")
        if not self.methods.has(method_id):
            return _deny("unknown_method")
        return "allow", "method_ok", self._to_run(unit), ("method", method_id)

    def _decide_advance(self, unit: WorkUnit, action: Action):
        to = action.to
        if not to:
            return _deny("missing_target_state")
        try:
            chainmod.can_advance(unit, to, action.actor, self._kinds[unit.id])
        except NotOperator:
            return _deny("not_operator")
        except BlockedByAdvisor:
            return _deny("blocked_by_advisor")
        except NeedAcceptance:
            return _deny("need_acceptance")
        except IllegalTransition:
            return _deny("illegal_transition")
        if to == "acceptance":
            return self._decide_accept(unit, action)
        if to == "disposition":
            return "advanced", "ok", {"state": to}, ("memory_commit",)
        return "advanced", "ok", {"state": to}, None

    def _decide_accept(self, unit: WorkUnit, action: Action):
        if action.actor != "operator":
            return _deny("not_operator")
        if unit.state != "evidence":
            return _deny("illegal_transition")
        if unit.advisor_challenge and not unit.challenge_waived:
            return _deny("blocked_by_advisor")
        return "accepted", "operator_act", {"acceptance": True, "state": "acceptance"}, ("acceptance",)

    def _decide_challenge(self, unit: WorkUnit, action: Action):
        if action.actor != "advisor":
            return _deny("not_advisor")
        if unit.state not in {"evidence", "run"}:
            return _deny("challenge_station")
        return "challenged", "recorded", {"challenge": {"note": action.note or ""}}, None

    def _decide_clear(self, unit: WorkUnit, action: Action):
        if action.actor != "advisor":
            return _deny("not_advisor")
        if unit.advisor_challenge is None:
            return "waived", "no_challenge", {}, None
        # Clear is not a waiver of an existing challenge; the Operator must waive.
        return _deny("challenge_exists_operator_must_waive")

    def _decide_waive(self, unit: WorkUnit, action: Action):
        if action.actor != "operator":
            return _deny("not_operator")
        if unit.advisor_challenge is None or unit.challenge_waived:
            return _deny("no_open_challenge")
        if not (action.note or "").strip():
            return _deny("waiver_requires_rationale")
        return "waived", "operator_act", {"waived": True}, None

    def _decide_memory(self, unit: WorkUnit, action: Action):
        kind = action.memory_kind or "scratch"
        if kind in DURABLE_MEMORY and kind != "acceptance" and unit.acceptance is None:
            return _deny("durable_memory_requires_acceptance")
        verdict = check(self.constitution.morals, action)
        if verdict == "DENY":
            return _deny("morals.hard_stop")
        if verdict == "CONFIRM" and action.actor != "operator":
            return "confirm", "morals.soft_stop", {}, None
        return "allow", "memory_written", {}, ("memory_write", kind)

    def _decide_abort(self, unit: WorkUnit, action: Action):
        if action.actor != "operator":
            return _deny("not_operator")
        return "advanced", "aborted", {"abort": True, "state": "disposition"}, ("memory_commit",)
