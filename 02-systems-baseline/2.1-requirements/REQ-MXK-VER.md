# MXM verification-boundary requirements

**Source WP:** `04-work-packages/WP-MXK-0008-transformer-limitations/`  
**Implementation WP:** `04-work-packages/WP-MXK-0009-verification-boundary/`  
**Status:** Approved requirements; implementation status is tracked separately.

## REQ-MXK-VER-01 — Independent assurance

A generative inference path SHALL NOT be the sole verifier of its own consequential factual,
computational, or action claim when qualified independent verification is required and available.

"Independent" is functional, not merely process identity. A second sample, second prompt, or
second model is not automatically an independent verifier. The verification mechanism must have
an evidentiary basis appropriate to the property claimed.

## REQ-MXK-VER-02 — Computational authority separation

MXM SHALL distinguish generative inference from authoritative state, deterministic computation,
external execution, provenance, validation, and action receipts. Generated text alone SHALL NOT
be promoted to evidence of an external effect or authoritative state.

## REQ-MXK-VER-03 — Explicit verification boundary

A verification result used for a consequential claim SHALL identify:

- the property actually verified;
- the evidence source or mechanism;
- the material limitations of the verification.

The result SHALL NOT be represented as assurance of properties outside that boundary.

## REQ-MXK-VER-04 — Resource and assurance honesty

When required computation or verification exceeds the supported resource or assurance boundary,
MXM SHALL preserve an explicit unresolved, unsupported, timed-out, approximate, or failed state
as applicable. Such a state SHALL NOT be promoted to an authoritative assertion merely because a
model generated a plausible answer.

## REQ-MXK-VER-05 — System-boundary claims

Any computational-capability or impossibility claim used as an MXM design constraint SHALL name
the relevant system boundary. A limitation established for a transformer or other component SHALL
NOT be represented as a limitation of a tool-using composite system without a separate argument.

## Evidence basis

These requirements survive the claim audit of Sikka and Sikka (2025). They do not depend on the
paper's stronger universal claim that every task above a stated transformer complexity bound must
produce hallucination. See
`WP-MXK-0008-transformer-limitations/evidence/sikka-sikka-2025-audit.md`.

Human-Curated, AI-Enabled (HCAE)
