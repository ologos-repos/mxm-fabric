# The Governed Control System

![Navy and amber hero graphic with bold text: The Governed Control System, beside a circular loop marked Ratify.](hero.png)

The first three pieces in this series built an argument in stages. [Agentic Enterprise Architecture](../agentic-enterprise-architecture/agentic-enterprise-architecture.md) set out the operating model: Strategy, Architecture, Roadmaps, and Standards, worked at the enterprise, systems, and solutions levels. [The Architecture Repository](https://blog.thinxai.net/posts/the-architecture-repository/) made the model concrete as typed artifacts in Git, with a catalog, registered views, and machine-checked gates. [Own the Core. Synthesize the Rest.](https://blog.thinxai.net/posts/own-the-core-synthesize-the-rest/) defended owning that record instead of renting it back from a platform vendor.

A careful reader of the series put a question to me that I have not been able to put down: is this an operating model, or is it a control system? The honest answer is that I had built the second and named it the first. This piece corrects the framing, because the framing decides what the thing is for.

## An operating model has no dynamics

SARS tells an organization what it is responsible for: who owns strategy, who owns standards, at which levels, with what handoffs. That is necessary, and it is static. An operating model does not say how the record and the estate correct each other over time, how fast, or how anyone would know the correction is working.

But the loop was already there, in the first piece, drawn as an arrow I did not take seriously enough: observed state flowing back into the model. Sense, reconcile, propose, ratify, change the estate, sense again. That is not an org chart. That is a feedback loop, and a feedback loop with setpoints, sensors, and gated actuation has a name in every other engineering discipline. It is a control system. Agentic enterprise architecture is a governed control system for the digital ecosystem, and SARS is the operating model inside it.

## The mapping

**The plant** is the digital ecosystem itself: the systems, services, and operations the architecture describes, doing the organization's real work.

**The setpoints** are the authorized target state. Not a wish list: the ratified record. The SARS artifacts, the catalog of elements and relations, the standards in force. When the record says a system will expose a contract at version two, that is a setpoint.

**The sensors** are the evidence. Statements about the estate as it actually is: what a vendor declares about its own service, what direct inspection observes, what analysis infers from both. Each arrives with a source, a method, and a confidence, or it does not count as a reading.

**The controller** is the agentic operation from the first piece: sense the estate, reconcile evidence against the record, analyze the difference, and propose a correction. Agents do this work continuously because the estate changes continuously and a quarterly review board cannot track a daily plant.

**The actuators** are ratified changes: a merged pull request against the record, a funded work package, a cutover. Nothing actuates on a proposal. The path from controller to actuator runs through a gate.

**Governance** is that gate, staffed by humans whose authority is scoped: an architecture board ratifies enterprise standards, a systems architect ratifies inside a ratified system boundary, a security authority co-ratifies what touches its domain. The gate is not a courtesy. It is the difference between a control system and an amplifier.

![The governed control system: authorized target state compared against evidence from the plant, corrections proposed by agents and actuated only through human ratification.](fig-loop.png)

*The governed control system. Evidence changes the record, and the record changes the estate. Human authority gates the one transition that can do either.*

## Control systems are measured

Here is why the name matters. An operating model is adopted. A control system is tuned, and tuning requires readings. If this loop is working, four numbers move:

- **Conformance rate**: the share of the estate the evidence shows matching its authorized target state.
- **Change throughput**: ratified architectural changes per quarter, from proposal to merged record.
- **Architectural currency**: the share of the record verified against evidence inside its review window. A model nobody has checked lately is a hypothesis, not a record.
- **Drift half-life**: the median time from a drift item opening to its closing, halved or doubled as the loop improves or decays.

If those numbers do not move, the loop is theater: agents generating proposals nobody can ratify, sensors producing snapshots nobody reconciles. The measures are the difference between a claim and a system.

## Four open problems

I would rather state these plainly than pretend the series solved them.

**First, evidence is an interpretation.** My earlier pieces treated observed state as ground truth. It is not. A vendor's registry declares one thing, direct inspection observes another, and both are claims with provenance. I have started on this one: the [repository template](https://github.com/jdlongmire/ea-repository-template) now specifies evidence as typed artifacts in three kinds (declared, observed, inferred), each carrying source, method, time, and confidence, and drift is classified four ways: the estate is wrong (defect), the record is wrong (model error), the reading is wrong (sensor error), or the evidence cannot yet say (undetermined). A controller that cannot grade its own sensors will file confident defects against healthy systems.

**Second, typing is not semantics.** A catalog with a fixed relation vocabulary, which the template now has, stops agents from inventing relationships. It does not yet stop them from drawing legal nonsense: a solution realizing a capability directly, a standard bound to a roadmap. The next step is relation law: which element types may stand at each end of each relation, in what counts, enforced by the same verifier that checks everything else.

**Third, conformance is not fitness.** The loop can prove a system meets a standard. It cannot, from that proof, tell you whether the standard still serves the strategy. Automation floods toward conformance because conformance is checkable; fitness is the harder evaluation, and it belongs to the Strategy and Roadmaps columns: exception counts per standard, milestone attainment, the outcomes the roadmap promised. A standard with a perfect conformance rate and a rising exception queue is a standard asking to be retired.

**Fourth, authority is scoped, not flat.** The template encodes ratification as code ownership, which answers "whose file is this" and not "who may ratify this change." Real authority is ordinal and bounded by scope and impact, an argument I have made in the ORDSA work ([Ordinal Systems Architecture](https://doi.org/10.5281/zenodo.20334233)) and not yet honored in the tooling. A ratification matrix (change type by level by impact, naming required approvers including separate security authority) is engineering debt this series owes.

## Intent, evidence, authority

Underneath the mapping sit three things the loop must never blur. **Intent**: what the organization has decided the estate should be, held in the record. **Evidence**: what the estate actually is, arriving as graded claims. **Authority**: who may change either one. Every failure mode I have seen in architecture governance is a blur among these three: a dashboard treated as a decision, a decision treated as a fact, an agent's proposal treated as someone else's ratification.

The control-system framing keeps them separate by construction. Setpoints are not sensor readings. The controller proposes and the gate disposes. Agents make the loop fast; governance is what makes the speed safe to want.

The loop is running today, against a fictional estate, in the open: the template holds the record, and [ThinxEA](https://github.com/jdlongmire/thinxea) is the execution face I am building for it, with the measured quantities above as its dashboard rather than its decoration. The four problems are the agenda. I intend to work them in the open, in that order.

---

Essay first published 2026-10-17 on Thinx-Tank (https://blog.thinxai.net/posts/the-governed-control-system/). Pulled into this repository 2026-10-23; publication scaffolding removed on import, and the citation of the companion SARS essay points at the local copy. Source: jdlongmire/thinx-tank, content/posts/the-governed-control-system.md, blob 12a792a7.

Human-Curated, AI-Enabled (HCAE)
