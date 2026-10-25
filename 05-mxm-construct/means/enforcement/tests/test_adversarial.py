"""Negative conformance: the SPEC §3 threat model, as tests (WP-TMH-0016, WP-MXK-0005).

P0 findings (F-16 identity, F-17 evidence integrity, F-19 persistence) and the #36 release
blockers must hold. P1 findings are strict xfails that name their recommendation: when a fix
lands, the xfail turns into an unexpected pass and must be promoted to a plain test.
"""
from __future__ import annotations

import json
import shutil
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mxm_testing import ADVISOR, CONST, OPERATOR, Harness, make_trust  # noqa: E402
from mxm import audit_chain  # noqa: E402
from mxm.authz import Signer, Trust, act_of  # noqa: E402
from mxm.means import ToolSpec  # noqa: E402
from mxm.kernel import OPEN_FIELDS, default_tools  # noqa: E402
from mxm.types import Action  # noqa: E402

ADVANCE = Action(type="advance", to="unit")


def lines(h):
    return h.k.log.path.read_text().splitlines()


def write_lines(h, rows):
    h.k.log.path.write_text("\n".join(rows) + "\n")


def forge(h, **fields):
    """Append a well-chained record directly to the log, as an engine with write access could.
    The forgery is made valid in every respect except the one under test: a signed act names
    its key's real principal, and evidence states an outcome, unless the test sets them."""
    payload = fields.get("payload")
    if isinstance(payload, dict):
        auth = payload.get("authorization")
        if fields.get("kind") == "act" and isinstance(auth, dict) and payload.get("principal") is None:
            key = h.trust.keys.get(auth.get("body", {}).get("key_id"))
            if key is not None:
                payload["principal"] = key.principal
        if fields.get("kind") in ("receipt", "memory"):
            payload.setdefault("outcome", "done")
    return audit_chain.append(h.k.log.path, fields)


# --- F-16: the Assistant cannot claim another principal's authority ------------------

def test_f16_assistant_payload_cannot_claim_operator_or_advisor(tmp_path):
    h = Harness(tmp_path)
    uid = h.at_evidence()
    h.challenge(uid, "not ready")
    for forged in ({"type": "waive_challenge", "actor": "operator", "operator_ok": True},
                   {"type": "accept", "actor": "operator", "operator_ok": True},
                   {"type": "challenge", "actor": "advisor", "note": "self-clear"}):
        assert h.k.assistant_propose(uid, forged).kind == "deny", forged
    assert h.unit(uid).acceptance is None and not h.unit(uid).challenge_waived


def test_f16_assistant_payload_cannot_unlock_privileged_tools(tmp_path):
    h = Harness(tmp_path)
    uid = h.at_evidence()
    d = h.k.assistant_propose(uid, {"type": "tool", "tool": "send_email", "actor": "operator", "operator_ok": True})
    assert d.kind == "deny"


def test_f16_open_package_requires_a_signed_operator_authorization(tmp_path):
    h = Harness(tmp_path)
    pin = h.k.constitution.pin()
    assert h.k.open_package("probe").payload == {"authorization": "missing"}
    by_advisor = ADVISOR.authorize("u1", h.k.opening_act("probe"), pin)
    assert h.k.open_package("probe", by_advisor).payload == {"authorization": "wrong_role"}
    other_package = OPERATOR.authorize("u1", h.k.opening_act("elsewhere"), pin)
    d = h.k.open_package("probe", other_package)
    assert (d.kind, d.reason, d.payload) == ("deny", "unverified_operator", {"authorization": "act_mismatch"})
    assert h.k.records() == [] and h.k.units == {}


def test_open_package_refuses_an_existing_unit_id(tmp_path):
    h = Harness(tmp_path)
    uid = h.open("probe")
    again = OPERATOR.authorize(uid, h.k.opening_act("probe"), h.k.constitution.pin())
    assert h.k.open_package("probe", again).reason == "unit_exists"


def _authorization(case, h, uid):
    now = datetime.now(timezone.utc)
    if case == "missing":
        return None
    if case == "malformed":
        return {"body": {"v": 1}, "sig": "zz"}
    if case == "unknown_key":
        return h.sign(Signer("stranger", "operator", bytes(32)), uid, ADVANCE)
    if case == "wrong_role":
        return h.sign(ADVISOR, uid, ADVANCE)
    if case == "bad_signature":
        env = h.sign(OPERATOR, uid, ADVANCE)
        env["body"]["expires_at"] = (now + timedelta(days=365)).isoformat()
        return env
    if case == "forged_key_id":
        return h.sign(Signer("op-test", "operator", bytes(32)), uid, ADVANCE)
    if case == "wrong_unit":
        return h.sign(OPERATOR, "another-unit", ADVANCE)
    if case == "act_mismatch":
        return h.sign(OPERATOR, uid, Action(type="advance", to="run"))
    if case == "wrong_pin":
        return OPERATOR.authorize(uid, act_of(ADVANCE), "0" * 64)
    if case == "expired":
        return h.sign(OPERATOR, uid, ADVANCE, ttl=60, now=now - timedelta(hours=1))
    if case == "not_yet_valid":
        return h.sign(OPERATOR, uid, ADVANCE, now=now + timedelta(hours=1))
    raise AssertionError(case)


