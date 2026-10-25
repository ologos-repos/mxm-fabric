# Agentic AI Ecosystem Reference Architecture

![Navy and amber hero graphic with bold text: The Agentic AI Ecosystem, beside a six-band stack labeled Governs, Remembers, Reasons, Connects, Executes, Delivers.](hero.png)

Every reference architecture is an argument about what matters, drawn as boxes. This one is mine for the agentic AI ecosystem: the stack an enterprise needs if agents are going to do real work under real authority, and keep doing it after the demo ends. I have built pieces of this for years and argued for most of it in pieces. Here it is on one plate, with the decisions visible.

Read it in the order it is drawn. Across the top sits a governance and enforcement control plane. Beneath it, six layers carry the work from experience down to infrastructure. Beneath those, an assurance framework states how anything on the plate earns trust. At the bottom, outcomes are judged. The left rail is what the world brings in; the right rail is what the ecosystem owes back.

![MxM Fabric, an agentic AI reference architecture: a governance and enforcement control plane across the top, six layers from Experience and Interaction down to Infrastructure and Platforms, the Epistemic Assurance Framework beneath them, trusted and accountable outcomes at the bottom, external environment at the left, outcomes and value at the right.](plate.jpg)

*The MxM Fabric plate. The layer colors are the reading aid: each layer states a job.*

## Governance is drawn first, on purpose

Most stack diagrams draw governance as a box off to the side, or omit it and add a review board later. This plate draws it across the top, as a control plane that touches every layer beneath it.

The control plane is the MxM Multi-Mode Meta-Harness, the governing construct the author's own agents run under. Its six surfaces state what governance consists of. Mission: purpose, objectives, scope, success criteria. Mind: reasoning standards, methodological discipline, uncertainty handling. Morals: integrity, transparency, authorized conduct, accountability. Memory: knowledge governance, provenance, admission, and supersession under the Triadic Memory Fabric (TMF). Methods: the disciplined practices the work follows. Means: the models, tools, data access, and computation any agent is allowed to reach. Under the surfaces sit the governance functions (identity and authorization, delegation and control, conformance and monitoring, policy and guardrails, evidence and audit, risk management), enforced across layers rather than inside any one of them.

Methods deserves a sentence of its own, because it is wider than it looks. It covers three families of practice: reasoning and research, meaning the research workflows of the Epistemic Assurance Framework (EAF) below; software delivery and operations, meaning DevSecOps, GitOps, Everything as Code, and the Scaled Agile Framework (SAFe); and systems engineering, meaning Model-Based Systems Engineering (MBSE) and the Modular Open Systems Approach (MOSA). An agent that reasons well but ships through no disciplined pipeline is half governed. The methods are the other half.

