# Interfaces baseline

The interfaces the system actually exposes today, and the one it has
committed to build. An interface listed here exists and can be
exercised; prospective entries are marked as such. Written under
WP-MXK-0015 step 3; the accuracy gate applies.

## 1. Kernel API (implemented)

The enforcement core exposes a Python API (SPEC §7,
`05-mxm-construct/means/enforcement/SPEC.md`) through which principals
propose acts and the kernel decides: Allow, Deny, Confirm, Halt (see
`02-systems-baseline/2.3-behavior/`). Invalid arguments raise; the MCP
layer reports them as refused tool calls. Operator and Advisor acts
cross this boundary only with signed, act-bound authorizations.

## 2. MCP interface (implemented)

`05-mxm-construct/means/mcp/` ships a dependency-free MCP framework
(standard library, stdio transport; ADR-MXK-0002) with a server entry
point (`mxm_mcp_server.py`), kernel tools, and delegation binding: a
tool result carries the identity and authorization it was produced
under. The MCP framework ships inside the kernel release. Registering
it with a given engine is harness-side configuration, not part of
this interface.

## 3. Session tooling interface (implemented)

`05-mxm-construct/means/scripts/` is how an operator or aide drives a
session in this repository, run from the repository root:

- `session-start.py`: prints the briefing (posture, profile, memory
  index, Git status).
- `aide.py`: `start`, `verify` (structural contract; nonzero on
  failure), `wrap` (verification plus a clean-tree requirement),
  `remember` (retain a candidate note with timestamp, source, and
  id; candidates are not accepted facts).
- `session-wrap.py`: the wrap entry point used at handoff.

## 4. Vendoring boundary (implemented)

The interface between this repository and every harness that consumes
the kernel (ADR-MXK-0001):

- `release.py build`: produces a release tree and
  `release-manifest.json` (per-file SHA-256 plus an aggregate pin).
- `release.py verify`: offline, fail-closed; integrity, containment
  (standard library only), conformance, in that order.
- `release.py install --expect AGGREGATE`: refuses an unverified or
  wrongly pinned release, copies, re-verifies in place, and writes
  `mxm-kernel.lock.json` in the harness.
- `release.json`: names the release paths, conformance suites,
  minimum Python, and platform.

## 5. Bootstrap and discovery interface (implemented)

How a fresh session finds the construct: `CLAUDE.md` (Claude Code
discovery) imports `AGENTS.md` (the cross-harness adapter), which
routes to `MXM.md`, the canonical bootstrap, and to the always-loaded
surfaces in `05-mxm-construct/meta-harness/`. The arrangement is
decided (ADR-MXM-0002): adapters are minimal and MXM.md is the
source. Structural verification checks this contract; only a fresh
session proves it.

## 6. Core API and contracts (prospective, not implemented)

ADR-MXM-0002 commits the fabric to a headless core API under
`05-mxm-construct/mxm-core/`, with versioned schemas in
`mxm-contracts/`, transport-independent: stdio JSON-RPC and HTTP as
adapters over one service layer. This is WP-MXK-0014 phases 2-3. No
part of it exists yet; when the contracts land, this baseline will
describe them and point to `mxm-contracts/` as their home, rather
than duplicating schema content here.

Human-Curated, AI-Enabled (HCAE)