@pytest.mark.parametrize("case", ["missing", "malformed", "unknown_key", "wrong_role", "bad_signature",
                                  "forged_key_id", "wrong_unit", "act_mismatch", "wrong_pin", "expired",
                                  "not_yet_valid"])
def test_f16_operator_port_denies_any_authorization_that_does_not_fit_the_act(tmp_path, case):
    h = Harness(tmp_path)
    uid = h.open("probe")
    d = h.k.operator_propose(uid, ADVANCE, _authorization(case, h, uid))
    expected = "expired" if case == "not_yet_valid" else "bad_signature" if case == "forged_key_id" else case
    assert (d.kind, d.reason, d.payload) == ("deny", "unverified_operator", {"authorization": expected})
    assert h.unit(uid).state == "package"


def test_f16_an_authorization_is_single_use_across_kernels(tmp_path):
    h = Harness(tmp_path)
    uid = h.open("probe")
    env = h.sign(OPERATOR, uid, ADVANCE)
    assert h.k.operator_propose(uid, ADVANCE, env).kind == "advanced"
    assert h.k.operator_propose(uid, ADVANCE, env).payload == {"authorization": "replayed"}
    assert h.restart().k.operator_propose(uid, ADVANCE, env).payload == {"authorization": "replayed"}


def test_f16_a_retired_key_signs_nothing_new_but_its_history_still_verifies(tmp_path):
    retired = dict(OPERATOR.trust_entry("operator-under-test"), valid_through_seq=2)
    h = Harness(tmp_path, trust=Trust.from_entries([retired, ADVISOR.trust_entry("advisor-under-test")]))
    uid = h.at_unit()  # records 1 and 2: signed while the key was valid
    assert h.op(uid, Action(type="advance", to="run")).payload == {"authorization": "key_retired"}
    assert h.restart().assist(uid, type="tool", tool="echo").kind == "allow"


def test_f16_advisor_port_requires_an_advisor_authorization(tmp_path):
    h = Harness(tmp_path)
    uid = h.at_evidence()
    note = Action(type="challenge", note="x")
    assert h.k.challenge(uid, "x").payload == {"authorization": "missing"}
    assert h.k.advisor_propose(uid, note, h.sign(OPERATOR, uid, note)).payload == {"authorization": "wrong_role"}
    assert h.unit(uid).advisor_challenge is None


def test_clear_challenge_uses_the_advisor_port(tmp_path):
    h = Harness(tmp_path, trust=make_trust(advisor="adv-bob"))
    assert h.clear_challenge("no-such-unit").reason == "unknown_unit"
    uid = h.at_evidence()
    assert h.clear_challenge(uid).reason == "no_challenge"
    h.challenge(uid, "gap")
    assert h.clear_challenge(uid).reason == "challenge_exists_operator_must_waive"
    clears = [r for r in h.k.records(uid) if r["kind"] == "act" and r["payload"]["action"]["type"] == "clear_challenge"]
    assert len(clears) == 2 and all(r["payload"]["principal"] == "adv-bob" for r in clears)


def test_r06_waiver_needs_an_open_challenge_and_a_rationale(tmp_path):
    h = Harness(tmp_path)
    uid = h.at_evidence()
    assert h.waive(uid, "why").reason == "no_open_challenge"
    h.challenge(uid, "gap")
    assert h.waive(uid, "  ").reason == "waiver_requires_rationale"
    assert h.waive(uid, "risk accepted: reversible").kind == "waived"
    assert h.waive(uid, "again").reason == "no_open_challenge"


def test_unknown_unit_is_denied_not_raised(tmp_path):
    h = Harness(tmp_path)
    assert h.assist("no-such-unit", type="tool", tool="echo").reason == "unknown_unit"


def test_p3_on_disk_constitution_edit_does_not_reach_the_running_kernel(tmp_path):
    const = tmp_path / "c.json"
    shutil.copy(CONST, const)
    h = Harness(tmp_path / "k", const=const)
    uid = h.at_unit()
    doc = json.loads(const.read_text()); doc["morals"]["hard_stops"] = []; const.write_text(json.dumps(doc))
    assert h.op(uid, Action(type="tool", tool="send_email")).kind != "allow"


# --- Release blocker 5: authority lives in the log, not in which method was called ---

