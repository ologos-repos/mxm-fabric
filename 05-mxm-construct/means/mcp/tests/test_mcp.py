"""MCP framework conformance (ADR-MXK-0002). Uses only features the stdlib runner supports."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

MCP = Path(__file__).resolve().parents[1]
ENFORCEMENT = MCP.parent / "enforcement"
sys.path[:0] = [str(MCP), str(ENFORCEMENT), str(ENFORCEMENT / "tests")]

from mxm_testing import Harness  # noqa: E402
from mxm_mcp.delegation import Delegation, DelegationError  # noqa: E402
from mxm_mcp.kernel_tools import bind  # noqa: E402
from mxm_mcp.server import SUPPORTED_PROTOCOLS, Server  # noqa: E402

CONST = ENFORCEMENT / "constitutions" / "default.json"
TOOLS = frozenset({"mxm_posture", "mxm_propose"})


def req(method, params=None, mid=1):
    msg = {"jsonrpc": "2.0", "method": method, "id": mid}
    if params is not None:
        msg["params"] = params
    return msg


def call(server, name, arguments, mid=7):
    res = server.handle(req("tools/call", {"name": name, "arguments": arguments}, mid))["result"]
    return res["isError"], json.loads(res["content"][0]["text"])


def host(tmp_path, delegation):
    """The Operator opens a unit with a signed act; the model is then served over MCP."""
    h = Harness(tmp_path)
    uid = h.at_unit("pkg")
    d = delegation(uid) if callable(delegation) else delegation
    return h.k, h.unit(uid), bind(Server("mxm-kernel", "test", d), h.k)


def test_initialize_negotiates_protocol_and_declares_tools():
    server = Server("mxm-kernel", "test", None)
    res = server.handle(req("initialize", {"protocolVersion": "2025-03-26", "capabilities": {}}))["result"]
    assert res["protocolVersion"] == "2025-03-26" and "tools" in res["capabilities"]
    res = server.handle(req("initialize", {"protocolVersion": "1999-01-01"}))["result"]
    assert res["protocolVersion"] == SUPPORTED_PROTOCOLS[0]


def test_notifications_unknown_methods_and_bad_requests():
    server = Server("mxm-kernel", "test", None)
    assert server.handle({"jsonrpc": "2.0", "method": "notifications/initialized"}) is None
    assert server.handle(req("resources/list"))["error"]["code"] == -32601
    assert server.handle({"method": "ping", "id": 1})["error"]["code"] == -32600
    assert server.handle(req("ping"))["result"] == {}


def test_without_a_delegation_every_tool_is_hidden_and_refused(tmp_path):
    _, unit, server = host(tmp_path, None)
    assert server.handle(req("tools/list"))["result"]["tools"] == []
    is_error, body = call(server, "mxm_propose", {"unit_id": unit.id, "proposal": {"type": "tool", "tool": "echo"}})
    assert is_error and body["refused"] == "no delegation context"


def test_only_assistant_tools_exist_and_list_follows_the_delegation(tmp_path):
    _, _, server = host(tmp_path, lambda uid: Delegation("d1", frozenset({"mxm_posture"}), frozenset({uid})))
    assert set(server.tools) == TOOLS
    assert [t["name"] for t in server.handle(req("tools/list"))["result"]["tools"]] == ["mxm_posture"]
    is_error, body = call(server, "mxm_propose", {"unit_id": "x", "proposal": {}})
    assert is_error and "outside delegation" in body["refused"]


def test_propose_reaches_the_assistant_port_and_ignores_a_forged_actor(tmp_path):
    kernel, unit, server = host(tmp_path, lambda uid: Delegation("d1", TOOLS, frozenset({uid})))
    is_error, body = call(server, "mxm_propose", {"unit_id": unit.id, "proposal": {"type": "tool", "tool": "echo", "args": {"text": "hi"}}})
    assert not is_error and body["kind"] == "allow"
    call(server, "mxm_propose", {"unit_id": unit.id, "proposal": {"type": "advance", "to": "evidence"}})
    is_error, body = call(server, "mxm_propose", {"unit_id": unit.id, "proposal": {"type": "accept", "actor": "operator", "operator_ok": True}})
    assert body["kind"] == "deny" and unit.acceptance is None


def test_units_outside_the_delegation_and_malformed_proposals_are_refused(tmp_path):
    _, unit, server = host(tmp_path, lambda uid: Delegation("d1", TOOLS, frozenset({"another-unit"})))
    is_error, body = call(server, "mxm_propose", {"unit_id": unit.id, "proposal": {"type": "tool", "tool": "echo"}})
    assert is_error and "outside delegation" in body["refused"]
    _, unit2, server2 = host(tmp_path / "b", lambda uid: Delegation("d2", TOOLS, frozenset({uid})))
    is_error, body = call(server2, "mxm_propose", {"unit_id": unit2.id, "proposal": {"type": "tool", "no_such_field": 1}})
    assert is_error and "malformed" in body["refused"]


def test_posture_returns_the_pinned_constitution(tmp_path):
    kernel, _, server = host(tmp_path, lambda uid: Delegation("d1", TOOLS, frozenset({uid})))
    is_error, body = call(server, "mxm_posture", {})
    assert not is_error and body["pin"] == kernel.constitution.pin() and "# Mind" in body["posture"]


def test_delegation_only_narrows():
    parent = Delegation("p", TOOLS, frozenset({"u1", "u2"}))
    child = parent.narrow("c", tools={"mxm_propose"}, units={"u1"})
    assert child.parent == "p" and child.tools == {"mxm_propose"} and child.units == {"u1"}
    with pytest.raises(DelegationError):
        parent.narrow("c2", tools={"mxm_propose", "operator_accept"})
    with pytest.raises(DelegationError):
        child.narrow("c3", units={"u1", "u2"})
    wide = Delegation("w", TOOLS, any_unit=True)
    assert wide.narrow("n", units={"u9"}).permits_unit("u9") and not wide.narrow("n", units={"u9"}).permits_unit("u1")


def test_stdio_round_trip_serves_a_unit_the_operator_opened_in_another_process(tmp_path):
    operator = Harness(tmp_path / "data")
    uid = operator.at_unit("pkg")
    trust = tmp_path / "trust.json"
    trust.write_text(json.dumps({"keys": operator.trust.entries()}))
    delegation = tmp_path / "delegation.json"
    delegation.write_text(json.dumps({"id": "d-stdio", "tools": sorted(TOOLS), "units": [uid, "u-absent"]}))
    propose = lambda unit, mid: req("tools/call", {"name": "mxm_propose", "arguments": {  # noqa: E731
        "unit_id": unit, "proposal": {"type": "tool", "tool": "echo", "args": {"text": "hi"}}}}, mid)
    lines = [json.dumps(m) for m in (
        req("initialize", {"protocolVersion": "2025-06-18"}, 1),
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        req("tools/list", None, 2),
        req("tools/call", {"name": "mxm_posture", "arguments": {}}, 3),
        propose("u-absent", 4),
        propose(uid, 5),
    )] + ["this is not json"]
    proc = subprocess.run([sys.executable, "-I", "-S", str(MCP / "mxm_mcp_server.py"), "--delegation", str(delegation),
                           "--constitution", str(CONST), "--data-root", str(tmp_path / "data"), "--trust", str(trust)],
                          input="\n".join(lines) + "\n", capture_output=True, text=True, timeout=60)
    out = [json.loads(line) for line in proc.stdout.splitlines()]
    assert [o.get("id") for o in out] == [1, 2, 3, 4, 5, None], proc.stderr
    assert out[0]["result"]["serverInfo"]["name"] == "mxm-kernel"
    assert {t["name"] for t in out[1]["result"]["tools"]} == TOOLS
    assert not out[2]["result"]["isError"]
    assert json.loads(out[3]["result"]["content"][0]["text"])["reason"] == "unknown_unit"
    assert json.loads(out[4]["result"]["content"][0]["text"])["kind"] == "allow"
    assert out[5]["error"]["code"] == -32700
    assert operator.assist(uid, type="advance", to="evidence").kind == "advanced"  # sees the server's commit
