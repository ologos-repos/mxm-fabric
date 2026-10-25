# WP-MXK-0008 — Transformer limitations and independent verification boundary

## Purpose

Evaluate Varin Sikka and Vishal Sikka's 2025 paper, *Hallucination Stations: On Some Basic
Limitations of Transformer-Based Language Models* (arXiv:2507.07505), as a potential external
constraint source for MXM.

The paper is relevant because it argues from computational limits rather than merely observed
hallucination rates, including a stronger claim concerning tasks whose answers a transformer
cannot reliably verify. That claim intersects directly with MXM's separation of generative
reasoning from authoritative action, evidence, and enforcement.

## Governing caution

This work package does **not** begin from the proposition that the paper proves that LLMs must
hallucinate in every relevant setting. The formal argument, assumptions, quantifiers, and
architectural scope must be reconstructed first.

Particular attention is required for distinctions between a bounded transformer forward pass
and systems that add autoregressive iteration, tools, deterministic computation, external
memory, verification services, or other agents.

## Intended MXM harvest

If supported by the audit, the paper may strengthen the rationale for:

1. authoritative state outside the transformer;
2. provenance and evidence bound to actions;
3. deterministic executors for tasks that require deterministic computation;
4. independent or heterogeneous verification for consequential claims;
5. explicit uncertainty and failure states;
6. prohibition on treating model confidence or self-review as sufficient evidence.

These are candidate implications, not pre-approved conclusions.

## Cross-program disposition

TMF may later consume findings concerning external memory and provenance, but this package
belongs in MXM because its primary question is the trust and enforcement boundary around a
probabilistic generative component.
