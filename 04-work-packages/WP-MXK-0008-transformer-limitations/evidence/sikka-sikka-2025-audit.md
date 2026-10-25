# Sikka & Sikka (2025) claim and scope audit

**Primary source:** Varin Sikka and Vishal Sikka, *Hallucination Stations: On Some Basic
Limitations of Transformer-Based Language Models*, arXiv:2507.07505v3 (15 July 2025).

**Audit date:** 2026-09-28

## Executive finding

The paper identifies a sound general concern: a bounded computational component cannot correctly
execute every arbitrarily harder computation, and high-consequence agent systems should not treat
language-model generation or self-review as sufficient evidence of correctness.

The paper's stronger formulation, however, should **not** be imported into MXM as a theorem that
all tasks whose conventional algorithmic complexity exceeds O(N^2 d) force an LLM or LLM-based
agent to hallucinate.

The proof as written does not establish that universal claim. It moves from a bound asserted for
the transformer's core/self-attention computation to a bound on an entire generated response and
then to an LLM-based agent. Autoregressive generation performs repeated inference as output tokens
are generated, and an agent can invoke external computation. The paper itself later acknowledges
that its work concerns individual LLM limitations and that multiple LLMs/composite systems can
achieve higher abilities.

The Time Hierarchy Theorem supports the weaker existence claim: for computational models with
specified resource bounds, there exist problems outside the lower time class. It does not by itself
show that every problem commonly implemented by an O(n^3), exponential, or factorial algorithm is
unsolvable by the model, nor that failure is semantically identical to hallucination.

## Claim ledger

| ID | Paper claim | Audit classification | MXM disposition |
|---|---|---|---|
| HS-01 | Conventional self-attention over N tokens and dimension d has an O(N^2 d + N d^2) computational cost, simplified by the authors under stated assumptions. | SUPPORTED WITH SCOPE | Cite only as a component-level cost characterization. |
| HS-02 | An LLM's overall computation is O(N^2 d) for a prompt of length N. | OVERBROAD / ASSUMPTION | Do not adopt as a bound on an autoregressive response or agent system. |
| HS-03 | If a prompt specifies any task above that complexity, the LLM cannot correctly carry it out. | NOT ESTABLISHED AS STATED | Replace with a resource-bounded existence claim and task-specific verification requirement. |
| HS-04 | Theorem 1: a task of O(n^3) or higher in a prompt makes an LLM or LLM-based agent unavoidably hallucinate. | NOT ESTABLISHED AS STATED | Reject as an MXM theorem. Preserve as an external claim under audit. |
| HS-05 | Time hierarchy implies there exist tasks beyond a bounded computational class. | SUPPORTED IN GENERAL FORM | Harvest the existence principle, subject to formal model/resource definitions. |
| HS-06 | Exact verification of some tasks can itself be computationally expensive or intractable. | SUPPORTED IN GENERAL; EXAMPLES NEED PRECISION | Harvest as rationale for verifier selection and explicit assurance boundaries. |
| HS-07 | An LLM verifier cannot in general verify another agent's solution when verification exceeds its resources. | DIRECTIONALLY SUPPORTED, OVERGENERALIZED IN PAPER | Harvest only as prohibition on assuming same-path self-review is sufficient assurance. |
| HS-08 | All operations of an LLM-based agent are bounded by the core LLM complexity. | FALSE FOR GENERAL TOOL-USING AGENTS | Explicitly reject for MXM. External tools/executors have their own resource models. |
| HS-09 | Reasoning models do not overcome the limitation. | CONJECTURAL IN THIS PAPER | Do not harvest as theorem. Paper says rigorous analysis is future work. |
| HS-10 | Composite systems, rigorous augmentation/constraining, and multiple LLMs can increase system capability. | ACKNOWLEDGED BY AUTHORS | Strongly relevant to MXM architecture. Does not imply correctness by composition. |

## Formal issues requiring qualification

### 1. Per-operation cost is not total response cost

The paper describes output as autoregressive, with generated tokens feeding subsequent token
generation, but then reasons from an O(N^2 d) core-operation characterization as though it bounded
the whole task. For an output of K generated tokens, total inference work necessarily includes
repeated generation steps and depends on implementation, caching, changing sequence length,
model depth, and other architectural details. Therefore the paper's stated bound cannot simply be
used as the total computational budget of an arbitrary response.

### 2. Time hierarchy does not prove the universal task claim

The deterministic time hierarchy theorem establishes separations between time classes under its
formal conditions. It establishes existence of languages/problems requiring more time than a
lower class. It does not license the inference:

> this named task has a familiar O(n^k) algorithm; therefore no lower-complexity method or
> representation can solve this instance/task family.

An upper bound for a particular algorithm is not automatically a lower bound for the problem.

### 3. Output size must be separated from computational hardness

The token-composition example asks the model to enumerate an exponentially large output. An
exponential lower bound follows trivially from the amount of output that must be emitted. This is
useful as a resource-bound example, but it does not establish a general theory of hallucination.

### 4. Matrix multiplication example is not a clean lower-bound proof

Citing the naive O(mnp) algorithm establishes the cost of that algorithm, not an inherent lower
bound of the matrix-multiplication problem. It therefore cannot carry the universal theorem.

### 5. TSP decision/optimization/verification distinctions matter

Verifying that a supplied route is syntactically valid and has a stated length is polynomial.
Verifying that it is globally optimal without a certificate or other bound is a different question.
The paper's brute-force illustration is not proof that every exact optimality verification procedure
must enumerate all routes. MXM must keep execution, certificate checking, and global optimality
claims distinct.

### 6. "Hallucination" is overloaded

Failure to compute a requested answer within a resource budget, refusal, timeout, approximation,
incorrect computation, and fabrication are different failure classes. MXM should preserve these
distinctions. Resource insufficiency should produce an explicit unresolved/unsupported state rather
than being collapsed into the label hallucination.

## Architectural harvest for MXM

The paper is most useful to MXM as a constraint argument for **epistemic and computational
separation**:

1. The generative model is a bounded computational component, not an authority.
2. Model confidence and model self-review are not evidence of correctness.
3. Tasks should be routed to fit-for-purpose deterministic or independently checkable executors
   where the assurance claim requires them.
4. Verification must have an explicit resource and trust model. A second generative pass is not
   automatically independent verification.
5. Consequential actions require evidence bound to the action and its outcome.
6. The system must represent unsupported, unresolved, timeout, approximation, and verification
   failure states without converting them into asserted facts.
7. External tools expand system capability but do not erase limits. Their outputs require provenance,
   authorization, and verification appropriate to consequence.
8. Composite architecture changes the unit of analysis from the transformer to the whole system.
   Claims about system limits must therefore specify the system boundary.

## Proposed MXM requirements

### REQ-MXK-VER-01 — Independent assurance

A generative inference path SHALL NOT be the sole verifier of its own consequential factual,
computational, or action claim when an independent deterministic, authoritative, or otherwise
qualified verification mechanism is available and required by the assurance level.

### REQ-MXK-VER-02 — Computational authority separation

MXM SHALL distinguish generative inference from authoritative state, deterministic computation,
external execution, provenance, validation, and action receipts.

### REQ-MXK-VER-03 — Explicit verification boundary

Each verification mechanism used for a consequential claim SHALL identify what property it
verifies, its evidence source, and material limitations. Verification SHALL NOT be represented as
proof of properties outside that boundary.

### REQ-MXK-VER-04 — Resource/failure honesty

When a requested computation or verification exceeds available resources or supported assurance,
MXM SHALL preserve an explicit unresolved, unsupported, timeout, approximate, or failed state
rather than promote the result to an authoritative assertion.

### REQ-MXK-VER-05 — System-boundary claims

Any computational-capability or impossibility claim used as an MXM design constraint SHALL name
the relevant system boundary. A transformer-component limitation SHALL NOT be represented as a
limit of a tool-using composite system without a separate argument.

## Cross-program disposition

TMF is a downstream integration point for durable memory, provenance, and state separation.
No TMF change is authorized by this WP. The primary architectural finding belongs in MXM because
it concerns what the generative component is allowed to assert, verify, and authorize within the
system trust boundary.

## Confidence

- Primary-paper bibliographic and textual claims: **HIGH**, verified against arXiv v3.
- Audit of the paper's inference from core-operation complexity to whole-response/agent complexity:
  **HIGH** as a logical scope objection.
- Exact alternative asymptotic characterization of modern autoregressive/tool-using systems:
  **not asserted here**; it is implementation-dependent and outside the proof needed for this WP.
- Independent peer-review status: **UNCERTAIN**. arXiv describes v3 as a six-page preprint intended
  for AAAI-26 submission after reviews; this audit does not treat it as peer-reviewed.

## Reference

Sikka, V. and Sikka, V. (2025) 'Hallucination Stations: On Some Basic Limitations of
Transformer-Based Language Models', arXiv:2507.07505v3, 15 July.