def test_blocker5_in_process_bypass_cannot_commit_an_unauthorized_operator_effect(tmp_path):
    h = Harness(tmp_path)
    uid = h.at_evidence()
    before = h.k.records()
    forged = Action(type="accept", actor="operator", operator_ok=True)
    with h.k._txn():
        d = h.k._commit(uid, forged, None, None,
                        ("accepted", "operator_act", {"acceptance": True, "state": "acceptance"}, ("acceptance",)))
        rec, err = h.k._record({"kind": "act", "unit_id": uid, "actor": "assistant", "payload": {
            "action": {"type": "accept", "actor": "assistant"}, "authorization": None, "principal": None,
            "decision": {"kind": "accepted", "reason": "x"}, "effects": {"acceptance": True, "state": "acceptance"}}})
    assert d.kind == "deny" and d.reason.startswith("kernel_invariant") and rec is None and err
    assert h.k.records() == before and h.unit(uid).acceptance is None


def _act(actor, uid, effects, authorization=None, kind="accepted", type_="accept"):
    return {"kind": "act", "unit_id": uid, "actor": actor, "payload": {
        "action": {"type": type_, "actor": actor, "operator_ok": True}, "authorization": authorization,
        "principal": None, "decision": {"kind": kind, "reason": "forged"}, "effects": effects}}


@pytest.mark.parametrize("forgery", ["unsigned_operator", "assistant_acceptance", "replayed_authorization",
                                     "unknown_key", "illegal_transition", "assistant_challenge",
                                     "advisor_signed_waiver", "intercepted_open_widened",
                                     "intercepted_open_reuses_a_unit", "intercepted_clear_with_extra_effects"])
def test_a_forged_record_in_the_log_halts_every_kernel(tmp_path, forgery):
    h = Harness(tmp_path)
    uid = h.at_evidence()
    accept = {"acceptance": True, "state": "acceptance"}
    if forgery == "unsigned_operator":
        forge(h, **_act("operator", uid, accept))
    elif forgery == "assistant_acceptance":
        forge(h, **_act("assistant", uid, accept))
    elif forgery == "replayed_authorization":
        spent = next(r for r in h.k.records(uid) if r["actor"] == "operator" and r["payload"]["action"]["type"] == "advance")
        forge(h, **{k: spent[k] for k in ("kind", "unit_id", "actor", "payload")})
    elif forgery == "unknown_key":
        engine_key = Signer("engine-minted", "operator", bytes(range(64, 96)))
        act = act_of(Action(type="accept", operator_ok=True))
        forge(h, **_act("operator", uid, accept, engine_key.authorize(uid, act, h.pin(uid))))
    elif forgery == "assistant_challenge":
        forge(h, **_act("assistant", uid, {"challenge": {"note": "self-block"}}, kind="challenged", type_="challenge"))
    elif forgery == "advisor_signed_waiver":
        h.challenge(uid, "gap")
        waiver = Action(type="waive_challenge", operator_ok=True, note="advisor waives")
        record = _act("advisor", uid, {"waived": True}, h.sign(ADVISOR, uid, waiver), kind="waived", type_="waive_challenge")
        record["payload"]["action"] = {**waiver.to_dict(), "actor": "advisor"}
        forge(h, **record)
    elif forgery.startswith("intercepted_open"):
        # A genuine, unspent Operator authorization, wrapped in a record the kernel would not write.
        target = uid if forgery.endswith("reuses_a_unit") else "fresh-unit"
        act = h.k.opening_act("probe", scope="internal-drafts")
        opening = {**{k: act[k] for k in OPEN_FIELDS}, "pin": h.pin(None)}
        if forgery.endswith("widened"):
            opening["scope"] = "everything"
        forge(h, kind="act", unit_id=target, actor="operator", payload={
            "action": {"actor": "operator", **act}, "authorization": OPERATOR.authorize(target, act, h.pin(None)),
            "principal": None, "decision": {"kind": "opened", "reason": "forged"}, "effects": {"open": opening}})
    elif forgery == "intercepted_clear_with_extra_effects":
        clear = Action(type="clear_halt")
        forge(h, kind="act", unit_id=None, actor="operator", payload={
            "action": {**clear.to_dict(), "actor": "operator"}, "authorization": OPERATOR.authorize(None, act_of(clear), None),
            "principal": None, "decision": {"kind": "cleared", "reason": "forged"},
            "effects": {"clear_halt": True, "state": "disposition"}})
    else:
        forge(h, **_act("assistant", uid, {"state": "disposition"}, kind="advanced", type_="advance"))
    d = h.assist(uid, type="tool", tool="echo")
    assert (d.kind, d.reason) == ("halt", "invalid_record")
    restarted = h.restart()
    assert restarted.accept(uid).reason == "invalid_record"
    assert restarted.unit(uid).acceptance is None and restarted.unit(uid).state == "evidence"


# --- WP-MXK-0006: a valid signature cannot carry effects its action does not produce ----

