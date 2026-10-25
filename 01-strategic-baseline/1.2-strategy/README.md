# Strategy: chosen approach and tradeoffs

Ratified 2026-10-23 by the Principal Operator, approved as drafted (WP-MXK-0015). Drafted from this repository's own record.

## The approach

1. **Govern the harness, not the model.** Models change quarterly; the
   authority, evidence, and acceptance structure must not. The fabric
   invests in the layer that persists: surfaces, kernel, contracts.
2. **Kernel first, evidence before claims.** Build the enforcement core,
   prove it with tests that can fail (including mutation checks), and
   let every wider claim wait for its evidence. Maturity attributes are
   independently evidenced or not claimed at all.
3. **Consolidate before expanding.** One construct, one home, no shadow
   authorities (ADR-MXM-0002). New components land in owned places
   under 05-mxm-construct or they do not land.
4. **Publish the record.** The architecture, the papers, and the
   conformance evidence are the credibility asset. The repository is
   the reference implementation and conformance authority for the layer
   it describes.
5. **Stay portable and vendor-neutral.** Capability contracts specify
   required behavior, not products. The kernel vendors self-contained,
   hash-pinned, and offline-verifiable, so governed execution works in
   regulated and air-gapped environments where agentic tooling usually
   cannot go.

## Tradeoffs, stated plainly

| Choice | We take | We give up |
|---|---|---|
| Enforcement location | Kernel boundary, fail-closed | The convenience of trusting model or UI-level controls |
| Dependencies | Standard library for the kernel; console dependencies isolated in the console's own release | Faster feature development from third-party stacks |
| Maturity claims | Claim only what evidence supports (Specified is not Operational) | Impressive but unverifiable positioning |
| Scope growth | Bounded work packages with explicit authority boundaries | Opportunistic breadth |
| Memory | Admission and provenance before accumulation | Effortless recall of everything, governed or not |
| Consoles | Thin clients that can never authorize | Feature-rich operator surfaces with direct power |

## What this strategy refuses

- A second enforcement implementation anywhere, under any option.
- Treating structural verification as proof that a model complied.
- Treating automated evaluation scores as epistemic warrant or as
  principal acceptance.
- Expanding the capability footprint ahead of conformance evidence for
  the controls already claimed.

Human-Curated, AI-Enabled (HCAE)
