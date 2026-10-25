# MxM Epistemic Assurance Framework (EAF)
## Architecture and Implementation Specification

**Document ID:** SPEC-MXM-EAF-0001  
**Version:** 0.2.1  
**Status:** Approved, baseline v0.2.1 (ratified 2026-10-23, ADR-MXK-0007)  
**Target:** `ologos-repos/mxm-fabric`  
**Classification:** Domain-neutral / professional  
**Methodology:** Human-Curated, AI-Enabled (HCAE)

## 1. Executive summary

The MxM Epistemic Assurance Framework (EAF) establishes an evidence-disciplined methodology for AI-assisted reasoning, information evaluation, research, model development, and decision support within the Multi-Mode Meta-Harness (MxM). It integrates philosophy, logic, epistemology, information theory, scientific methodology, probability, and systems engineering into reusable analytical capabilities.

**Governing principle:** Every consequential conclusion should be traceable from assumptions and source information, through transformations, reasoning, and evidence, to verification status and disposition.

**Architectural principle:** Authority flows down. Evidence flows up. Information fidelity is evaluated across transformations.

EAF is domain-neutral, model-independent, and harness-portable. It does not prescribe a worldview or preferred conclusion. It extends MxM without replacing the kernel, its six surfaces, authorization controls, or memory authority.

## 2. Problem and objectives

AI outputs can obscure assumptions, fabricate support, conflate observations with interpretations, inconsistently compare hypotheses, overstate confidence, omit counterevidence, distort source meaning in compression or synthesis, misattribute sources, and lose decision history.

EAF SHALL:
1. Define consistent inquiry and evidence-evaluation procedures.
2. Make assumptions, claim types, inference dependencies, and uncertainty explicit.
3. Select complementary analytical methods proportionately to each inquiry.
4. Compare explanations against declared criteria, including adverse evidence.
5. Detect logical contradictions, methodological limits, and material information distortion.
6. Preserve provenance, transformations, objections, revisions, and supersession.
7. Generate reproducible records distinguishing automated assessment, verification, independent review, and human acceptance.
8. Operate within MxM authorization and governed memory interfaces across vendors and harnesses.

EAF SHALL NOT claim to guarantee truth, eliminate hallucinations, infer semantic truth from Shannon entropy, equate confidence with warrant, promote unvalidated memory, override kernel controls, or claim access to hidden model reasoning.

## 3. Methodological foundations

| Capability | Antecedent | Operational function |
|---|---|---|
| Critical inquiry | Socrates | Question assumptions, contradictions, and unanswered questions |
| Logical analysis | Aristotle | Analyze inference, categories, and causation |
| Common-sense evaluation | Thomas Reid | Examine ordinary cognitive and perceptual assumptions |
| Epistemic warrant | Alvin Plantinga | Assess justification, reliability, and defeaters |
| Formal boundary analysis | Kurt Gödel | Identify assumptions and limits of formal proof |
| Research-programme appraisal | Imre Lakatos | Appraise hard core, auxiliary hypotheses, and progressive or degenerating development |
| Probabilistic reasoning | Thomas Bayes | Update conditional assessments under explicit models |
| **Information theory and fidelity** | **Claude Shannon** | Quantify statistical uncertainty, model communication channels, and inform transformation-fidelity checks |

These are methodological antecedents, not personas or unquestionable authorities. Method selection SHALL follow the problem; not every method runs for every inquiry. Methods MAY operate iteratively or concurrently.

## 4. Placement in the six MxM surfaces

| Surface | EAF responsibility |
|---|---|
| Mission | Inquiry purpose, principal, authority, scope, and acceptance criteria |
| Mind | Reasoning discipline, epistemic distinctions, uncertainty, and evidence standards |
| Morals | Integrity, transparency, preservation of adverse evidence, authorized behavior |
| Memory | Governed preservation of validated claims, sources, decisions, defeaters, and supersession, using TMF where available |
| Methods | Inquiry procedures, evaluation rubrics, research appraisal, fidelity checks, review |
| Means | Approved retrieval, formal and statistical analysis, execution, verification, and evidence tools |

**Boundaries:** The MxM kernel owns applicable identity, authorization, delegation, and execution enforcement; EAF owns epistemic procedures and assurance evidence; TMF owns durable memory services; the harness performs authorized work. EAF SHALL NOT independently grant authority or bypass these boundaries.

The EAF profile SHALL be versioned and selectively activated rather than universally embedded into every always-loaded MxM instruction.

