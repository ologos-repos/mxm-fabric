# Traceability spine

The cross-baseline chain, in one place: every objective traces to
requirements, architecture, a solution configuration, an
implementation, and verification evidence, or the chain is shown
ending where it honestly ends. Published under WP-MXK-0015 step 5.
Upkeep passes to WP-MXK-0011 from this record forward: when evidence
changes, the affected row changes in the same commit.

How to read a row: follow it left to right. A cell naming a file or a
test is a link that exists today. "Ends at specification" means the
fabric specifies the capability and deliberately leaves its
implementation to deployments; that is a scope fact, not a defect
(see capability-traceability.md, same folder).

## 1. Complete chains: the kernel capability set

Objectives are from 01-strategic-baseline/1.3-objectives-krs (O1:
prove the kernel's controls in operation). Kernel requirements are
carried by the enforcement specification itself (see the 2.1 scope
note); the EAF and verification requirement families join where
noted. The solution for all five rows is the vendored-kernel
deployment pattern (03-solutions-baseline/kernel-deployment-pattern.md).

| Capability | Requirement | Architecture | Implementation (05) | Verification |
|---|---|---|---|---|
| CAP-08 Function calling | Enforcement SPEC §§5-7 (action and authorization model); REQ-MXK-VER-02 | MXM-CAPABILITY-CONTRACTS-0001 (CAP-08); reference architecture | means/enforcement | Enforcement TRACEABILITY.md; conformance, adversarial, Ed25519, and authorization tests; 40-case mutation check |
| CAP-09 Tool use | Enforcement SPEC §§5, 8 (act outcomes); REQ-MXK-VER-02, 04 | Contracts (CAP-09) | means/enforcement | TRACEABILITY act-outcome rows (executed, not_executed, unknown); same mutation evidence |
| CAP-10 MCP | ADR-MXK-0002 (self-contained MCP, delegation binding) | Contracts (CAP-10) | means/mcp/mxm_mcp | MCP test suite (means/mcp/tests), green in CI |
| CAP-12 Agent harness | Enforcement SPEC §§4-5 (principals, delegation); REQ-MXK-VER-01 | Contracts (CAP-12); ADR-MXM-0002 (construct) | means/enforcement; means/scripts (session discipline) | TRACEABILITY delegation rows (single-use, expiry, role and pin binding); suite green in CI |
| CAP-15 Guardrails | Enforcement SPEC §§7, 10 (decision and failure behavior); REQ-MXK-VER-04 | Contracts (CAP-15) | means/enforcement | Full TRACEABILITY plus the 40-case mutation check; the strongest evidence in the repository |

All five chains stop at Verified. Operational and Authoritative
require deployment evidence, which no repository record holds; the
missing link is named, not papered over, and cross-runtime
demonstration is WP-MXK-0010.

## 2. Partial chains: substrate present, chain incomplete

| Capability | Objective | Traces to | Chain ends at | Governing work |
|---|---|---|---|---|
| CAP-13 Execution loop | O1, O2 | Contracts (CAP-13); enforcement SPEC halt and outcome semantics | Partial implementation in the enforcement core; no standalone loop controller, no full-run termination traces | WP-MXK-0010 |
| CAP-14 Memory systems | O2 | Contracts (CAP-14); TMF specified in SPEC-MXM-EAF-0001; REQ-MXK-VER-02 | Pointer-shaped memory surfaces (05-mxm-construct/memory); no TMF store, no admission/promotion test evidence | WP-MXK-0013 |
| CAP-16 Observability | O2 | Contracts (CAP-16) | The signed event log as evidence substrate; no correlation, redaction, alert, or retention tooling | P2 backlog, no package yet |

## 3. Chains ending at specification

CAP-01 (embedding models), CAP-02 (vector indexing), CAP-03 (RAG),
CAP-04 (context engineering), CAP-05 (semantic caching), CAP-06
(model routing), CAP-07 (AI gateway), CAP-11 (external
integrations), CAP-17 (evaluations): objective O2 (complete the
construct) traces each to its contract in
MXM-CAPABILITY-CONTRACTS-0001, and the chain ends there by design.
These capabilities are deployment-supplied. Where a validation
obligation exists it is named: CAP-02 admission-aware retrieval is
WP-MXK-0013; CAP-03 and CAP-04 grounding and fidelity evidence
belongs to the EAF/IFA minimum implementation, WP-MXK-0012; CAP-17
claim evaluation likewise. The rest are not assessed (WP-MXK-0011
evidence population, if a deployment is nominated).

## 4. Requirement-family traces

- **EAF-001 to EAF-020** (2.1-requirements/EAF-requirements.md)
  derive from SPEC-MXM-EAF-0001 §10 and govern the EAF functional
  scope. Their implementation chain runs through WP-MXK-0012 (EAF/IFA
  minimum implementation, proposed); until it lands, these
  requirements trace to specification only, and this spine says so.
- **REQ-MXK-VER-01 to 05** trace from WP-MXK-0008 (claim audit) to
  WP-MXK-0009 (implementation: SPEC §8A, ADR-MXK-0006) to the
  verification behavior stated in 2.3-behavior §6 and exercised by
  the enforcement test evidence above.
- **Layout and bootstrap**: ADR-LAYOUT-0001 and ADR-LAYOUT-0002
  trace to 00-meta-model/verify-repository-layout.py, the aide
  verifier, and the layout evidence in this folder; their stated
  limit (structure is not behavior) is carried in 2.3-behavior §6.

## 5. Known breaks

1. No chain reaches Operational or Authoritative; no deployment
   evidence is recorded in this repository.
2. Cross-runtime links are missing for every kernel capability
   (WP-MXK-0010, sequenced after WP-MXK-0014 phases 1-2).
3. The EAF requirement family has no implementation link yet
   (WP-MXK-0012).
4. Objectives O3 and O4 trace to the record itself (this baseline
   set and the root README's Publications section); their
   verification is the state of the tree, checked at each landing.

Human-Curated, AI-Enabled (HCAE)
