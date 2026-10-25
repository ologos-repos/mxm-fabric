# MxM Implementation Maturity and Conformance Model

**ID:** MXM-CONFORMANCE-MODEL-0001  
**Version:** 0.2.0  
**Status:** Approved (ratified 2026-10-23, ADR-MXK-0007)  
**Related:** [Reference architecture](MXM-REFERENCE-ARCHITECTURE-0001.md), [EAF](SPEC-MXM-EAF-0001.md)

## Capability assessment contract

A conformance claim SHALL specify the capability, environment, implementation version, responsible principal, control or interface, test/observation, evidence, date, and limits. Record **Specified**, **Implemented**, **Verified**, **Operational**, and **Authoritative** as independently evidenced attributes rather than one inferred score. Unknown = **Not assessed**. A failed check = **Not conformant for tested criterion**, not a universal failure.

| Attribute | Minimum evidence |
|---|---|
| Specified | Versioned requirement or architecture contract |
| Implemented | Code/configuration and deployable component reference |
| Verified | Test case, execution environment, result, artifact |
| Operational | Real workflow observation, run logs, accountable owner |
| Authoritative | Explicit designation/approval, enforcement or system-of-record cutover, verification, rollback |

## Assurance gates

1. **Governance:** Can the kernel enforce the declared policy at the actual tool, model, CLI, and memory boundaries? Show tests, not just contracts.
2. **Retrieval:** Are admission decisions independent from relevance ranking? Are external evidence and authoritative memory distinguished?
3. **Memory:** Is TMF shadow/read-alongside or authoritative? Are pending records reconciled and promotion/rollback evidenced?
4. **EAF/IFA:** Can material claims be traced through sources and transformations to challenge, evaluation, and disposition?
5. **Operations:** Are benchmark drift, risk, recovery, and incident handling demonstrated in the target environment?

## Example assessment worksheet

| Capability | Specified | Implemented | Verified | Operational | Authoritative | Evidence / gap |
|---|---|---|---|---|---|---|
| MxM six-surface governance | Not assessed | Not assessed | Not assessed | Not assessed | Not assessed | Per-CLI evidence required |
| TMF memory | Not assessed | Not assessed | Not assessed | Not assessed | Not assessed | Read-alongside vs cutover to establish |
| Retrieval admission | Not assessed | Not assessed | Not assessed | Not assessed | Not assessed | Eligibility before ranking |
| Semantic retrieval | Not assessed | Not assessed | Not assessed | Not assessed | Not assessed | Optional capability; not implied by TMF |
| EAF/IFA | Specified | Not assessed | Not assessed | Not assessed | Not assessed | EAF v0.2 specification; no implementation asserted |
| Unified gateway | Not assessed | Not assessed | Not assessed | Not assessed | Not assessed | Borrowed proxy vs owned gateway |
| Continuous evaluation | Not assessed | Not assessed | Not assessed | Not assessed | Not assessed | Drift suite and thresholds |
| Recovery | Not assessed | Not assessed | Not assessed | Not assessed | Not assessed | Formal DR evidence |

The worksheet is intentionally conservative: it does not convert a third-party or operator narrative into verified conformance.

## Evidence and acceptance

Conformance is scoped to a release and environment. Structural repository verification is not proof of live enforcement. Reviewer and principal acceptance SHALL be separately recorded. Reassess after material deployment, policy, or memory-authority changes.

## Capability-level conformance (v0.2.0)

Every one of the 17 capabilities in [MXM-CAPABILITY-CONTRACTS-0001](MXM-CAPABILITY-CONTRACTS-0001.md) SHALL have an independent deployment assessment. Do not infer maturity from the reference diagram or adjacent capabilities.

A conformance record SHALL identify:
`capability_id`, `contract_version`, `deployment_id`, `implementation_ref`, `environment`, `control_owner`, `specified_evidence`, `implemented_evidence`, `verified_evidence`, `operational_evidence`, `authoritative_evidence`, `enforcement_points`, `open_gaps`, `risk_reference`, `reviewer`, `review_date`, and `principal_acceptance` where applicable.

### Minimum test families

- **Retrieval:** indexing correctness, lexical/vector recall and relevance, policy-filtered eligibility, provenance, caching invalidation, and unauthorized record exclusion.
- **Integration:** schema validation, delegated authorization, tool side effects, audit, failure and rate-limit handling.
- **Runtime:** loop termination, isolation, checkpoint recovery, telemetry, regression benchmarks, and drift thresholds.
- **Memory:** admission, supersession, lineage, read-alongside separation, authority cutover, rollback, and explicit principal designation.
- **EAF/IFA:** claim-to-source trace, material transformation fidelity, defeaters, dispositions, and independent acceptance.

**Acceptance rule:** A specified capability is not implemented; implemented is not verified; verified is not operational; operational is not authoritative. A deployment may be operational but explicitly nonauthoritative. Record unsupported evidence as **Not assessed**.

### Baseline governance

Architecture diagrams and capability contracts are reference-state artifacts. Operational readiness requires environment-specific conformance records and risk disposition. Continuous benchmark monitoring and formal risk registration are separately verifiable obligations, not presumed present.
