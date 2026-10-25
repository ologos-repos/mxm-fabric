# MxM Reference Architecture: Governance, Knowledge, and Epistemic Assurance

**ID:** MXM-REFERENCE-ARCHITECTURE-0001  
**Version:** 0.2.0  
**Status:** Approved, architecture baseline (ratified 2026-10-23, ADR-MXK-0007)  
**Related:** [EAF specification](SPEC-MXM-EAF-0001.md)

## Purpose and scope

This is a vendor-neutral **target reference architecture**, not a claim of deployed functionality in any specific environment. Product positioning, enterprise adoption, and specific deployment conformance are separate views derived from this reference.

## Cross-cutting governance topology

MxM is the **Multi-Mode Meta-Harness** and governs the entire AI ecosystem, not a sequential layer between experience and intelligence. Its Mission, Mind, Morals, Memory, Methods, and Means surfaces provide behavioral and operational contracts. Kernel enforcement applies only where a given implementation has demonstrated it.

Logical capability domains:
1. Experience and interaction: GUI, terminal, messaging, and enterprise applications.
2. Intelligence and context: model selection/routing, context engineering, retrieval, and RAG.
3. Knowledge and memory: TMF Meta/Meso/Micro, provenance, admission, and promotion.
4. Integration and execution: MCP, APIs, functions, tools, gateways, and workflows.
5. Runtime and operations: delegation, isolation, observability, evaluation, and quality drift monitoring.
6. Infrastructure and platforms: compute, storage, networks, and recovery.

**MxM governance** spans all six domains. **EAF** is a governed, cross-cutting epistemic assurance capability spanning source, transformation, inference, and disposition boundaries. **IFA**, within EAF, evaluates information fidelity. **TMF** is the durable memory fabric, not an alternative authorization authority.

```text
                   MxM governance and enforcement
       Mission | Mind | Morals | Memory | Methods | Means
    +------------------------------------------------------+
    | Experience and interaction                           |
    | Intelligence and context                             |
    | Knowledge and memory (TMF)                           |
    | Integration and execution                            |
    | Agent runtime and operations                         |
    | Infrastructure and platforms                         |
    +------------------------------------------------------+
           EAF / IFA: cross-cutting assurance checks
                 Governed, accountable outcomes
```

This diagram shows logical scope, not guaranteed runtime coverage.

## Architectural decisions (proposed)

**D-1 Governance topology:** MxM is a cross-cutting control plane; deployments must identify each enforcement point, coverage gap, and verification artifact. A six-surface contract does not by itself prove enforcement across every CLI.

**D-2 Memory authority:** Separate TMF design conformance, service implementation, operational integration, and promotion to authoritative memory. Read-alongside or shadow deployments SHALL NOT be represented as authoritative. Promotion requires documented principal approval, migration/reconciliation, rollback, admissibility controls, and verification.

**D-3 Retrieval admission:** Admission is independent of relevance. Similarity and lexical ranking MAY order **eligible/admitted** records, but SHALL NOT make a record admissible or authoritative. A retrieved record is evidence to evaluate, not a validated conclusion. A conceptual flow is: governed admission -> retrieval and ranking of eligible records -> EAF evidence evaluation -> reasoned disposition -> governed memory promotion. Candidate evidence acquisition may precede admission; admission governs use as authoritative context, not the ability to inspect external material.

**D-4 Epistemic assurance:** EAF/IFA shall provide traceable source-to-transformation-to-claim-to-disposition evidence, proportional checks, and explicit separation of Shannon statistical information, semantic fidelity, and epistemic warrant.

## Implementation maturity and conformance

Every material capability SHALL be labeled with a scope, evidence reference, and one of:
- **Specified:** contract or design documented; no implementation asserted.
- **Implemented:** executable code/configuration exists in an identified environment.
- **Verified:** defined tests passed for that implementation, version, and scope.
- **Operational:** observed in an active workflow with operational evidence.
- **Authoritative:** designated system of record or enforcement authority, with explicit principal approval and verified cutover where relevant.

These states are **not automatically cumulative**. For example, a service can be operational in read-alongside mode without authoritative status. A claim of authoritative status requires separately recorded evidence. Mark unknowns **Not assessed**, not failed.

Each conformance record SHOULD contain: capability ID, target environment, version/commit, claimed maturity, control owner, enforcement surface, verification method, observed evidence, gaps, date, and reviewer.