SIGNED = {  # a genuine, unspent authorization for each of these, intercepted by the engine
    "waive": ("operator", Action(type="waive_challenge", operator_ok=True, note="ok")),
    "accept": ("operator", Action(type="accept", operator_ok=True)),
    "abort": ("operator", Action(type="abort", operator_ok=True)),
    "advance": ("operator", Action(type="advance", to="integration")),
    "challenge": ("advisor", Action(type="challenge", note="x")),
    "clear_challenge": ("advisor", Action(type="clear_challenge")),
    "clear_halt": ("operator", Action(type="clear_halt")),
}
EFFECT_CLASSES = {
    "abort": ({"abort": True, "state": "disposition"}, "advanced"),
    "accept": ({"acceptance": True, "state": "acceptance"}, "accepted"),
    "waive": ({"waived": True}, "waived"),
    "challenge": ({"challenge": {"note": "x"}}, "challenged"),
    "advance": ({"state": "integration"}, "advanced"),
    "clear_halt": ({"clear_halt": True}, "cleared"),
    "run": ({"state": "run"}, "allow"),
    "open": ("open", "opened"),
}
LEGITIMATE = {("waive", "waive"), ("abort", "abort"), ("challenge", "challenge")}
SUBSTITUTIONS = [(a, e) for a in SIGNED for e in EFFECT_CLASSES if (a, e) not in LEGITIMATE]


@pytest.mark.parametrize("signed, effect", SUBSTITUTIONS)
def test_a_valid_signature_cannot_carry_another_acts_effects(tmp_path, signed, effect):
    h = Harness(tmp_path)
    uid = h.at_evidence()
    h.challenge(uid, "gap")
    role, action = SIGNED[signed]
    scope = None if action.type == "clear_halt" else uid
    signer = OPERATOR if role == "operator" else ADVISOR
    auth = signer.authorize(scope, act_of(action), h.pin(scope) if scope else None)
    effects, kind = EFFECT_CLASSES[effect]
    if effects == "open":
        act = h.k.opening_act("probe")
        effects = {"open": {**{k: act[k] for k in OPEN_FIELDS}, "pin": h.pin(None)}}
    forge(h, kind="act", unit_id=scope, actor=role, payload={
        "action": {**action.to_dict(), "actor": role}, "authorization": auth, "principal": None,
        "decision": {"kind": kind, "reason": "forged"}, "effects": effects})
    restarted = h.restart()
    assert restarted.assist(uid, type="tool", tool="echo").reason == "invalid_record"
    unit = restarted.unit(uid)
    assert (unit.state, unit.acceptance, unit.challenge_waived) == ("evidence", None, False)


@pytest.mark.parametrize("case", ["right_effects_wrong_decision", "empty_rationale_waiver",
                                  "unit_scoped_clear_halt"])
def test_a_signed_act_must_also_be_one_the_kernel_would_record(tmp_path, case):
    h = Harness(tmp_path)
    uid = h.at_evidence()
    h.challenge(uid, "gap")
    scope, kind, effects = uid, "waived", {"waived": True}
    if case == "right_effects_wrong_decision":
        action, kind = Action(type="waive_challenge", operator_ok=True, note="ok"), "accepted"
    elif case == "empty_rationale_waiver":
        action = Action(type="waive_challenge", operator_ok=True, note="  ")
    else:
        forge(h, kind="halt", unit_id=None, actor="kernel", payload={"scope": "kernel", "reason": "anchor_unwritable"})
        action, kind, effects = Action(type="clear_halt"), "cleared", {"clear_halt": True}
    forge(h, kind="act", unit_id=scope, actor="operator", payload={
        "action": {**action.to_dict(), "actor": "operator"}, "authorization": h.sign(OPERATOR, scope, action),
        "principal": None, "decision": {"kind": kind, "reason": "forged"}, "effects": effects})
    restarted = h.restart()
    assert restarted.assist(uid, type="tool", tool="echo").reason == "invalid_record"
    assert not restarted.unit(uid).challenge_waived


def test_the_legitimate_pairings_still_replay(tmp_path):
    h = Harness(tmp_path)
    uid = h.at_evidence()
    h.challenge(uid, "gap")
    h.waive(uid, "ok")
    h.challenge(uid, "again")
    h.abort(uid)
    restarted = h.restart()
    assert restarted.k._fatal is None and restarted.unit(uid).state == "disposition"


def test_an_open_must_sign_the_resolved_unit(tmp_path):
    from mxm.authz import open_act
    h = Harness(tmp_path)
    pin = h.k.constitution.pin()
    unresolved = {"type": "open_package", "package_id": "probe", "scope": None, "unit_type": "generic",
                  "ad_hoc": False, "method_id": None, "constitution_version": h.k.constitution.version}
    assert h.k.open_package("probe", OPERATOR.authorize("u1", unresolved, pin)).payload == {"authorization": "act_mismatch"}
    h.k.methods.register("001_echo_draft", "draft", lambda args: {})
    no_method = open_act("probe", "internal-drafts", "draft", False, None, h.k.constitution.version)
    d = h.k.open_package("probe", OPERATOR.authorize("u2", no_method, pin), scope="internal-drafts", unit_type="draft")
    assert d.payload == {"authorization": "act_mismatch"}
    assert h.k.units == {}