## 5. Assurance lifecycle

Eight logical stages MAY iterate:

1. **Frame:** Define objective, scope, authority, assumptions, and acceptance criteria. Output: Inquiry Definition.
2. **Ground:** Identify authoritative and competing sources, provenance, and integrity references. Output: Source Inventory and Evidence Register.
3. **Decompose:** Distinguish observations, source assertions, interpretations, hypotheses, predictions, and conclusions. Output: Claim and Assumption Register.
4. **Analyze:** Apply selected logical, causal, epistemic, probabilistic, information-theoretic, and domain methods; check transformations. Output: Analytical and Fidelity Records.
5. **Challenge:** Seek counterevidence, alternatives, contradictions, defeaters, and possible distortions. Output: Challenge Register.
6. **Evaluate:** Appraise coherence, evidence, explanatory and predictive adequacy, uncertainty, and fidelity. Output: Evaluation Record.
7. **Disposition:** Assign Accepted, Provisionally Retained, Revision Required, Suspended, Rejected, or Undetermined, with rationale. Output: Disposition Record. Automated disposition is not human acceptance.
8. **Preserve:** Route eligible validated artifacts and lineage through governed memory. Output: Epistemic Assurance Record.

## 6. Core information contracts

The implementation SHALL provide machine-readable, versioned schemas with at least these fields:

| Entity | Required fields |
|---|---|
| Inquiry | `inquiry_id`, `objective`, `scope`, `principal`, `authority_reference`, `acceptance_criteria`, `domain_profile`, `created_at`, `status` |
| Claim | `claim_id`, `statement`, `claim_type`, `source_references`, `assumptions`, `supporting_evidence`, `counterevidence`, `inference_method`, `uncertainty`, `epistemic_status`, `version` |
| Evidence | `evidence_id`, `source`, `source_type`, `retrieved_at`, `content_reference`, `provenance`, `relevance`, `limitations`, `integrity_reference` |
| Defeater | `defeater_id`, `target_claim`, `description`, `evidence_references`, `severity`, `resolution_status`, `resolution_rationale` |
| Information Transformation | `transformation_id`, `operation_type`, `input_references`, `output_references`, `tool_or_model`, `configuration_reference`, `timestamp`, `provenance_links`, `known_limitations` |
| Fidelity Assessment | `assessment_id`, `transformation_id`, `source_references`, `assessment_method`, `preserved_claims`, `material_omissions`, `material_distortions`, `unsupported_additions`, `attribution_findings`, `uncertainty`, `assessment_result`, `verification_status` |
| Disposition | `disposition_id`, `subject_id`, `decision`, `rationale`, `supporting_records`, `unresolved_limitations`, `evaluator`, `verification_status`, `acceptance_status`, `timestamp` |

Provenance SHOULD include immutable identifiers or hashes where feasible. Candidate claims SHALL remain distinguishable from validated facts.

## 7. Information Fidelity Assurance (IFA)

IFA is a first-class **EAF capability**, not an independent MxM surface. It evaluates whether information remains attributable, intact, and fit for purpose through retrieval, selection, compression, summarization, synthesis, model execution, and persistence.

Shannon entropy for a discrete random variable is:

```text
H(X) = - sum_x p(x) log2 p(x)
```

Conditional entropy, mutual information, and channel capacity MAY be used when variables, probability distributions, assumptions, and measurements are explicitly defined. These are **not** direct measures of semantic meaning, truth, source reliability, or epistemic warrant. Bayesian updating and Shannon information measures are complementary, not interchangeable; a decrease in entropy does not prove increased truth.

IFA SHALL distinguish five dimensions:
1. **Source integrity:** Identity and byte/content integrity where feasible.
2. **Transformation fidelity:** Preservation of material propositions, qualifications, causal relations, and constraints.
3. **Statistical uncertainty:** Justified information-theoretic measures only with defensible models.
4. **Provenance continuity:** Traceable input-to-output lineage.
5. **Semantic validation:** Material meaning, omissions, misattribution, and unsupported additions, evaluated separately from entropy.

Designated boundaries SHOULD include source-to-index, retrieval-to-context, context-to-analysis, analysis-to-output, output-to-memory-candidate, candidate-to-validated-memory, and memory-to-reuse.

Checks SHALL be risk-proportionate. Authorized lossy summaries are not automatically failures: evaluate losses against the declared purpose and fidelity requirements. Cryptographic integrity does not imply truth; semantic faithfulness may preserve a source's errors; statistical dependence does not imply justification.

