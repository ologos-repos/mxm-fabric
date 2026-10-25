# Behavior baseline

The system's behavior, stated as implemented. Source of truth: the MxM
Kernel Specification (`05-mxm-construct/means/enforcement/SPEC.md`) and
the verification-boundary requirements
(`02-systems-baseline/2.1-requirements/REQ-MXK-VER.md`). This document
describes behavior; it adds no semantics. Where it and the SPEC
disagree, the SPEC governs and this document is in defect. Written
under WP-MXK-0015 step 3.

## 1. The work chain

All governed work moves through one chain:

```text
package → unit → run → evidence → acceptance → integration → disposition
```

Transitions move exactly one step forward. There are no skips and no
backwards steps; the Operator's `abort` is terminal, not a reverse.

| From | To | Gate |
|---|---|---|
| (create) | package | An Operator-signed package exists |
| package | unit | Operator, or kernel within package scope; constitution pinned |
| unit | run | Means bound; a Method, where one exists for the unit type, is selected unless the Operator marks the unit ad hoc |
| run | evidence | At least one kernel Evidence record of kind receipt, deny, or note |
| evidence | acceptance | Actor is the Operator; an open, unwaived Advisor challenge blocks |
| acceptance | integration | Acceptance is present |
| integration | disposition | Integration recorded; then Memory commit/flush |

**Acceptance is an Operator act.** The kernel records who accepted,
which unit, when, and under which pin. Model text containing the word
"accepted" is not Acceptance.

**The Advisor station** sits after Evidence and before Acceptance. The
Advisor writes a Challenge or an explicit Clear. A Challenge locks
Acceptance until the Operator waives it (a waiver requires a
rationale) or constitutionally supersedes it.

## 2. Decision behavior

Every proposed act receives exactly one decision:

- **Allow**: the act proceeds and its effects are recorded.
- **Deny**: no side effect; the WorkUnit remains in its current state;
  Evidence is recorded. After a Deny the Assistant may propose a legal
  alternative. The kernel does not retry.
- **Confirm**: a soft stop without operator authorization; no side
  effect until the Operator confirms.
- **Halt**: the unit, or the kernel as a whole, stops. Halts are
  recorded, persist across restarts, and are cleared only as section 4
  describes.

## 3. Authorization behavior

Operator and Advisor acts require a valid, unspent authorization for
exactly that act: signed, principal-bound, scoped, and expiring.
Anything else is denied (`unverified_operator` / `unverified_advisor`,
with the payload naming the problem). Authorizations are single-use;
replay is a denial, not a second execution. The Assistant acts within
the scope a package grants and holds no standing authority of its own.

## 4. Evidence behavior

There is one event log. Every decision, act, and outcome appends to
it, hash-chained and anchored; the anchor is kept where the engine
cannot write.

- If an Assistant summary disagrees with Evidence, **Evidence wins**.
  Integration and external attribution cite Evidence ids, never chat.
- A record that fails replay was not written by a conforming kernel:
  the kernel halts (`invalid_record`) and the record takes no effect.
- Tamper findings (edited, deleted, reordered, or corrupt chain;
  rewritten prefix; unreadable or missing anchor; unwritable closing
  record) halt the kernel for the rest of the process. Integrity halts
  cannot be cleared in-band; the log must be repaired out of band.
  Recorded kernel halts of the non-integrity kind are cleared only by
  a signed Operator `clear_halt`.
- A crash between an append and the anchor write is not tampering: on
  restart the kernel verifies the log, replays it, and moves the
  anchor forward.

## 5. Failure behavior (normative summary)

| Condition | Behavior |
|---|---|
| Constitution pin mismatch | Halt, no side effect |
| Hard stop; out of mission; illegal chain transition; unknown action type | Deny |
| Soft stop without operator authorization | Confirm, no side effect |
| Non-Operator Acceptance; Acceptance while a challenge is open; Integration without Acceptance | Deny |
| Assistant memory write recorded as a decision before Acceptance | Deny |
| Advisor calls a privileged tool | Deny |
| Unknown WorkUnit | Deny (`unknown_unit`) |
| Event log fails verification; a record fails replay | Halt, kernel-wide, recorded |
| Anchor unreadable or unwritable | Halt; never an exception |
| Waiver with no open challenge, or with an empty rationale | Deny |

Failure is a terminal, representable state, not an embarrassment to be
smoothed over: unsupported, unresolved, timed-out, approximate, and
failed outcomes are recorded as what they are and are never promoted
to assertions because a model produced a plausible answer
(REQ-MXK-VER-04).

## 6. Verification behavior

Verification is property-bounded (REQ-MXK-VER-01 to 05, ADR-MXK-0006).
A verifier establishes only the property it actually checked, against
identified evidence, with its limits named. Generation is not
verification: re-sampling, critique, or a second model does not become
independent assurance by being a separate inference. Structural
verification of this repository proves layout and bootstrap
conformance; it does not prove a model loaded, retained, or obeyed
anything (ADR-LAYOUT-0002).

## 7. Session behavior

A session in this repository starts by loading the canonical posture
(Mission, Mind, Morals via the harness adapters; MXM.md as the source)
and the active work record, and wraps by running verification and the
test suite and disclosing failures and limits. After context
compaction, posture and the work record are reloaded before work
resumes. The session tooling's exact contract is an interface; see
`02-systems-baseline/2.4-interfaces/`.

## 8. Not yet behavior

The runtime semantics of the future core API (cancellation,
streaming, reconnect and replay, idempotency, timeout, recovery) are
specified as requirements in the consolidation record (R-10,
ADR-MXM-0002) and are **not implemented**. They will be stated here
when the implementation exists, under WP-MXK-0014, and not before.

Human-Curated, AI-Enabled (HCAE)
