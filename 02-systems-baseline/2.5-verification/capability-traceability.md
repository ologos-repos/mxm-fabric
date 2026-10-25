# Capability traceability matrix

Architecture and implementation assessment record for the 17 capabilities
in [MXM-CAPABILITY-CONTRACTS-0001](../2.2-architecture/MXM-CAPABILITY-CONTRACTS-0001.md),
assessed under [MXM-CONFORMANCE-MODEL-0001](../2.2-architecture/MXM-CONFORMANCE-MODEL-0001.md).

- **Assessed:** 2026-10-23, against this repository's main after
  ADR-MXK-0007 ratified the v0.2 baseline.
- **Input:** External architecture evaluation (GPT, 2026-10-23), filed in
  this folder with verification annotations.
- **Governing work package:** WP-MXK-0011 (assessment maintenance and
  evidence population).
- **Rules:** Attributes are independently evidenced, never inferred from
  adjacent capabilities or from the reference diagram. Unknown is recorded
  as **Not assessed**. Unfilled future work is not an implemented
  capability. A capability supplied by a deployment rather than by this
  repository is marked as such; its absence here is a scope fact, not a
  defect.

**Attributes:** S = Specified, I = Implemented, V = Verified,
O = Operational, A = Authoritative.

## Matrix

| CAP | Implementation in this repository | Evidence on hand | Attributes | Gap / governing work |
|---|---|---|---|---|
| CAP-01 Embedding models | None. Deployment-supplied. | Contract only. | S | Not assessed. WP-MXK-0011 evidence population if a deployment is nominated. |
| CAP-02 Vector indexing/search | None. Deployment-supplied. | Contract only; architectural rule 1 (eligibility before authoritative retrieval) is normative. | S | Admission-aware retrieval validation is WP-MXK-0013. |
| CAP-03 RAG | None. Deployment-supplied. | Contract only. | S | Grounding/fidelity evidence belongs to the EAF/IFA minimum implementation, WP-MXK-0012. |
| CAP-04 Context engineering | None as a product capability. The kernel's own context discipline is Methods, not this capability. | Contract only. | S | Omission/qualification fidelity checks: WP-MXK-0012. |
| CAP-05 Semantic caching | None. Deployment-supplied. | Contract only. | S | Not assessed. WP-MXK-0011. |
| CAP-06 Model routing | None. Deployment-supplied. The kernel is model-neutral by design and routes nothing itself. | Contract only. | S | Not assessed. WP-MXK-0011. |
| CAP-07 AI gateway | None. Deployment-supplied. | Contract only. | S | Gateway policy conformance sits in the P2 operational assurance backlog; no package yet. |
| CAP-08 Function calling | Enforcement core (`05-mxm-construct/means/enforcement/`): model proposals become validated, authorization-bound invocations with captured parameters and results. | `TRACEABILITY.md` in the enforcement folder; conformance, adversarial, Ed25519, and authorization test files; 40-case mutation check, suite failing at the aimed test each time. | S, I, V | Cross-runtime demonstration outstanding: WP-MXK-0010. Operational and Authoritative not claimed. |
| CAP-09 Tool use | Enforcement core: authorized actions execute with signed act outcomes and an event log; unverified success claims are structurally excluded. | Same traceability and mutation evidence as CAP-08; act-outcome records (WP-MXK-0007). | S, I, V | Rollback evidence is partial and deployment-specific. Cross-runtime: WP-MXK-0010. |
| CAP-10 MCP | Dependency-free MCP framework (`05-mxm-construct/means/mcp/mxm_mcp/`), per ADR-MXK-0002. | MCP test suite in `means/mcp/tests/`, green in CI. | S, I, V | Interoperability evidence against third-party MCP servers is not recorded. WP-MXK-0010. |
| CAP-11 External integrations | None. Deployment-supplied. | Contract only. | S | Not assessed. WP-MXK-0011. |
| CAP-12 Agent harness | The MxM construct itself: kernel bootstrap, delegation by signed authorization, task decomposition under the six surfaces. | Enforcement traceability (delegation, single-use, expiry, role and pin binding rows); suite green in CI. | S, I, V | Isolation and acceptance evidence in a second consuming runtime: WP-MXK-0010. |
| CAP-13 Execution loop | Partial: the kernel's step, halt, and outcome semantics inside the enforcement core. No standalone loop controller ships in this repository. | Halt and closing-outcome rows in enforcement traceability, including `not_executed` and `unknown` terminal states. | S, partial I, partial V | Loop-level termination and error-recovery traces across a full agent run: WP-MXK-0010. |
| CAP-14 Memory systems | Partial substrate: pointer-shaped memory surfaces (`05-mxm-construct/memory/`) and admission/provenance discipline in the kernel design. The Triadic Memory Fabric is specified in the EAF SPEC; no TMF implementation ships here. | SPEC sections on TMF; no admission/promotion/rollback test evidence for a TMF store. | S, partial I | TMF implementation and its authority tests do not exist yet. Governed retrieval and admission validation: WP-MXK-0013. |
| CAP-15 Guardrails | Enforcement core: policy constraints enforced at the kernel boundary (authorization, role, scope, replay, expiry), deny-by-default. | Strongest evidence in the repository: full traceability plus the 40-case mutation check. | S, I, V | Enforcement-point coverage in other runtimes: WP-MXK-0010. |
| CAP-16 Observability | Partial substrate: the signed event log is an evidence chain with integrity properties. No monitoring, alerting, or retention tooling ships here. | Event-log rows in enforcement traceability (chain, anchor, prefix checks). | S, partial I | Correlation, redaction, alert, and retention evidence: P2 backlog, no package yet. |
| CAP-17 Evaluations | None as a deployable capability. This repository's own suites evaluate the kernel; they are not the capability. | Contract only, for the capability as specified. | S | EAF claim evaluation is WP-MXK-0012; runtime evaluation harnesses are deployment scope. |

## Summary

- **Specified:** 17 of 17 (baseline ratified, ADR-MXK-0007).
- **Implemented and Verified in this repository:** CAP-08, CAP-09, CAP-10,
  CAP-12, CAP-15, all at kernel scope.
- **Partial substrate:** CAP-13, CAP-14, CAP-16.
- **Specified only:** CAP-01 through CAP-07, CAP-11, CAP-17. These are
  ecosystem capabilities the contracts deliberately leave to deployments
  and suppliers; the kernel product, the MxM Fabric reference
  architecture, and integrated ecosystem deployments are distinct scopes
  and this matrix assesses only the first against this repository.
- **Operational:** none claimed. No deployment evidence is recorded in
  this repository.
- **Authoritative:** none claimed.

## Maintenance

Update a row when its evidence changes: a test added, a runtime
demonstrated, a deployment assessed. Each update names the evidence, its
location, and the date. Attribute promotions require the evidence the
conformance model specifies for that attribute, reviewed independently of
the implementer where the model requires it.

Human-Curated, AI-Enabled (HCAE)
