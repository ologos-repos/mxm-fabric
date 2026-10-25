# ADR-MXK-0006 — Verification is a bounded evidence relation

- **Status:** Decided
- **Work package:** `04-work-packages/WP-MXK-0009-verification-boundary/`
- **Evidence:** `04-work-packages/WP-MXK-0008-transformer-limitations/evidence/sikka-sikka-2025-audit.md`
- **Decision authority:** Principal Operator, 2026-09-28 ("Proceed")
- **Requirements:** REQ-MXK-VER-01 through REQ-MXK-VER-05

## Context

The kernel already treats a model as untrusted compute, treats model summaries as non-evidence,
and binds external effects to kernel receipts. That is necessary but incomplete. A system can
still overclaim by calling model self-review "verification", by treating a verifier as proving
more than it checked, or by converting resource exhaustion into a confident assertion.

The Sikka and Sikka audit strengthens the architectural motivation for explicit verification
boundaries while rejecting their strongest universal complexity-to-hallucination inference.

## Decision

1. **Verification is property-bounded.** A verifier establishes only the property it actually
   checks against identified evidence.
2. **Generation is not verification by default.** Re-sampling, critique, reflection, or another
   generative model may be useful evidence but does not become independent assurance merely by
   being a separate inference.
3. **Authority remains external to prose.** A generated claim cannot create authoritative state,
   prove an external action occurred, or substitute for a receipt.
4. **Failure is representable.** Unsupported, unresolved, timed-out, approximate, and failed
   outcomes are legitimate terminal epistemic states and cannot silently become assertions.
5. **Capability claims name their boundary.** Component limits and composite-system limits are
   separate propositions.

## Consequences

The SPEC gains normative verification semantics. The enforcement implementation does not yet
carry a general typed Verification object or assurance-level gate. Those controls remain tracked
implementation work until tests demonstrate them. Existing receipt, authorization, and event-log
mechanisms continue to provide strong verification for the narrower properties they actually
record.

Human-Curated, AI-Enabled (HCAE)
