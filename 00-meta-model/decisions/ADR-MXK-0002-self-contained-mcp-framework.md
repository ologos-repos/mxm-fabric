# ADR-MXK-0002 — Self-contained MCP framework

- **Status:** Decided
- **Work package:** `04-work-packages/WP-MXK-0004-mcp-framework/`

## Context

The reference deployment integrates several code assistants and models, so the kernel cannot reach an engine
through any one vendor's hooks. The Model Context Protocol (MCP) is the engine-neutral
surface they share. Every standalone meta-harness must carry its own MCP framework, because
air-gapped ones cannot install the official SDK. The same framework is also how MxM
federates: a subagent inherits the constitution and only a narrowed slice of its parent's
authority.

## Decision

1. **A standard-library MCP server ships in the release.** `mxm_mcp` implements stdio
   transport as newline-delimited JSON-RPC 2.0, with `initialize`, `notifications/initialized`,
   `ping`, `tools/list` and `tools/call`. It negotiates protocol versions 2025-06-18,
   2025-03-26 and 2024-11-05, and answers every other method "method not found". It is named
   `mxm_mcp` so it never shadows the official `mcp` package where one is installed.
2. **Only the Assistant's side of the kernel is exposed.** Two tools are registered:
   `mxm_posture` (the pinned constitution) and `mxm_propose` (the Assistant port,
   `assistant_propose`). Operator and Advisor acts are never registered as tools. No
   message an engine sends can reach them, and any `actor` field in a proposal is ignored.
3. **Every server runs under a delegation, fixed at launch.** A delegation names the tools
   and WorkUnits it permits. The host supplies it as a file; no protocol message can change
   it. `tools/list` shows only permitted tools. A call outside the delegation, or any call on a
   server with no delegation, is refused as a tool error.
4. **Delegation only narrows.** `Delegation.narrow` derives a child for a subagent and
   raises if the child asks for any tool or unit its parent lacks. This is the mechanical form
   of "authority flows down".
5. **The MCP suite is a release conformance suite.** A vendored harness verifies the MCP
   layer offline like the rest of the kernel. The suite includes a stdio round trip through
   the launched server in isolated mode (`python -I -S`).

## Consequences

- Any MCP-capable engine can run under the kernel with no vendor-specific adapter, and with
  no network or third-party package.
- The model-facing surface is exactly two tools. Growing it is an ADR-level change.
- Known limit: units live in process memory until the transactional event log lands (roadmap
  step 5). Until then a launched server only knows units its own host process opened. A
  standalone server therefore denies every proposal as `unknown_unit`. The framework is
  proven; it is not yet usable for real work across processes.
- Not decided here: registering the server with any engine (a harness-side change), MCP
  resources or prompts, and returning evidence from subagents as run-bound candidates
  (roadmap step 6).

Human-Curated, AI-Enabled (HCAE)
