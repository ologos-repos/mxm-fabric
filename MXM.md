# MXM.md — canonical MxM bootstrap (mxm-fabric)

## Profile

| Field | Value |
|---|---|
| Profile | `mxm-fabric`, version `0.2.0` |
| Repository-class | Meta-Harness |
| Construct root | `05-mxm-construct/` |

## The six surfaces

| Surface | Answers | File | Loading |
|---|---|---|---|
| Mind | How I reason | [Mind](05-mxm-construct/meta-harness/mind.md) | Always-loaded |
| Morals | What's obligatory | [Morals](05-mxm-construct/meta-harness/morals.md) | Always-loaded |
| Mission | Identity and purpose | [Mission](05-mxm-construct/meta-harness/mission.md) | Always-loaded |
| Memory | What persists | [Memory](05-mxm-construct/meta-harness/memory.md) | Pointer-shaped; read on need |
| Methods | How work is done, across all disciplined practice | [Methods](05-mxm-construct/meta-harness/methods.md) | Pointer-shaped; read on need |
| Means | What executes | [Means](05-mxm-construct/means/README.md) | Pointer-shaped; read on need |

## Loading rules

Always-loaded is the required session posture. Claude resolves the imports in
its adapter; Codex must explicitly read the same files before substantive work.
Reload after compaction. Structural verification cannot prove a model obeyed
or retained these instructions; fresh-session validation remains necessary.
Memory, Methods and Means are separate pointer-shaped surfaces read on need.

## Harness adapters

| Harness | Entry | Mechanism |
|---|---|---|
| Claude Code | CLAUDE.md | Imports AGENTS.md, then mission.md, mind.md and morals.md |
| Codex and other CLIs | AGENTS.md | Explicit reads of required posture and MXM.md |

Native harness histories preserve session state. Validated canonical memory
owns durable semantic claims; no live native-memory adapter is installed here.

## Memory and Means

[Memory contract](05-mxm-construct/meta-harness/memory.md) routes to the durable
store. [Means](05-mxm-construct/means/README.md) routes to executable tools.
Start: `python 05-mxm-construct/means/scripts/session-start.py`.
Wrap: `python 05-mxm-construct/means/scripts/session-wrap.py`.
Significant work uses a dedicated branch and Git worktree.

## Repository-local routing

Sysops belongs in this repository; DevOps product artifacts belong in their
product repository. Shared-host infra requires verified ownership and authority.
`00`–`04` contain baselines and work packages, `05-mxm-construct/` contains the
aide, `06-operations/` contains operating guidance. Root MEMORY.md is the
operational index. Repo decisions and optional profiles live inside 00-meta-model.

## Conformance gate

`python 00-meta-model/verify-repository-layout.py` enforces the closed root,
required baseline files, canonical surface locations and bootstrap chain.
The session verifier invokes it. Tests inject wrong roots, shadow contracts,
missing operations and broken adapters. This is structural conformance to the
portable MxM layout, not a claim to ship all MxM runtime enforcement.