@pytest.mark.parametrize("forgery", ["orphan_receipt", "receipt_by_assistant", "second_receipt",
                                     "memory_for_a_tool", "halt_by_assistant"])
def test_evidence_records_must_answer_an_act(tmp_path, forgery):
    h = Harness(tmp_path)
    uid = h.at_unit()
    h.assist(uid, type="tool", tool="echo", args={"text": "x"})
    tool_act = next(r for r in h.k.records(uid) if r["kind"] == "act" and r["payload"]["action"]["type"] == "tool")
    if forgery == "orphan_receipt":
        forge(h, kind="receipt", unit_id=uid, actor="kernel", payload={"act_seq": 1, "receipt": {"echo": "forged"}})
    elif forgery == "receipt_by_assistant":
        h.k.log.path.write_text("\n".join(lines(h)[:-1]) + "\n")  # drop the real receipt, then forge one
        forge(h, kind="receipt", unit_id=uid, actor="assistant", payload={"act_seq": tool_act["seq"]})
    elif forgery == "second_receipt":
        forge(h, kind="receipt", unit_id=uid, actor="kernel", payload={"act_seq": tool_act["seq"]})
    elif forgery == "memory_for_a_tool":
        h.k.log.path.write_text("\n".join(lines(h)[:-1]) + "\n")
        forge(h, kind="memory", unit_id=uid, actor="kernel", payload={"act_seq": tool_act["seq"]})
    else:
        forge(h, kind="halt", unit_id=None, actor="assistant", payload={"scope": "kernel", "reason": "x"})
    assert h.restart().assist(uid, type="tool", tool="echo").reason == "invalid_record"


def test_a_lagging_anchor_is_moved_forward_not_treated_as_tampering(tmp_path):
    anchor = tmp_path / "anchor" / "head.json"
    h = Harness(tmp_path / "data", anchor=anchor)
    uid = h.at_unit()
    lagging = json.loads(anchor.read_text())
    h.assist(uid, type="tool", tool="echo")
    anchor.write_text(json.dumps(lagging))  # as if the process died between append and anchor write
    head = h.k.records()[-1]["seq"]
    restarted = h.restart()  # catch-up alone, before any new append, moves the anchor forward
    assert json.loads(anchor.read_text())["seq"] == head
    assert restarted.assist(uid, type="tool", tool="echo").kind == "allow"


def test_a_deleted_anchor_halts(tmp_path):
    anchor = tmp_path / "anchor" / "head.json"
    h = Harness(tmp_path / "data", anchor=anchor)
    uid = h.at_unit()
    anchor.unlink()
    assert h.restart().assist(uid, type="tool", tool="echo").reason == "anchor_missing"


def test_a_failing_memory_write_is_recorded_and_denied_not_raised(tmp_path):
    h = Harness(tmp_path)
    uid = h.at_unit()
    (tmp_path / "memory" / f"{uid}.json").mkdir(parents=True)
    d = h.assist(uid, type="memory_write", memory_kind="scratch", args={"x": 1})
    assert (d.kind, d.reason) == ("deny", "memory_write_failed")
    assert h.restart().assist(uid, type="tool", tool="echo").kind == "allow"


# --- WP-MXK-0007: principal records are signed; every act's outcome is closed -------------

@pytest.mark.parametrize("forgery", ["unsigned_advisor_clear", "unsigned_operator_deny_with_principal",
                                     "unsigned_operator_other_deny", "assistant_names_a_principal",
                                     "signed_with_wrong_principal"])
def test_a_principal_record_is_signed_or_is_the_kernels_unverified_denial(tmp_path, forgery):
    h = Harness(tmp_path)
    uid = h.at_evidence()
    clear = Action(type="clear_challenge")
    waive = Action(type="waive_challenge", operator_ok=True, note="ok")
    payload = {"authorization": None, "principal": None, "effects": {}}
    if forgery == "unsigned_advisor_clear":
        payload.update(action={**clear.to_dict(), "actor": "advisor"}, decision={"kind": "waived", "reason": "no_challenge"})
        actor = "advisor"
    elif forgery == "unsigned_operator_deny_with_principal":
        payload.update(action={**waive.to_dict(), "actor": "operator"}, principal="operator-under-test",
                       decision={"kind": "deny", "reason": "unverified_operator"}, authorization_problem="missing")
        actor = "operator"
    elif forgery == "unsigned_operator_other_deny":
        payload.update(action={**waive.to_dict(), "actor": "operator"}, decision={"kind": "deny", "reason": "no_open_challenge"})
        actor = "operator"
    elif forgery == "assistant_names_a_principal":
        payload.update(action={**Action(type="tool", tool="echo").to_dict(), "actor": "assistant"},
                       principal="operator-under-test", decision={"kind": "deny", "reason": "x"})
        actor = "assistant"
    else:
        payload.update(action={**clear.to_dict(), "actor": "advisor"}, authorization=h.sign(ADVISOR, uid, clear),
                       principal="someone-else", decision={"kind": "waived", "reason": "no_challenge"})
        actor = "advisor"
    forge(h, kind="act", unit_id=uid, actor=actor, payload=payload)
    assert h.restart().assist(uid, type="tool", tool="echo").reason == "invalid_record"


