#!/usr/bin/env python3
"""Launch the MxM kernel MCP server on stdio (ADR-MXK-0002, ADR-MXK-0003).

    mxm_mcp_server.py --delegation DELEGATION.json --constitution CONSTITUTION.json \
        --data-root DIR --trust TRUST.json [--anchor HEAD.json]

An engine registers this command as a stdio MCP server. The server exposes only the
Assistant port. The kernel still replays the shared event log, including the Operator's and
Advisor's signed acts, so it needs the same trust registry (public keys only) and anchor as
every other kernel on DIR. It never holds a signing key, so no Operator or Advisor act can
originate here. WorkUnits are opened by the Operator's own surface, in its own process.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(_HERE), str(_HERE.parent / "enforcement")]

from mxm.authz import Trust  # noqa: E402
from mxm.constitution import Constitution  # noqa: E402
from mxm.kernel import Kernel  # noqa: E402
from mxm_mcp.delegation import Delegation  # noqa: E402
from mxm_mcp.kernel_tools import bind  # noqa: E402
from mxm_mcp.server import Server  # noqa: E402

VERSION = "0.2.0-dev"


def build(delegation_path, constitution_path, data_root, trust_path, anchor_path=None) -> Server:
    delegation = Delegation.load(delegation_path) if delegation_path else None
    kernel = Kernel(Constitution.load(constitution_path), data_root, trust=Trust.load(trust_path),
                    anchor_path=anchor_path)
    return bind(Server("mxm-kernel", VERSION, delegation), kernel)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--delegation", type=Path, help="delegation JSON; without it every tool call is refused")
    ap.add_argument("--constitution", type=Path, required=True)
    ap.add_argument("--data-root", type=Path, required=True)
    ap.add_argument("--trust", type=Path, required=True, help="trust registry: Operator/Advisor public keys")
    ap.add_argument("--anchor", type=Path, help="log head anchor; must not be engine-writable")
    args = ap.parse_args(argv)
    build(args.delegation, args.constitution, args.data_root, args.trust, args.anchor).serve()
    return 0


if __name__ == "__main__":
    sys.exit(main())
