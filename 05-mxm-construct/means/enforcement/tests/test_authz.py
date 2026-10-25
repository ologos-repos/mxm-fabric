"""Authorization format limits (WP-MXK-0006): the signing serialization's value domain and
trust-registry key validation."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mxm_testing import OPERATOR, make_trust  # noqa: E402
from mxm import ed25519  # noqa: E402
from mxm.authz import Trust, canonical, check  # noqa: E402


@pytest.mark.parametrize("value", [1.5, float("nan"), float("inf"), 2**53, {1: "x"}, {"k": {3.0}}, b"x"])
def test_values_outside_the_signing_domain_cannot_be_signed(value):
    with pytest.raises(ValueError):
        canonical({"act": value})
    with pytest.raises(ValueError):
        OPERATOR.authorize("u", {"args": value}, "pin")


def test_the_signing_serialization_is_fixed():
    assert canonical({"b": [1, None, True], "a": "é"}) == '{"a":"é","b":[1,null,true]}'.encode("utf-8")


def test_an_envelope_outside_the_domain_is_malformed_not_an_error():
    env = OPERATOR.authorize("u", {"type": "accept"}, "pin")
    env["body"]["act"] = {"type": "accept", "weight": 0.5}
    principal, problem = check(env, make_trust(), role="operator", unit_id="u", act={"type": "accept"},
                               pin="pin", seq=1)
    assert (principal, problem) == (None, "malformed")


def test_the_trust_registry_refuses_weak_keys():
    identity = int.to_bytes(1, 32, "little").hex()
    pk = ed25519.public_key(bytes(range(32)))
    mixed = ed25519._compress(ed25519._add(ed25519._decompress(pk), (0, ed25519.P - 1, 1, 0))).hex()
    for weak in (identity, mixed, "00" * 31):
        with pytest.raises(ValueError):
            Trust.from_entries([{"key_id": "k", "role": "operator", "principal": "p", "public_key": weak}])