The placement is the claim. Governance is not a filter applied to outputs at the end. It is the harness every agent runs inside from the first token. The longer version of this argument is made in [Harness Engineering](https://blog.thinxai.net/posts/harness-engineering/): the wrapper matters more than the model, because the wrapper is where authority lives. Identity is the clearest case: every agent needs an identity is not a runtime concern in one layer, it is a condition the control plane sets on every layer that touches a credential, a dataset, or a tool. The spine drawn down the left of the stack is that condition made visible: the control plane does not sit above the layers as a comment on them, it connects into each one.

One distinction before going further, because the plate invites the mistake. The six surfaces and the six layers are not corresponding pairs, and they are not the same kind of thing. The surfaces are a governing contract: how any work in this ecosystem is purposed, reasoned, authorized, remembered, methodized, and resourced. The layers are an organization of technical capabilities: what the work runs on. The EAF, below the layers, evaluates the quality and warrant of the information and reasoning the capabilities produce. The TMF, inside layer three, provides the governed knowledge and memory services the rest of the stack draws on. Contract, capabilities, evaluation, memory: four different jobs, drawn in four different places because they are different dimensions of the same system.

## Memory is a layer, not a feature

Layer three is knowledge and memory, and it is drawn as infrastructure: the Triadic Memory Fabric in three tiers (Meta: knowledge models, ontologies, domains; Meso: themes, entities, and relationships, the knowledge graphs; Micro: records, evidence, provenance), with state management, admission control, and a federation and authority function that today reads alongside existing stores and is meant to be promoted to the authority over them. This placement is the second claim. Vendors sell memory as a model feature, a longer context window or a recall toggle. An ecosystem cannot run on that. Agents change models; the record of what was decided, observed, and superseded has to survive the change, and it has to carry its provenance with it, because an agent that cannot say where a memory came from cannot be trusted to act on it.

This is also where the plate meets the enterprise architecture work. In [The Governed Control System](https://blog.thinxai.net/posts/the-governed-control-system/) the argument is that evidence is an interpretation and has to arrive graded, with source, method, and confidence. Layer three is where that graded evidence lives between turns of the loop. Memory without provenance is just a longer hallucination with better recall.

## Context is engineered, and the model is a routed resource

Layer two (embedding models, vector search and indexing, Retrieval-Augmented Generation (RAG), context engineering, semantic caching, model routing, relevance ranking over admitted records) exists to make a third claim: what reaches the model is an engineering decision, not an accident of whoever wrote the prompt last. Context assembly, grounding, caching, and routing are architecture, with owners and budgets. Note where the models sit: behind the routing in layer two, and again behind the AI gateways in layer four. Nowhere on this plate is a model the center of anything. Models are replaceable parts under governance, selected per task on cost and performance, with fallback when one fails or misbehaves. Any architecture that cannot survive swapping its model is not an architecture; it is a dependency.

Two clarifications the tiles compress. The vector store underneath the search is an implementation choice, not a commitment: layer three's memory fabric is defined by its tiers and its admission rules, and it does not stand or fall with any one indexing engine. And the retrieval in RAG is governed retrieval, which is the word doing the work in that tile. What retrieval returns is candidate context, assembled under the context engineering in the same layer and used to ground the generation. It becomes knowledge only by passing the admission control in layer three. Retrieved is not the same as admitted, and the plate keeps the two in different layers on purpose.

A note on what kind of document this plate is, because it governs how to read everything on it. This is a target architecture. It states the capabilities the ecosystem is designed to have, whole and without apology. Which of those capabilities are deployed in a given estate today, and how completely, is a conformance question, and it is answered per deployment, not on this plate. Annotating the target model with one estate's current state would date the plate the moment the estate changes, and would confuse the design with a status report. Design here; conformance elsewhere.

## Execution is a loop, run as an operation

Layers four and five are where intent becomes action. Layer four is integration: AI gateways, the Model Context Protocol (MCP), function calling, tool use, external APIs, workflow orchestration, and data connectors. Layer five is the runtime above them: the agent harness, and inside it the execution loop drawn as what it is, a repeating cycle of perceive, plan, act, observe, evaluate, iterate, with observability, evaluations, and operations alongside. The pairing matters. Tool access without an operations discipline is how an agent with good intentions edits the wrong record at machine speed. Observability and evaluations are drawn inside the runtime layer, not up in the control plane, because they are not compliance artifacts. They are how the operation knows what it did, in time to do something about it.

## Assurance is a discipline, drawn as a band

Under the layers sits the MxM Epistemic Assurance Framework, the EAF: six disciplines that state how a conclusion on this plate earns the right to be trusted. Information Fidelity (Shannon: source integrity, transformation fidelity, uncertainty analysis). Logical Analysis (Aristotle: validity, causality, categories). Critical Inquiry (Socrates: assumptions, contradictions, questions). Epistemic Warrant (Plantinga and Reid: justification, reliability, defeaters). Probabilistic Reasoning (Bayes: evidence updating, model comparison). Research Programme Appraisal (Lakatos and Gödel: the hard core of a programme, its hypotheses, and the formal limits on what can be proven inside it).

The names are on the plate because the disciplines are not mine and do not pretend to be. Each one is a standing body of work with standards an agent's reasoning can be checked against. Warrant is the one I lean on hardest: a conclusion carries its justification, the reliability of the process that produced it, and the defeaters that would overturn it, or it does not travel. The outcomes band at the bottom of the plate states the standard the EAF exists to meet: traceable from sources and assumptions, through transformations and reasoning, to verified and accepted conclusions.

## The bottom line is outcomes

Layer six is rented ground: compute, storage, networks, backup and recovery, disaster recovery, scaling. Necessary, and deliberately unglamorous, because none of it differentiates anything.

The right rail and the bottom band are the judgment: better decisions, trustworthy analysis, validated knowledge, higher productivity, lower risk, accountable AI use. The stack is read downward but justified upward. Every layer has to be able to say, in one sentence, how it feeds a trusted outcome at the bottom. A layer that cannot answer that question is decoration, and decoration in an agent stack is worse than useless, because it is attack surface with a budget.

## How this plate relates to the other one

Readers of the SARS series will ask how this fits [Digital Ecosystem Architecture at All Levels](https://blog.thinxai.net/posts/agentic-enterprise-architecture/). The two plates are companions at different altitudes. SARS is the enterprise's operating model: how strategy, architecture, roadmaps, and standards govern the whole estate. This plate is the reference architecture of the agentic ecosystem that estate now contains: in control-system terms, the architecture of the plant's newest and fastest-moving part, with MxM as its local governor under the enterprise's authority. One governs the enterprise. The other describes what is being governed.

Use the plate as a test. Bring any proposed agent capability to it and ask four questions. Which layer does it live in? What is its memory story, with provenance? Which control plane functions touch it, and who holds the authority? Which outcome at the bottom does it move, and how would we know? A proposal that answers all four is architecture. A proposal that answers only the first is a demo, and demos are how ecosystems accumulate agents nobody can govern.

---

Reference-architecture article (2026-10-23), companion to
[MXM-REFERENCE-ARCHITECTURE-0001](../MXM-REFERENCE-ARCHITECTURE-0001.md).
Pulled into this repository 2026-10-23; publication scaffolding and external
venue links removed on import.

Human-Curated, AI-Enabled (HCAE)
