#!/usr/bin/env python3
"""Issue Operator and Advisor acts from the principal's own process (ADR-MXK-0003).

    mxm_principal.py keygen --key-id ID --role operator|advisor --principal NAME \
        --key-out KEY.json --trust TRUST.json
    mxm_principal.py act --key KEY.json --constitution C.json --data-root DIR \
        --trust TRUST.json [--anchor HEAD.json] COMMAND ...

``keygen`` writes a new secret key file (mode 0600, refusing to overwrite) and adds its
public key to the trust registry, creating the registry if needed. ``act`` signs one
authorization for exactly one act and submits it to the kernel on DIR; the secret never
leaves this process. Run both as the principal, never as the engine's account. Commands:

    open PACKAGE [--scope S] [--unit-type T] [--ad-hoc]
    advance UNIT STATE | accept UNIT | abort UNIT | waive UNIT NOTE        (Operator)
    challenge UNIT NOTE | clear-challenge UNIT                             (Advisor)
    clear-halt                                                             (Operator)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mxm.authz import ROLES, Signer, Trust, act_of  # noqa: E402
from mxm.constitution import Constitution  # noqa: E402
from mxm.kernel import Kernel  # noqa: E402
from mxm.types import Action  # noqa: E402


def keygen(args) -> int:
    registry = json.loads(args.trust.read_text()) if args.trust.exists() else {"keys": []}
    if any(e.get("key_id") == args.key_id for e in registry["keys"]):
        print(f"key id {args.key_id!r} is already in {args.trust}", file=sys.stderr)
        return 2
    secret = os.urandom(32)
    signer = Signer(args.key_id, args.role, secret)
    fd = os.open(args.key_out, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump({"key_id": args.key_id, "role": args.role, "principal": args.principal, "secret": secret.hex()}, f)
    entry = signer.trust_entry(args.principal)
    registry["keys"].append(entry)
    Trust.from_entries(registry["keys"])  # refuse to write an invalid registry
    args.trust.write_text(json.dumps(registry, indent=2) + "\n")
    print(json.dumps(entry))
    return 0


def _action(args) -> Action:
    return {"advance": lambda: Action(type="advance", to=args.state),
            "accept": lambda: Action(type="accept", operator_ok=True),
            "abort": lambda: Action(type="abort", operator_ok=True),
            "waive": lambda: Action(type="waive_challenge", operator_ok=True, note=args.note),
            "challenge": lambda: Action(type="challenge", note=args.note),
            "clear-challenge": lambda: Action(type="clear_challenge")}[args.command]()


def act(args) -> int:
    key = json.loads(args.key.read_text())
    signer = Signer(key["key_id"], key["role"], bytes.fromhex(key["secret"]))
    kernel = Kernel(Constitution.load(args.constitution), args.data_root, trust=Trust.load(args.trust),
                    anchor_path=args.anchor)
    if args.command == "open":
        unit_id = uuid.uuid4().hex
        auth = signer.authorize(unit_id, kernel.opening_act(args.package, args.scope, args.unit_type, args.ad_hoc),
                                kernel.constitution.pin())
        decision = kernel.open_package(args.package, auth, args.scope, args.unit_type, args.ad_hoc)
    elif args.command == "clear-halt":
        decision = kernel.clear_halt(signer.authorize(None, act_of(Action(type="clear_halt")), None))
    else:
        action = _action(args)
        unit = kernel.units.get(args.unit)
        auth = signer.authorize(args.unit, act_of(action), unit.pin if unit else kernel.constitution.pin())
        port = kernel.operator_propose if signer.role == "operator" else kernel.advisor_propose
        decision = port(args.unit, action, auth)
    print(json.dumps(asdict(decision), default=str))
    return 0 if decision.ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="verb", required=True)
    kg = sub.add_parser("keygen")
    kg.add_argument("--key-id", required=True)
    kg.add_argument("--role", choices=ROLES, required=True)
    kg.add_argument("--principal", required=True)
    kg.add_argument("--key-out", type=Path, required=True)
    kg.add_argument("--trust", type=Path, required=True)
    ac = sub.add_parser("act")
    ac.add_argument("--key", type=Path, required=True)
    ac.add_argument("--constitution", type=Path, required=True)
    ac.add_argument("--data-root", type=Path, required=True)
    ac.add_argument("--trust", type=Path, required=True)
    ac.add_argument("--anchor", type=Path)
    cmd = ac.add_subparsers(dest="command", required=True)
    op = cmd.add_parser("open")
    op.add_argument("package")
    op.add_argument("--scope")
    op.add_argument("--unit-type", default="generic")
    op.add_argument("--ad-hoc", action="store_true")
    for name, extra in (("advance", "state"), ("accept", None), ("abort", None), ("waive", "note"),
                        ("challenge", "note"), ("clear-challenge", None)):
        p = cmd.add_parser(name)
        p.add_argument("unit")
        if extra:
            p.add_argument(extra)
    cmd.add_parser("clear-halt")
    args = ap.parse_args(argv)
    return keygen(args) if args.verb == "keygen" else act(args)


if __name__ == "__main__":
    sys.exit(main())