def test_the_kernels_own_unverified_denials_still_replay(tmp_path):
    h = Harness(tmp_path)
    uid = h.at_evidence()
    assert h.k.accept(uid).reason == "unverified_operator"
    assert h.k.challenge(uid, "x").reason == "unverified_advisor"
    assert h.k.clear_halt().reason == "unverified_operator"
    assert h.restart().k._fatal is None


def test_every_outcome_is_closed_exactly_once(tmp_path):
    h = Harness(tmp_path)
    uid = h.at_unit()
    h.assist(uid, type="tool", tool="echo")
    h.assist(uid, type="memory_write", memory_kind="scratch", args={"x": 1})
    closing = [r["payload"]["outcome"] for r in h.k.records(uid) if r["kind"] in ("receipt", "memory")]
    assert closing == ["done", "done"] and h.k._awaiting == {}


@pytest.mark.parametrize("outcome", ["done_with_error", "failed_without_error", "invented"])
def test_a_closing_record_must_state_a_consistent_outcome(tmp_path, outcome):
    h = Harness(tmp_path)
    uid = h.at_unit()
    h.assist(uid, type="tool", tool="echo")
    tool_act = next(r for r in h.k.records(uid) if r["kind"] == "act" and r["payload"]["action"]["type"] == "tool")
    write_lines(h, lines(h)[:-1])  # drop the real receipt
    payload = {"act_seq": tool_act["seq"], "outcome": {"done_with_error": "done", "failed_without_error": "failed",
                                                       "invented": "probably"}[outcome]}
    if outcome == "done_with_error":
        payload["error"] = "x"
    forge(h, kind="receipt", unit_id=uid, actor="kernel", payload=payload)
    assert h.restart().assist(uid, type="tool", tool="echo").reason == "invalid_record"


def test_a_process_that_stops_mid_effect_leaves_an_unknown_outcome_not_a_gap(tmp_path):
    def dies(args):
        raise KeyboardInterrupt  # the process stops between recording the act and its receipt
    h = Harness(tmp_path, tools={**default_tools(), "echo": ToolSpec("echo", dies)})
    uid = h.at_unit()
    with pytest.raises(KeyboardInterrupt):
        h.assist(uid, type="tool", tool="echo")
    assert not [r for r in h.k.records(uid) if r["kind"] == "receipt"]
    restarted = h.restart()
    assert [r["payload"]["outcome"] for r in restarted.k.records(uid) if r["kind"] == "receipt"] == ["unknown"]
    assert restarted.k._awaiting == {} and restarted.k._fatal is None


def test_an_unwritable_evidence_record_halts_instead_of_reporting_success(tmp_path):
    state = {}

    def ran(args):
        state["ran"] = True
        def refuse(fields):
            raise OSError("disk full")
        h.k.log.append = refuse  # the effect has happened; recording it now fails
        return {"ok": True}
    h = Harness(tmp_path, tools={**default_tools(), "echo": ToolSpec("echo", ran)})
    uid = h.at_unit()
    d = h.assist(uid, type="tool", tool="echo")
    assert state["ran"] and (d.kind, d.reason) == ("halt", "evidence_unwritable")
    assert h.assist(uid, type="tool", tool="echo").reason == "evidence_unwritable"
    restarted = h.restart()
    assert [r["payload"]["outcome"] for r in restarted.k.records(uid) if r["kind"] == "receipt"] == ["unknown"]


# --- F-17: evidence integrity -----------------------------------------------------------

def test_f17_the_log_is_one_hash_chain(tmp_path):
    h = Harness(tmp_path)
    h.at_evidence()
    records = h.k.records()
    assert [r["seq"] for r in records] == list(range(1, len(records) + 1))
    assert all(b["prev_hash"] == a["hash"] for a, b in zip(records, records[1:]))


