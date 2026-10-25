# MxM Fabric — the governance plane for agentic AI ecosystems

MxM Fabric is the governed fabric built on the MxM (multi-mode meta-harness)
kernel: the governance and enforcement layer for agentic AI ecosystems. It
covers the six MxM surfaces (Mind, Morals, Mission, Memory, Methods, Means)
and the MCP framework through which any engine reaches them, and this
repository is the standalone reference implementation and conformance
authority for that layer.

It is for operators and builders running more than one agent under one
authority: anyone who needs to know who authorized an action, what evidence
supports a claim, and who accepted a result, with those answers enforced by
the harness rather than left to convention. This repository is the home of
MxM fabric work; fabric-specific scope is defined in its baselines and work
packages as the work lands.

## Architecture viewpoint

![The MxM framework: the Principal Governance Triad (human operator, AI assistant, AI advisor), the six surfaces split between always-loaded and read-on-need, and the work chain with the Advisor's review gate before acceptance.](02-systems-baseline/2.2-architecture/mxm-explainer/mxm-diagram.png)

The framework laid flat: the Principal Governance Triad, the six surfaces
(Mind, Morals, Mission always loaded; Memory, Methods, Means read on need),
and the work chain, with the Advisor reviewing at Evidence before Acceptance.
![Agentic AI Ecosystem Reference Architecture: a governance and enforcement control plane across the top, six layers from Experience and Interaction down to Infrastructure and Platforms, the Epistemic Assurance Framework beneath them, trusted and accountable outcomes at the bottom, external environment at the left, outcomes and value at the right.](02-systems-baseline/2.2-architecture/agentic-ai-ecosystem-reference-architecture/plate.svg)

The MxM Fabric plate: the ecosystem-level viewpoint, with the reference architecture article and files in [agentic-ai-ecosystem-reference-architecture/](02-systems-baseline/2.2-architecture/agentic-ai-ecosystem-reference-architecture/).

Companion material: the [explainer narrative](02-systems-baseline/2.2-architecture/mxm-explainer/mxm-narrative.md),
the [explainer article](02-systems-baseline/2.2-architecture/mxm-explainer/introducing-mxm.md), and the
[reference architecture](02-systems-baseline/2.2-architecture/MXM-REFERENCE-ARCHITECTURE-0001.md).
Harvested companion essays are in [essays/](02-systems-baseline/2.2-architecture/essays/).
## Publications

The fabric's published record on Zenodo:

- **Governed Execution in Multi-Mode Agent Harnesses: Admission, Authority,
  Memory, Routing, and Closure Patterns (A Mx-Modes Companion)** (2026) — the
  execution-time governance patterns a conformant MxM harness enforces.
  [doi.org/10.5281/zenodo.23367869](https://doi.org/10.5281/zenodo.23367869)
- **Ordinal Systems Architecture: A Control Grammar for Enterprise AI
  Authority** (2026, with Micah Longmire) — the control grammar for enterprise
  AI authority that the SARS operating model and the ecosystem viewpoint draw
  on. [doi.org/10.5281/zenodo.20334233](https://doi.org/10.5281/zenodo.20334233)

## Layout

This repository uses the standard MxM Meta-Harness structure. See [MXM.md](MXM.md), and
[04-work-packages/](04-work-packages/) for bounded delivery records.

## How the kernel in this tree is consumed

**Every meta-harness carries its own self-contained, enforced copy.** A harness adopts a
kernel *release* by vendoring it into its own tree:

- The release is **pinned by hash** in a release manifest.
- The release is **verified offline** by the conformance suite shipped with it, with network
  egress disabled.
- The vendored copy imports and fetches **nothing** from outside the harness, so it works
  in air-gapped environments.
- The **MCP framework ships inside the release**. It is dependency-free: a standard-library
  implementation over stdio, with no third-party SDK.

Authority flows down; evidence flows up. Fixes found in a harness come back as
proposals and ship in a new release. A vendored copy is never edited in place.
## Lineage

**Kernel home (2026-10-23).** This repository is the MxM kernel's home and source of
truth. The former standalone kernel repository is archived and read-only; its code was
byte-identical to this tree's at the move. The Go kernel remains the target
implementation, with the Python kernel here as its pattern source. Kernel releases are
tagged here as `mxm-kernel-vX.Y.Z`; the first is `mxm-kernel-v0.2.0`. Changes land by
pull request on the development process home, where `main` is protected and the CI
suite is a required gate.

Initial tree imported 2026-10-23 (133 files), starting from a full copy of
the kernel. The delivery records
(`04-work-packages/WP-MXK-*`, `00-meta-model/decisions/ADR-MXK-*`) and the
release identity (`mxm-kernel` in `05-mxm-construct/means/release/`) are
retained as historical and component records; living identity surfaces
(this README, MXM.md, the repo description) carry the mxm-fabric name.
## Inherited kernel roadmap (from the source repository)

| Step | Work |
|---|---|
| 1 | Stand-up: process home, protected `main`, CI, ref mirror (WP-MXK-0001) |
| 2 | Bring in the reconciled enforcement core (identity-bound ports, chained Evidence, persisted halt, traceability) |
| 3 | Release and vendoring contract: manifest, hash pinning, offline verifier, no-external-import check |
| 4 | Self-contained MCP framework (stdlib, stdio) with delegation binding (WP-MXK-0004, ADR-MXK-0002); registering it with each engine is harness-side |
| 5 | Signed, single-use, act-bound authorizations and one transactional event log (WP-MXK-0005, ADR-MXK-0003) |
| 6 | Memory and federation enforcement: memory operations as governed actions; one delegation model that only narrows |
| 7 | First release, and its first vendored adoption |

Human-Curated, AI-Enabled (HCAE)
