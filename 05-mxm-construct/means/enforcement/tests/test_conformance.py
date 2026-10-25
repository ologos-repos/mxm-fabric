"""SPEC §11 conformance through the signed ports (WP-MXK-0005).

Each test names the SPEC item it proves; TRACEABILITY.md maps the SPEC to these tests.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mxm_testing import Harness  # noqa: E402
from mxm.types import Action  # noqa: E402


@pytest.fixture
def booted(tmp_path):
    def boot(ad_hoc=True, unit_type="generic"):
        h = Harness(tmp_path)
        return h, h.at_unit("pkg-1", scope="internal-drafts", unit_type=unit_type, ad_hoc=ad_hoc)
    return boot


def to_evidence(h, uid):
    h.assist(uid, type="tool", tool="echo", args={"text": "x"})
    return h.assist(uid, type="advance", to="evidence")


def test_s11_1_assistant_cannot_send(booted):
    h, uid = booted()
    d = h.assist(uid, type="tool", tool="send_email", effect="send", channel="email")
    assert d.kind == "deny"


def test_s11_2_assistant_cannot_accept(booted):
    h, uid = booted()
    to_evidence(h, uid)
    d = h.assist(uid, type="accept")
    assert (d.kind, d.reason) == ("deny", "not_operator")


def test_s11_3_challenge_blocks_acceptance_until_operator_waives(booted):
    h, uid = booted()
    to_evidence(h, uid)
    assert h.challenge(uid, "incomplete evidence").kind == "challenged"
    d = h.accept(uid)
    assert (d.kind, d.reason) == ("deny", "blocked_by_advisor")
    assert h.waive(uid, "risk understood").kind == "waived"
    assert h.accept(uid).kind == "accepted"


def test_s11_4_pin_mismatch_halts(booted):
    h, uid = booted()
    object.__setattr__(h.k.constitution, "mind", h.k.constitution.mind + "\nTAMPER")
    d = h.assist(uid, type="tool", tool="echo")
    assert (d.kind, d.reason) == ("halt", "constitution_mismatch")


def test_s11_5_disposition_flushes_scratch_keeps_durable(booted):
    h, uid = booted()
    to_evidence(h, uid)
    h.accept(uid)
    h.assist(uid, type="memory_write", memory_kind="scratch", args={"note": "tmp"})
    h.assist(uid, type="memory_write", memory_kind="decision", args={"choice": "keep"})
    h.op(uid, Action(type="advance", to="integration"))
    assert h.op(uid, Action(type="advance", to="disposition")).kind == "advanced"
    kinds = {row["kind"] for row in h.k.memory.load(uid)}
    assert {"decision", "acceptance"} <= kinds and "scratch" not in kinds


def test_s11_6_attribution_is_kernel_applied(booted):
    h, uid = booted()
    d = h.assist(uid, type="tool", tool="echo", args={"text": "x"})
    assert d.payload["attribution"] == "Human-Curated, AI-Enabled"


def test_s11_7_advisor_cannot_use_privileged_tool(booted):
    h, uid = booted()
    d = h.adv(uid, Action(type="tool", tool="send_email", effect="send"))
    assert d.kind == "deny"


def test_s11_8_required_method_blocks_freeform(tmp_path):
    h = Harness(tmp_path)
    h.k.methods.register("001_echo_draft", "draft", lambda args: {"ok": True})
    uid = h.at_unit("pkg-2", unit_type="draft", ad_hoc=False)
    d = h.assist(uid, type="tool", tool="echo")
    assert (d.kind, d.reason) == ("deny", "method_required")
    d2 = h.assist(uid, type="method_run", method_id="001_echo_draft", args={"text": "hi"})
    assert d2.kind == "allow"


def test_happy_path(booted):
    h, uid = booted()
    assert h.assist(uid, type="tool", tool="echo", args={"text": "hello"}).kind == "allow"
    assert h.assist(uid, type="advance", to="evidence").kind == "advanced"
    assert h.accept(uid).kind == "accepted"
    assert h.op(uid, Action(type="advance", to="integration")).kind == "advanced"
    assert h.op(uid, Action(type="advance", to="disposition")).kind == "advanced"
    assert h.unit(uid).state == "disposition"


def test_open_package_returns_a_decision_and_the_signed_unit_id(tmp_path):
    h = Harness(tmp_path)
    uid = h.open("pkg-3", scope="internal-drafts")
    unit = h.unit(uid)
    assert (unit.package_id, unit.scope, unit.state, unit.pin) == ("pkg-3", "internal-drafts", "package", h.k.constitution.pin())


def test_every_act_is_one_chained_record_in_one_log(booted):
    h, uid = booted()
    to_evidence(h, uid)
    h.accept(uid)
    records = h.k.records()
    assert [r["seq"] for r in records] == list(range(1, len(records) + 1))
    assert all(b["prev_hash"] == a["hash"] for a, b in zip(records, records[1:]))
    acts = [r for r in records if r["kind"] == "act" and r["unit_id"] == uid]
    assert [r["payload"]["action"]["type"] for r in acts] == ["open_package", "advance", "tool", "advance", "accept"]
    operator_acts = [r for r in acts if r["actor"] == "operator"]
    assert all(r["payload"]["principal"] == "operator-under-test" for r in operator_acts)
    assert all(r["payload"]["authorization"]["body"]["unit_id"] == uid for r in operator_acts)


def test_principal_cli_issues_signed_acts_from_its_own_process(tmp_path):
    import json
    import os
    import subprocess
    cli = Path(__file__).resolve().parents[1] / "mxm_principal.py"
    const = Path(__file__).resolve().parents[1] / "constitutions" / "default.json"
    trust, key, data = tmp_path / "trust.json", tmp_path / "op.key", tmp_path / "data"

    def run(*argv):
        return subprocess.run([sys.executable, "-I", "-S", str(cli), *map(str, argv)], capture_output=True, text=True)

    made = run("keygen", "--key-id", "jd-1", "--role", "operator", "--principal", "jd", "--key-out", key, "--trust", trust)
    assert made.returncode == 0, made.stderr
    assert os.stat(key).st_mode & 0o777 == 0o600
    assert run("keygen", "--key-id", "jd-1", "--role", "operator", "--principal", "jd",
               "--key-out", tmp_path / "again.key", "--trust", trust).returncode == 2
    base = ("act", "--key", key, "--constitution", const, "--data-root", data, "--trust", trust)
    opened = json.loads(run(*base, "open", "pkg", "--scope", "internal-drafts").stdout)
    assert opened["kind"] == "opened"
    advanced = run(*base, "advance", opened["unit_id"], "unit")
    assert advanced.returncode == 0 and json.loads(advanced.stdout)["kind"] == "advanced"
    records = [json.loads(line) for line in (data / "events.jsonl").read_text().splitlines()]
    assert [r["payload"]["principal"] for r in records] == ["jd", "jd"]