@pytest.mark.parametrize("tamper", ["delete_line", "edit_payload", "reorder"])
def test_f17_tampered_log_halts_the_kernel(tmp_path, tamper):
    h = Harness(tmp_path)
    uid = h.at_evidence()
    rows = lines(h)
    if tamper == "delete_line":
        rows = rows[:1] + rows[2:]
    elif tamper == "edit_payload":
        rec = json.loads(rows[1]); rec["payload"]["principal"] = "forged"; rows[1] = json.dumps(rec, sort_keys=True)
    else:
        rows[1], rows[2] = rows[2], rows[1]
    write_lines(h, rows)
    assert (h.assist(uid, type="tool", tool="echo").kind, h.k._fatal["reason"]) == ("halt", "evidence_tampered")
    assert h.accept(uid).kind == "halt"
    assert h.restart().assist(uid, type="tool", tool="echo").reason == "evidence_tampered"


def test_f17_a_halted_kernel_writes_one_halt_record_then_nothing(tmp_path):
    h = Harness(tmp_path)
    uid = h.at_evidence()
    rows = lines(h)
    rec = json.loads(rows[0]); rec["payload"]["principal"] = "forged"; rows[0] = json.dumps(rec, sort_keys=True)
    write_lines(h, rows)
    h.assist(uid, type="tool", tool="echo")
    after_first = lines(h)
    assert len(after_first) == len(rows) + 1 and json.loads(after_first[-1])["kind"] == "halt"
    h.accept(uid); h.challenge(uid, "x"); h.restart().assist(uid, type="tool", tool="echo")
    assert lines(h) == after_first


def test_f17_halt_persists_in_process_after_the_log_is_restored(tmp_path):
    h = Harness(tmp_path)
    uid = h.at_evidence()
    original = h.k.log.path.read_text()
    rows = lines(h)
    rows[1], rows[2] = rows[2], rows[1]
    write_lines(h, rows)
    assert h.assist(uid, type="tool", tool="echo").kind == "halt"
    h.k.log.path.write_text(original)
    assert h.assist(uid, type="tool", tool="echo").kind == "halt"


def test_f17_with_an_anchor_the_halt_survives_restore_and_restart(tmp_path):
    h = Harness(tmp_path / "data", anchor=tmp_path / "anchor" / "head.json")
    uid = h.at_evidence()
    original = h.k.log.path.read_text()
    rows = lines(h)
    rows[1], rows[2] = rows[2], rows[1]
    write_lines(h, rows)
    assert h.assist(uid, type="tool", tool="echo").kind == "halt"
    h.k.log.path.write_text(original)
    assert h.restart().assist(uid, type="tool", tool="echo").reason == "evidence_tampered"


def test_f17_anchor_detects_truncation(tmp_path):
    h = Harness(tmp_path / "data", anchor=tmp_path / "anchor" / "head.json")
    uid = h.at_evidence()
    write_lines(h, lines(h)[:-1])
    assert h.restart().assist(uid, type="tool", tool="echo").reason == "evidence_tampered"


def _recompute(h, edit):
    records = [json.loads(r) for r in lines(h)]
    edit(records)
    prev = audit_chain.ZERO
    for rec in records:
        rec["prev_hash"] = prev
        rec["hash"] = audit_chain.record_hash(rec)
        prev = rec["hash"]
    write_lines(h, [json.dumps(r, sort_keys=True) for r in records])


def _edit_receipt(records):
    receipt = next(r for r in records if r["kind"] == "receipt")
    receipt["payload"]["receipt"] = {"echo": "forged"}


def test_f17_recomputed_chain_is_detected_with_an_anchor(tmp_path):
    h = Harness(tmp_path / "data", anchor=tmp_path / "anchor" / "head.json")
    uid = h.at_evidence()
    _recompute(h, _edit_receipt)
    assert h.restart().assist(uid, type="tool", tool="echo").reason == "evidence_tampered"


def test_f17_without_an_anchor_unsigned_evidence_can_be_recomputed(tmp_path):
    """Documents the stated limit (SPEC §8): unanchored truncation, and recomputation of
    records that carry no signature, are invisible to a restarted kernel."""
    h = Harness(tmp_path)
    uid = h.at_evidence()
    _recompute(h, _edit_receipt)
    assert h.restart().assist(uid, type="tool", tool="echo").kind == "allow"
    write_lines(h, lines(h)[:-2])
    assert h.restart().assist(uid, type="tool", tool="echo").kind == "allow"


def test_f17_even_without_an_anchor_a_recomputed_signed_record_is_detected(tmp_path):
    h = Harness(tmp_path)
    uid = h.at_evidence()

    def retarget(records):
        advance = next(r for r in records if r["actor"] == "operator" and r["kind"] == "act"
                       and r["payload"]["action"]["type"] == "advance")
        advance["payload"]["action"]["to"] = "run"
    _recompute(h, retarget)
    assert h.restart().assist(uid, type="tool", tool="echo").reason == "invalid_record"


