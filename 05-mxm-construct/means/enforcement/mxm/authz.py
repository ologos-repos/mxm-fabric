"""Signed, single-use, act-bound authorizations for Operator and Advisor acts (ADR-MXK-0003).

An authorization is ``{"body": {...}, "sig": hex}``. The body names one act and nothing else:

    v           1
    id          unique; an authorization is spent the first time the kernel records it
    key_id      a key in the kernel's trust registry
    role        "operator" | "advisor"; must match the key's role and the port
    unit_id     the WorkUnit the act is for (for open_package: the id the new unit gets;
                null for kernel-scope acts)
    act         the proposed action without its actor, exactly as the port receives it
    pin         the constitution pin the act is issued under (the unit's pin)
    issued_at, expires_at   ISO-8601 with a timezone

``sig`` is Ed25519 over ``DOMAIN + canonical(body)``. ``canonical`` is the MxM signing
serialization, not a general canonical-JSON scheme: values are restricted to objects with
string keys, arrays, strings, booleans, null and integers of magnitude below 2**53 (no
floats, no NaN or infinities); objects are emitted with keys sorted by Unicode code point,
no insignificant whitespace, and UTF-8 without escaping. Anything outside that domain
cannot be signed or verified. The kernel holds only public keys (the trust registry), so
nothing that can read the kernel's files can mint authority.
"""
from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable, Optional

from . import ed25519

DOMAIN = b"mxm-authorization-v1\n"
ROLES = ("operator", "advisor")
CLOCK_SKEW = timedelta(seconds=60)


MAX_INT = 2**53


def _in_domain(obj: Any) -> None:
    if obj is None or isinstance(obj, (bool, str)):
        return
    if isinstance(obj, int):
        if abs(obj) >= MAX_INT:
            raise ValueError("integer outside the signing domain")
        return
    if isinstance(obj, (list, tuple)):
        for item in obj:
            _in_domain(item)
        return
    if isinstance(obj, dict):
        for key, value in obj.items():
            if not isinstance(key, str):
                raise ValueError("object key is not a string")
            _in_domain(value)
        return
    raise ValueError(f"{type(obj).__name__} is outside the signing domain")


def canonical(obj: Any) -> bytes:
    """The MxM signing serialization (see the module docstring). Raises ValueError outside it."""
    _in_domain(obj)
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False).encode("utf-8")


def act_of(action: Any) -> dict:
    """The act an authorization binds: every field of the proposed action except its actor."""
    fields = dict(action.to_dict() if hasattr(action, "to_dict") else action)
    fields.pop("actor", None)
    return fields


def open_act(package_id: str, scope: str, unit_type: str, ad_hoc: bool, method_id: Optional[str],
             constitution_version: str) -> dict:
    """The fully resolved opening. Every field of the new unit is signed; nothing is defaulted
    after signing. ``Kernel.opening_act`` resolves it for a signer to preview."""
    return {"type": "open_package", "package_id": package_id, "scope": scope, "unit_type": unit_type,
            "ad_hoc": ad_hoc, "method_id": method_id, "constitution_version": constitution_version}


@dataclass(frozen=True)
class TrustedKey:
    key_id: str
    role: str
    principal: str
    public: bytes
    valid_through_seq: Optional[int] = None  # retired: valid only for log records up to this seq


class Trust:
    """The public keys the kernel accepts. Operator-owned; must not be engine-writable."""

    def __init__(self, keys: Iterable[TrustedKey] = ()):
        self.keys = {k.key_id: k for k in keys}

    @classmethod
    def from_entries(cls, entries: Iterable[dict]) -> "Trust":
        keys = []
        for e in entries:
            public = bytes.fromhex(e["public_key"])
            through = e.get("valid_through_seq")
            if e["role"] not in ROLES or not ed25519.valid_public_key(public) or not e["key_id"] or not e["principal"] \
                    or not (through is None or (isinstance(through, int) and not isinstance(through, bool))):
                raise ValueError(f"invalid trust entry {e.get('key_id')!r}")
            keys.append(TrustedKey(e["key_id"], e["role"], e["principal"], public, through))
        return cls(keys)

    def entries(self) -> list[dict]:
        return [{"key_id": k.key_id, "role": k.role, "principal": k.principal, "public_key": k.public.hex(),
                 "valid_through_seq": k.valid_through_seq} for k in self.keys.values()]

    @classmethod
    def load(cls, path: str | Path) -> "Trust":
        return cls.from_entries(json.loads(Path(path).read_text(encoding="utf-8"))["keys"])


