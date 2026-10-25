# ADR-MXK-0004 — Revision of step 5 after independent review

- **Status:** Decided; extended by [ADR-MXK-0005](ADR-MXK-0005-signed-principal-records-and-act-outcomes.md)
- **Amends:** ADR-MXK-0003
- **Work package:** `04-work-packages/WP-MXK-0006-step5-revision/`
- **Decision authority:** Principal Operator, 2026-09-28 ("Proceed: Revise kernel step 5 per the
  Advisor's REVISE findings")
- **Review:** Principal Advisor, cross-provider, 2026-09-28, recommendation REVISE. The record is
  retained in the `principal-advisor-log`.

## Context

The independent review of step 5 (WP-MXK-0005) found that the design was sound in outline but
could not yet be represented as an enforcement boundary. The Principal Assistant reproduced
the two most serious findings against the merged code before accepting them:

1. **Effect substitution.** A signature covered the action, but replay did not check that the
   recorded effects were the ones that action produces. An intercepted, unspent Operator
   waiver authorization could be written into the log as an abort, and every kernel accepted
   it.
2. **Small-order keys.** The verifier accepted the identity point as a public key. With the
   identity nonce and S = 0 it verified any message, and the trust registry accepted it.

The review also found claims stronger than the code:

- the serialization was called canonical JSON;
- a scope default was applied after signing;
- Evidence records were barely validated;
- the anchor-failure semantics were stated too broadly;
- the ADR said faults "never raise".

No kernel log had been deployed, so the rules could be tightened without migrating history.

## Decision

1. **Replay derives effects.** For every act, `_check` computes the only effects the action
   type produces for the recorded decision, from the action and current state. Each action
   type may record only its own effecting decisions. A record with any other effects, or any
   other decision, halts the kernel. Per-type preconditions are checked on replay too:
   - waiver rationale;
   - clear with no challenge;
   - kernel-scope `clear_halt` with a halt to clear;
   - a new unit on open.

   A signature therefore authorizes an effect exactly when the effect is what the signed
   action does.
2. **Weak keys are refused.**
   - Verification rejects small-order public keys and nonces.
   - `valid_public_key` also requires the prime-order subgroup.
   - The trust registry refuses any other key when loaded.
3. **A defined signing domain.** Signed bodies may contain only these value types:
   - string-keyed objects and arrays;
   - strings, booleans and null;
   - integers below 2^53 in magnitude.

   Floats, NaN and infinities are excluded, and anything outside the domain cannot be signed
   and verifies as `malformed`. The SPEC calls this the MxM signing serialization and no
   longer claims general canonical JSON.
4. **The opening is resolved before signing.** `kernel.opening_act` fills in these fields,
   and the Operator signs all of them:
   - scope;
   - required method;
   - constitution version.

   `open_package` refuses any other act, and replay requires the opened unit to be exactly
   the signed opening.
5. **Evidence answers an act.** `receipt` and `memory` records must be written by the kernel
   and answer, once, an earlier act that owes that kind of evidence. `halt` records must be
   written by the kernel.
6. **Anchor lag and loss.**
   - A crash between append and anchor write leaves the anchor behind a valid log. The next
     kernel verifies the log, replays it and moves the anchor forward.
   - A configured anchor that is missing beside a non-empty log halts (`anchor_missing`).
   - On anchor-write failure, the act stays recorded with its state change, and its external
     side effect does not run.
7. **Faults.**
   - Failing side effects (tool, method, memory) are recorded with their error and denied.
   - Log read errors halt the kernel.
   - What still raises is stated: lock-acquisition I/O errors, and invalid Python API
     arguments.

## Alternatives considered

- **Sign the whole record (action, decision and effects) after a principal-side preview.**
  This is stronger in principle, but it moves the kernel's decision into the signer's
  workflow and requires a preview round trip for every act. Deriving effects on replay gives
  the same guarantee for principal effects without changing the workflow.
- **Recompute the full decision (`_decide`) on replay.** Not possible for host policy, since
  the broker, trust scope and methods are host configuration. So it was not adopted, and the
  limit is stated instead (SPEC §7): replay does not re-evaluate host policy for Assistant
  acts.
- **Use a vetted Ed25519 library through an isolated helper.** This is not available in the
  standard-library-only, air-gapped release. The hand-written verifier is mitigated by:
  - the RFC 8032 vectors;
  - byte-identical cross-checks against OpenSSL and `cryptography`;
  - small-order and subgroup tests;
  - the mutation battery.

  A harness that can carry a vetted library may substitute one, since signatures interoperate.

## Consequences

- Every finding in the review is dispositioned. TRACEABILITY.md and the WP record map each
  one to its code and tests.
- A 33-mutation check covers every defence, old and new. Each disabled defence fails the
  suite, and each is caught by the test aimed at it.
- Stated limit, not closed: an engine that can write the log can still record Assistant-level
  acts that host policy would deny, with receipts. No tool runs, but state and Evidence can be
  falsified that way. The log not being engine-writable is a deployment precondition.
- Whether the kernel may now be represented as an enforcement boundary under the stated
  preconditions is the Principal Operator's call. A follow-up Advisor review of this
  revision is recommended before making it.

Human-Curated, AI-Enabled (HCAE)