@pytest.mark.parametrize("change", ["recompute", "truncate"])
def test_f17_a_running_kernel_detects_a_changed_prefix_without_an_anchor(tmp_path, change):
    h = Harness(tmp_path)
    uid = h.at_evidence()
    if change == "recompute":
        _recompute(h, _edit_receipt)
    else:
        write_lines(h, lines(h)[:-1])
    assert h.assist(uid, type="tool", tool="echo").reason == "evidence_rewritten"


def test_a_crash_truncated_tail_is_repaired_not_halted(tmp_path):
    h = Harness(tmp_path)
    uid = h.at_evidence()
    with open(h.k.log.path, "ab") as f:
        f.write(b'{"kind": "act", "unit_')
    assert h.restart().assist(uid, type="tool", tool="echo").kind == "allow"
    assert any(r["kind"] == "repair" for r in h.k.records())


# --- Release blocker 1: anchor faults halt; they never raise ---------------------------

def test_blocker1_an_unreadable_anchor_halts_instead_of_raising(tmp_path):
    anchor = tmp_path / "anchor" / "head.json"
    h = Harness(tmp_path / "data", anchor=anchor)
    uid = h.at_evidence()
    anchor.write_text("{not json")
    restarted = h.restart()
    assert restarted.assist(uid, type="tool", tool="echo").reason == "anchor_unreadable"


def test_blocker1_an_unwritable_anchor_halts_until_the_operator_clears_it(tmp_path):
    anchor = tmp_path / "anchor" / "head.json"
    h = Harness(tmp_path / "data", anchor=anchor)
    uid = h.at_unit()
    blocker = tmp_path / "anchor" / "head.json.tmp"
    blocker.mkdir()
    d = h.assist(uid, type="tool", tool="echo")
    assert (d.kind, d.reason) == ("halt", "anchor_unwritable")
    assert [r["payload"]["outcome"] for r in h.k.records(uid) if r["kind"] == "receipt"] == ["not_executed"]
    assert h.restart().assist(uid, type="tool", tool="echo").reason == "anchor_unwritable"
    blocker.rmdir()
    assert h.k.clear_halt().payload == {"authorization": "missing"}
    assert h.clear_halt().kind == "cleared"
    assert h.assist(uid, type="tool", tool="echo").kind == "allow"
    assert h.restart().assist(uid, type="tool", tool="echo").kind == "allow"


# --- F-19 (promoted): units persist; kernels sharing a log see each other's commits ----

def test_f19_units_survive_restart(tmp_path):
    h = Harness(tmp_path)
    uid = h.open("probe")
    restarted = h.restart()
    assert restarted.op(uid, ADVANCE).kind == "advanced"


def test_f19_kernels_sharing_a_log_decide_against_each_others_commits(tmp_path):
    first = Harness(tmp_path)
    uid = first.at_evidence()
    second = first.restart()
    assert second.challenge(uid, "gap").kind == "challenged"
    assert first.accept(uid).reason == "blocked_by_advisor"
    assert first.waive(uid, "accepted risk").kind == "waived"
    assert second.accept(uid).kind == "accepted"
    assert first.assist(uid, type="accept").reason == "not_operator"
    assert first.unit(uid).acceptance is not None


def test_a_failing_tool_is_recorded_and_denied(tmp_path):
    def broken(args):
        raise RuntimeError("tool down")
    h = Harness(tmp_path, tools={**default_tools(), "echo": ToolSpec("echo", broken)})
    uid = h.at_unit()
    d = h.assist(uid, type="tool", tool="echo")
    assert (d.kind, d.reason) == ("deny", "tool_failed")
    receipt = [r for r in h.k.records(uid) if r["kind"] == "receipt"][-1]
    assert "tool down" in receipt["payload"]["error"]


# --- P1: known gaps, tracked ----------------------------------------------------------

@pytest.mark.xfail(strict=True, reason="F-08/R-08: Mission scope is two-way substring containment")
def test_f08_mission_scope_rejects_non_scope_targets(tmp_path):
    h = Harness(tmp_path)
    uid = h.at_unit()
    kinds = [h.assist(uid, type="tool", tool="echo", target=t).kind for t in ("i", "internal-drafts/../prod-release")]
    assert kinds == ["deny", "deny"]


@pytest.mark.xfail(strict=True, reason="F-18/R-18: run -> evidence accepts note/proposal records")
def test_f18_evidence_gate_requires_a_receipt(tmp_path):
    h = Harness(tmp_path)
    uid = h.at_unit()
    h.op(uid, Action(type="advance", to="run"))
    assert h.assist(uid, type="advance", to="evidence").kind != "advanced"


@pytest.mark.xfail(strict=True, reason="F-20/R-11: Assistant-authored durable decisions need an Operator act")
def test_f20_assistant_durable_decision_requires_operator(tmp_path):
    h = Harness(tmp_path)
    uid = h.at_evidence()
    h.accept(uid)
    d = h.assist(uid, type="memory_write", memory_kind="decision", args={"x": 1})
    assert d.kind != "allow"