## 8. Research-programme and probabilistic appraisal

For sustained research, EAF SHOULD capture Lakatosian hard-core commitments, protective-belt hypotheses, positive/negative heuristics, models, predictions and retrodictions, severe tests, adverse evidence, revisions, and progressive/degenerating indicators. Declared foundational commitments are not thereby empirically established. Evaluate alternatives without silently changing their premises.

For probabilistic analyses, EAF SHOULD record hypotheses, priors, likelihood assumptions, evidence dependencies, posteriors, sensitivity analyses, and model uncertainty. It SHALL refuse unjustified numerical precision and MAY provide clearly labeled qualitative assessments.

## 9. Traceability, statuses, and domain profiles

Each consequential disposition SHALL link:

**Inquiry → Sources → Transformations → Claims → Assumptions → Evidence → Methods → Challenges → Evaluation → Disposition**

Retain relevant versions and distinguish **Proposed**, **Executed**, **Verified**, **Independently Reviewed**, **Human Accepted**, and **Deployed**. An assurance record documents observable methods, artifacts, environments, and results, not private model thought.

Domain profiles MAY extend the domain-neutral core: `enterprise-architecture`, `systems-engineering`, `scientific-research`, `technology-evaluation`, `organizational-decision`, and `information-assurance`. Profiles MAY declare domain-specific commitments but SHALL NOT weaken provenance, integrity, or authorization requirements.

## 10. Functional requirements

