# ADR-MXM-0002 — Construct consolidation under 05-mxm-construct

- **Status:** Decided
- **Decision authority:** Principal Operator, 2026-10-23 ("I agree and ratify")
- **Concurrence:** GPT architecture review, 2026-10-23 (recommends ratification with the gates and the transport-independence requirement recorded in items 5 and 6).
- **Rationale:** Repository structure. Names no new requirements; the consolidation specification's R-01 to R-12 are the input record.
- **Input:** "MxM Fabric Construct Consolidation" specification and assessment (2026-10-23, filed in the working coordination record, with the file-by-file migration inventory).

## Context

The construct already lives under 05-mxm-construct (meta-harness, memory, means), but it has no runtime component, no contracts component, and no console. The reference architecture describes a broader system than the kernel library alone. A consolidation decision is needed before additive construction begins, so new components land in owned places and the release contract stays coherent.

## Decision

1. **All substantive MxM components are owned under 05-mxm-construct.** New components: mxm-core (headless runtime and API), mxm-console (TUI and web thin clients), mxm-contracts (versioned API/event schemas and conformance). No mxm-* directories at root.
2. **MXM.md remains the canonical bootstrap.** AGENTS.md and CLAUDE.md remain minimal discovery adapters that route to it. This amends the specification's R-02, which proposed the inverse arrangement; the current one is empirically what both harnesses load, and demoting MXM.md would break the substance of the Codex discovery path for no benefit. README.md remains the repository's public face, not a stub.
3. **means/ remains the executable substrate through phases 1-4** of WP-MXK-0014 (decision D1, Option A): mxm-core is built as a runtime/API layer consuming the enforcement core where it sits. Whether enforcement, mcp, and release relocate under mxm-core is reconsidered at phase 5 on implementation evidence, and if chosen is recorded as its own ADR amending ADR-MXK-0001. Under no option do two enforcement implementations exist.
4. **Console sequencing (D3):** TUI first, web second, both on the same contracts and event stream.
5. **The core API is transport-independent.** JSON-RPC over stdio and HTTP are adapters over the same application services. No transport implements its own authorization or execution logic.
6. **Approval gates.** Ratifying this ADR and approving WP-MXK-0014 passes the architecture gate: additive development under 05-mxm-construct is authorized through the normal branch, review, and verification workflow. Two further principal gates stand: the **runtime gate** (review the core API and its authorization conformance before integrating the TUI) and the **migration/release gate** (separately authorize any relocation of means/, any change to the vendoring contract, or any production cutover). Approval of the work package is not unrestricted permission to restructure the existing kernel.
7. **The numbered 00-06 backbone is unchanged.** Root retains only the existing discovery and metadata files.

## Alternatives considered

- Adopt the specification unamended, including R-02. Rejected: it inverts a working, deliberate bootstrap arrangement and breaks the substance of the Codex discovery path.
- Relocate means/ into mxm-core immediately. Rejected for now: the vendored release contract, verifier pins, and test bootstraps all pin current paths; relocation before the core API exists is churn without a consumer. Reconsidered at phase 5 under the migration/release gate.
- Leave the structure as is and let new components land ad hoc. Rejected: unowned growth is how shadow authorities form (R-06).

## Consequences

Construction proceeds under WP-MXK-0014. The layout verifier is amended before any canonical path changes (R-11). Work sequencing (D4): consolidation phases 1-2 complete first; cross-runtime conformance (WP-MXK-0010) then runs against the core API. Ratified baseline documents (SPEC, reference architecture, conformance model, capability contracts) are untouched; if consolidation changes any claim they make, that change goes through a new ADR or a version increment.

## Verification

ADR-MXM-0002 and WP-MXK-0014 are on main with this decision recorded; the migration inventory is frozen as phase-1 evidence under WP-MXK-0014; the layout verifier and the test suite pass on the tree carrying this record.

Human-Curated, AI-Enabled (HCAE)