def _when(value: str) -> datetime:
    ts = datetime.fromisoformat(value)
    if ts.tzinfo is None:
        raise ValueError("timestamp without a timezone")
    return ts


def check(envelope: Any, trust: Trust, *, role: str, unit_id: Optional[str], act: dict,
          pin: Optional[str], seq: int, now: Optional[datetime] = None,
          consumed: Iterable[str] = ()) -> tuple[Optional[str], Optional[str]]:
    """Return (principal, None) when the authorization permits exactly this act, else
    (None, reason). ``now`` is given when deciding; replay omits it, since expiry was
    checked when the act was recorded. ``pin`` None skips the pin binding (kernel scope)."""
    if envelope is None:
        return None, "missing"
    try:
        body, sig = envelope["body"], bytes.fromhex(envelope["sig"])
        auth_id, key_id = body["id"], body["key_id"]
        issued, expires = _when(body["issued_at"]), _when(body["expires_at"])
        if body.get("v") != 1 or not isinstance(auth_id, str) or not auth_id or not isinstance(key_id, str):
            return None, "malformed"
    except (KeyError, TypeError, ValueError, AttributeError):
        return None, "malformed"
    key = trust.keys.get(key_id)
    if key is None:
        return None, "unknown_key"
    if key.role != role or body.get("role") != role:
        return None, "wrong_role"
    if key.valid_through_seq is not None and seq > key.valid_through_seq:
        return None, "key_retired"
    try:
        signed = DOMAIN + canonical(body)
    except (TypeError, ValueError):
        return None, "malformed"
    if not ed25519.verify(key.public, signed, sig):
        return None, "bad_signature"
    if body.get("unit_id") != unit_id:
        return None, "wrong_unit"
    if pin is not None and body.get("pin") != pin:
        return None, "wrong_pin"
    try:
        mismatch = canonical(body.get("act")) != canonical(act)
    except ValueError:
        return None, "malformed"
    if mismatch:
        return None, "act_mismatch"
    if now is not None and not (issued - CLOCK_SKEW <= now <= expires):
        return None, "expired"
    if auth_id in consumed:
        return None, "replayed"
    return key.principal, None


def spent_id(envelope: Any) -> str:
    return envelope["body"]["id"]


class Signer:
    """Issues authorizations. Runs in the Operator's or Advisor's own process, never the engine's."""

    def __init__(self, key_id: str, role: str, secret: bytes):
        if role not in ROLES:
            raise ValueError(f"role must be one of {ROLES}")
        self.key_id, self.role, self._secret = key_id, role, bytes(secret)
        self.public = ed25519.public_key(self._secret)

    @classmethod
    def generate(cls, key_id: str, role: str) -> "Signer":
        return cls(key_id, role, os.urandom(32))

    def trust_entry(self, principal: str) -> dict:
        return {"key_id": self.key_id, "role": self.role, "principal": principal,
                "public_key": self.public.hex(), "valid_through_seq": None}

    def authorize(self, unit_id: Optional[str], act: dict, pin: Optional[str], ttl: int = 300,
                  now: Optional[datetime] = None) -> dict:
        now = now or datetime.now(timezone.utc)
        body = {"v": 1, "id": uuid.uuid4().hex, "key_id": self.key_id, "role": self.role,
                "unit_id": unit_id, "act": act, "pin": pin, "issued_at": now.isoformat(),
                "expires_at": (now + timedelta(seconds=ttl)).isoformat()}
        return {"body": body, "sig": ed25519.sign(self._secret, DOMAIN + canonical(body)).hex()}