The functional requirements for the EAF are recorded as traceable requirements in
[`02-systems-baseline/2.1-requirements/EAF-requirements.md`](../2.1-requirements/EAF-requirements.md),
IDs EAF-001 through EAF-020. That file is the requirements of record; this specification
traces to it rather than restating it. (The requirements were tabulated in this section
until 2026-10-23, when they moved to the repository's canonical requirements home.)

## 11. Nonfunctional requirements

EAF SHALL remain vendor- and harness-portable, auditable, extensible without kernel changes, and subordinate to existing security and authorization. It SHALL identify source versions, methods, tools, configurations, and environments needed for reproducibility. Checks SHOULD be proportionate to risk, consequence, and uncertainty. Interfaces SHOULD be machine-readable and accessible through governed MCP or approved equivalent adapters.

## 12. Verification and conformance

At minimum, test:
- Unsupported claims: identify insufficient support, never fabricate citations.
- Conflicting sources and hidden assumptions: preserve conflicts and expose assumptions.
- Circular arguments and formal proofs: identify invalid inference and proof-scope limits.
- Competing hypotheses: apply declared criteria consistently.
- Unjustified probabilities: reject invented precision.
- Memory promotion and unauthorized actions: honor MxM authority gates.
- Model revisions: preserve earlier evidence and rationale.
- Human acceptance: require explicit acceptance evidence.
- Lossy summaries: detect material omissions relative to purpose.
- Qualification reversals: detect changed meaning.
- Unsupported synthesis and misattribution: identify unsupported additions and attribution errors.
- Information metrics: require defined variables, distributions, and assumptions.
- Integrity versus truth: do not infer truth from an intact source.

Conformance evidence SHALL identify exact implementation, test version, environment, and result. Structural checks or a passing test suite do not establish universal epistemic reliability or runtime enforcement.

## 13. Implementation components

1. **Profile Registry:** Approved profiles, versions, activation rules.
2. **Method Library:** Analytical procedures, rubrics, templates, test protocols.
3. **Evaluation Engine:** Select methods, assemble evidence, challenge claims, propose dispositions.
4. **Information Fidelity Assurance Module:** Transformation lineage, fidelity checks, justified statistical measures.
5. **Assurance Recorder:** Provenance-linked records and governed memory routing.

The MVP MAY use structured files, schemas, and harness-invoked procedures; no standalone service is required initially.

### Proposed repository integration

```text
02-systems-baseline/
  2.1-requirements/EAF-requirements.md
  2.2-architecture/SPEC-MXM-EAF-0001.md
03-solutions-baseline/eaf/
  profiles/domain-neutral.yaml
  methods/method-catalog.yaml
  schemas/{inquiry,claim,evidence,defeater,transformation,fidelity-assessment,disposition}.schema.json
  tests/{conformance-cases,information-fidelity-cases}.yaml
04-work-packages/WP-MXM-EAF-0001/
  package.yaml
  implementation-plan.md
  verification-record.md
```

These are proposed future artifacts; this specification does not claim they exist, with one exception: `2.1-requirements/EAF-requirements.md` exists and is the requirements of record traced from section 10. Reconcile the remaining paths with canonical repository conventions before implementation.

## 14. Delivery phases and exit criteria

1. **Specification and contracts:** Approve requirements, schemas, profile, method catalog, and tests.
2. **Minimum viable EAF:** Produce a complete traceable inquiry and disposition.
3. **Information Fidelity Assurance:** Demonstrate detection of omissions, distortion, misattribution, and unsupported additions in controlled tests.
4. **MxM/TMF integration:** Preserve and retrieve validated records without bypassing authorization or promotion.
5. **Domain validation:** Show measurable improvement over agreed baseline in enterprise architecture, systems engineering, research, and information assurance pilots.
6. **Operationalization:** Introduce reporting, review, release versioning, and automated conformance for controlled adoption.

## 15. Measures and risks

Measure claim-to-evidence traceability, assumption identification, unsupported-claim detection, substantive defeaters, provenance completeness, transformation lineage, omission/distortion/addition detection, attribution accuracy, reproducibility, review disagreement, human rework, and time/cost per inquiry. Metrics require contextual interpretation; high traceability or semantic similarity does not prove accuracy.

Key risks and mitigations:
- Process overhead → proportional assurance.
- Structured-output overconfidence → independent checks and uncertainty.
- Method-selection bias → declared rules and adversarial review.
- Fabricated provenance → source integrity verification.
- Formal-method overreach → proof-boundary checks.
- Misapplied entropy → explicit statistical models and semantic separation.
- Semantic similarity overconfidence → claim- and qualification-level checks.
- Uncontrolled memory promotion → candidate-validation governance.
- Ideological prescription → domain-neutral core, scoped profiles.
- Kernel bypass → existing MxM enforcement interfaces.

## 16. Proposed architectural decision

**Decision:** Adopt EAF as a first-class domain-neutral capability of MxM Fabric, with Information Fidelity Assurance.

**Rationale:** Extend governed AI execution with disciplined analytical quality, explicit assumptions, information fidelity, traceability, structured challenge, and accountable dispositions.

**Constraints:** EAF does not replace the kernel, grant authority, or create alternative memory authority; its core remains domain-neutral; human acceptance is distinct from automated evaluation; Shannon metrics do not independently establish truth, meaning, or warrant.

**Initial work package:** `WP-MXM-EAF-0001` (proposed).  
**Decision status:** Approved by the Principal Operator 2026-10-23 (ADR-MXK-0007). Implementation and conformance remain separately evidenced.

## 17. Closing

MxM governs how AI capabilities operate. EAF governs the methodology by which AI-assisted claims, analyses, models, and recommendations are evaluated. IFA assesses information preservation and attribution. TMF preserves validated knowledge and provenance.

**Authority flows down. Evidence flows up. Information fidelity is evaluated. Conclusions remain open to examination.**

## 18. Integration clarifications (v0.2.1)

### 18.1 Distinct evaluation responsibilities

- **Runtime evaluation** tests agent/task behavior, benchmark quality, latency, operational correctness, and drift.
- **Information Fidelity Assurance (IFA)** assesses source integrity, transformations, omission, distortion, attribution, and semantic preservation.
- **EAF epistemic evaluation** assesses claim warrant, assumptions, competing explanations, defeaters, and evidence adequacy.
- **Human acceptance** is an explicitly authorized principal disposition, not inferred from any automated score.

Each produces independently identifiable evidence. Successful runtime evaluation SHALL NOT imply EAF acceptance, and successful IFA SHALL NOT imply source truth.

### 18.2 Retrieval and memory interface

EAF consumes source and retrieval records with provenance and eligibility metadata. Embeddings, vector databases, lexical retrieval, reranking, semantic caching, and RAG SHALL NOT independently promote information into authoritative memory. Ranking MAY order admitted records; an external source MAY be inspected as candidate evidence without becoming admitted authoritative context. EAF dispositions feed governed memory promotion only through existing authorization gates.

### 18.3 Capability contracts

EAF integration obligations SHALL be attached to the reference architecture's capability contracts, including evidence references, transformation lineage where material, verification status, and escalation for unresolved defeaters. EAF is not responsible for implementing retrieval engines, gateways, execution loops, or infrastructure.

See [MxM Reference Architecture](MXM-REFERENCE-ARCHITECTURE-0001.md) and [Capability Contracts](MXM-CAPABILITY-CONTRACTS-0001.md).