## Deployment assessment inputs

Deployment-specific assessments are recorded in per-deployment conformance records (see the Conformance Model), not in this reference. No deployment state is asserted here.

## Derived views and next steps

Maintain distinct views for (1) product positioning, (2) enterprise adoption, and (3) specific deployment conformance. Do not transfer implementation claims between them.

Proposed workstreams, subject to authority and prioritization: TMF authority transition; EAF-to-memory admission assurance; governed semantic retrieval; cross-CLI kernel enforcement; continuous quality and risk evaluation; unified gateway; formal recovery architecture.

**Acceptance:** principal review of D-1 through D-4 and maturity taxonomy. No runtime implementation, TMF cutover, or approval is implied by this document.

## Technical capability model (v0.2.0)

The 17 numbered capabilities below are logical reference capabilities, not assertions of installed components. The six architectural layers and six governance surfaces are orthogonal: no one-to-one pairing is implied.

| # | Capability | Primary layer | Required boundary |
|---|---|---|---|
| 1 | Embedding models | Intelligence and context | Representation generation is not admission |
| 2 | Vector databases / vector indexing | Intelligence and context (service); knowledge/storage (substrate) | Similarity ranking is not authority |
| 3 | Retrieval-Augmented Generation (RAG) | Intelligence and context | Governed retrieval, context assembly, grounded generation |
| 4 | Context engineering | Intelligence and context | Authorized context selection and lineage |
| 5 | Semantic caching | Intelligence and context | Cache entries honor policy, provenance, expiry, and admission |
| 6 | Model routing | Intelligence and context | Approved model selection and usage controls |
| 7 | AI gateways | Integration and execution | Identity, policy, quotas, audit, routing |
| 8 | Function calling | Integration and execution | Schema validation and delegated authorization |
| 9 | Tool use | Integration and execution | Approved tools, scope, side-effect controls |
| 10 | Model Context Protocol (MCP) | Integration and execution | Tool/resource interface with kernel authorization |
| 11 | External integrations | Integration and execution | API/data access and provenance |
| 12 | Agent harness | Agent runtime and operations | Delegation, orchestration, isolation, audit |
| 13 | Execution loop | Agent runtime and operations | Perceive -> plan/reason -> act -> observe -> evaluate -> iterate |
| 14 | Memory systems | Knowledge and memory | Triadic Memory Fabric (TMF): Meta, Meso, Micro; governed admission and authority |
| 15 | Guardrails | Cross-cutting MxM governance | Policy enforcement across all layers |
| 16 | Observability | Agent runtime and operations | Logs, metrics, traces, evidence and incident records |
| 17 | Evaluations | Agent runtime and operations; EAF | Operational tests distinct from epistemic assurance |

Additional supporting capabilities include identity and access, provenance, risk management, state/checkpoints, workflow orchestration, backup and recovery, disaster recovery, and infrastructure scaling.

### Governed retrieval and memory sequence

```text
Sources -> ingestion/chunking -> embedding or lexical indexing
        -> eligibility/admission policy -> retrieval/ranking/reranking
        -> authorized context assembly -> model inference
        -> runtime evaluation + EAF/IFA assessment
        -> disposition -> governed memory promotion
```

This is a logical sequence; source discovery and candidate-evidence inspection may precede authoritative admission. Embeddings, vector stores, and semantic caching are optional implementations, not prerequisites for TMF. The reference does not mandate a vector database.

### Cross-layer control and assurance

Every capability SHALL declare applicable Mission, Mind, Morals, Memory, Methods, and Means obligations and identify enforcement points, evidence, and unimplemented gaps. MxM is the cross-cutting governance and enforcement control plane, not a layer in the request path. EAF is a governed, cross-cutting assurance function; TMF provides knowledge and memory services. Neither EAF nor TMF bypasses kernel authorization.

### Diagram baseline

**MxM-RA-0001: Agentic AI Reference Architecture** is the intended diagram identifier. The visual SHALL retain the six layers, six surfaces, the full 17-capability inventory, expanded **Triadic Memory Fabric (TMF)** on first use, and EAF; avoid deployment-specific names, infrastructure provenance, and implementation-status claims. The diagram is a reference view; deployment maturity belongs in conformance records.

See [Capability Contracts](MXM-CAPABILITY-CONTRACTS-0001.md) and [Conformance Model](MXM-CONFORMANCE-MODEL-0001.md).
