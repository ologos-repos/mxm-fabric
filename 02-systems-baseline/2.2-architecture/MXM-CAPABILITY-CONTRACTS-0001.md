# MxM Technical Capability Contracts

**ID:** MXM-CAPABILITY-CONTRACTS-0001  
**Version:** 0.2.0  
**Status:** Approved, baseline (ratified 2026-10-23, ADR-MXK-0007)  
**Related:** [Reference Architecture](MXM-REFERENCE-ARCHITECTURE-0001.md), [EAF](SPEC-MXM-EAF-0001.md), [Conformance](MXM-CONFORMANCE-MODEL-0001.md)

## Contract model

Each capability is logical and vendor-neutral. The contract SHALL specify: purpose, inputs, outputs, dependencies, applicable governance controls, EAF/IFA assurance, and verification. Capabilities can be supplied by third-party products. Implementation maturity is separately assessed.

**Governance abbreviations:** Mi=Mission (scope), Md=Mind (reasoning), Mo=Morals (integrity/policy), Me=Memory (admission/provenance), Mt=Methods (procedures), Mn=Means (tools/resources). All six surfaces apply at system level; the table highlights primary controls, not exclusions.

| ID | Capability and purpose | Inputs → outputs | Dependencies | Primary MxM controls | EAF/IFA obligations | Minimum conformance evidence |
|---|---|---|---|---|---|---|
| CAP-01 | Embedding models: represent content | Approved content → vectors | Model registry, ingestion | Me, Mn, Mo | Source-to-vector lineage, limits | Model/version, deterministic fixture, authorization |
| CAP-02 | Vector indexing/search: similarity retrieval | Admitted vectors/query → ranked candidates | Storage, eligibility filter | Me, Mo, Mn | Ranking not authority, source trace | Exclusion tests, relevance metrics, index version |
| CAP-03 | RAG: retrieval-grounded generation | Query, eligible sources → cited response | Retrieval, context, inference | Me, Md, Mo, Mt | Grounding, citations, unsupported-addition detection | Provenance and adversarial grounding cases |
| CAP-04 | Context engineering: fit relevant context | Query, source candidates, budget → context | Admission, retrieval | Mi, Me, Md, Mt | Omission and qualification fidelity | Context manifest, token budget, omission checks |
| CAP-05 | Semantic caching: reuse equivalent work | Request, policy context → eligible cache hit/miss | Cache, provenance, identity | Me, Mo, Mn | No stale, cross-scope, or unsupported reuse | Tenant/policy isolation, invalidation, expiry |
| CAP-06 | Model routing: select approved model | Task, policy, economics → route decision | Model catalog, policy, telemetry | Mi, Mo, Mn | Explainable selection and limitations | Route trace, policy/availability/fallback tests |
| CAP-07 | AI gateway: control model/API access | Authenticated request → governed upstream request | Identity, routing, audit | Mo, Mn, Mi | Audit/provenance continuity | Deny/allow, quota, audit, error handling |
| CAP-08 | Function calling: structured invocation | Model call proposal → validated invocation/result | Schemas, authorized runtime | Mo, Mn, Mt | Capture parameters, result and evidence | Schema rejection, scope and replay tests |
| CAP-09 | Tool use: execute approved capabilities | Authorized action → observable result | Registry, sandbox, permissions | Mo, Mn, Mi | No unverified success claims | Authorization, side-effect, rollback evidence |
| CAP-10 | MCP: standardized tool/resource exchange | MCP requests → tool/resource responses | MCP servers/clients, auth | Mo, Mn, Me | Source identity and tool result lineage | Contract, transport, permissions tests |
| CAP-11 | External integrations: domain connectivity | Approved API/data request → governed data/action | Credentials, gateway, adapters | Mo, Mn, Me | Provenance, freshness, attribution | Permission, rate limit, failure, audit tests |
| CAP-12 | Agent harness: orchestration/delegation | Authorized objective → tasks and results | Models, tools, execution | Mi, Mo, Mt, Mn | Traceable task decomposition and claims | Delegation ledger, isolation, acceptance tests |
| CAP-13 | Execution loop: iterative agent control | Observation/plan → action/feedback | Harness, tools, evaluators | Mi, Md, Mo, Mt | Evidence at evaluation and stop gates | Termination, error recovery, loop trace |
| CAP-14 | Memory systems: durable governed knowledge | Candidate records → eligible/validated memory | TMF or equivalent, admission | Me, Mo, Md | Lineage, defeaters, supersession | Admission, promotion, rollback, authority tests |
| CAP-15 | Guardrails: enforce policy constraints | Proposed operation → allow/deny/escalate | Kernel, identity, policies | Mo, Mi, Mn | Record policy rationale and exceptions | Bypass attempts, enforcement-point coverage |
| CAP-16 | Observability: operational evidence | Logs, traces, metrics → monitoring/alerts | Runtime, telemetry, retention | Mo, Mt, Mn | Evidence chain and integrity | Correlation, redaction, alert, retention tests |
| CAP-17 | Evaluations: measure behavior and quality | Test cases and outputs → scores/findings | Benchmarks, harness, EAF | Md, Mt, Mo | Distinguish runtime scores from warrant | Regression, drift thresholds, review separation |

## Architectural rules

1. **Eligibility before authoritative retrieval:** Embedding similarity, vector indexing, lexical search, reranking, and caching cannot confer admission or authority. External candidate evidence may be inspected without being admitted to authoritative memory.
2. **Authority at execution boundaries:** Gateway, function calling, tool use, MCP, and agent loops SHALL honor applicable kernel authorization; a successful model response cannot substitute for permission.
3. **Evidence through transformation:** Context assembly, summarization, RAG, and caching SHOULD retain source-to-output lineage and support proportional IFA checks.
4. **Evaluation separation:** Runtime evaluation is distinct from EAF claim warrant, IFA fidelity, and principal acceptance.
5. **Portability:** A capability contract specifies required behavior, not a mandatory vendor, model, database, or deployment.
6. **Verification:** Passing tests is limited to the implementation version and environment tested; claims of operational or authoritative maturity require additional evidence.

## Acceptance

These contracts are proposed normative architecture. Adoption does not establish that any particular deployment satisfies them. Implementation work SHALL identify capability IDs, contract versions, exceptions, test evidence, and principal approval for reserved decisions.
