# ADR-MXK-0005 — Signed principal records and closed act outcomes

- **Status:** Decided
- **Extends:** ADR-MXK-0004
- **Work package:** `04-work-packages/WP-MXK-0007-act-outcomes/`
- **Decision authority:** Principal Operator, 2026-09-28 ("Proceed: Fix the follow-up Advisor
  findings in the kernel (WP-MXK-0007)")
- **Review:** Principal Advisor follow-up, cross-provider, 2026-09-28, recommendation REVISE. It
  found the effect derivation, key checks and anchor handling sound, and raised six narrower
  findings.

## Context

The follow-up review raised six findings:

1. A tool returning a non-mapping value raises past the port.
2. An evidence write that fails after a side effect is ignored, and the kernel reports
   success.
3. The logged decision of a failed side effect stays `allow`, while the caller is told
   `deny`.
4. An unsigned principal record with no effects passes replay.
5. The SPEC's anchor claims are inconsistent.
6. After an anchor-failure halt, a skipped effect's evidence obligation is never closed.

Finding 4 was reproduced; the others were confirmed by reading the code, except finding 1.
It did not reproduce, because the broker wraps every tool result in its own mapping before
the attribution merge.

## Decision

1. **Principal records are signed.**
   - An Operator or Advisor record is valid only if it carries a valid authorization whose
     key's principal is the recorded principal.
   - The one exception is the kernel's own denial of an act whose authorization failed: it
     records `unverified_<role>`, the problem, no principal and no effects.
   - Assistant records name no principal.
2. **Authorization and outcome are separate records.** The act record's decision is the
   kernel's authorization, written ahead of the effect with the state effects the
   authorization carries. Every act that owes evidence is closed by exactly one record,
   whose `outcome` is one of:
   - `done`;
   - `failed`, which carries the error;
   - `not_executed`, meaning the kernel halted while recording the act and skipped the effect;
   - `unknown`, meaning the process stopped before closing it. The next kernel holding the
     lock closes it.

   The Decision returned to the caller reports the outcome.
3. **An unrecordable outcome halts.** If the closing record cannot be written after the
   effect ran, the Decision is `halt` (`evidence_unwritable`), and the kernel stops for the
   rest of the process.
4. **Anchor claims reconciled.** The anchor detects truncation and rewriting, not appends.
   Validation proves a record is one a conforming kernel could write, not that one did;
   `kernel`-actor records are not authenticated. The log not being engine-writable is the
   only protection against validated but false appends.

## Alternatives considered

- **A full two-phase protocol.** The act records only intent, and a completion record
  carries the state transition. That would also make the tool's `unit` → `run` step
  conditional on success. It was not adopted: state effects follow authorization, not
  success, which matches the chain's meaning (a run was attempted), and the explicit
  outcome record makes the result unambiguous without moving state changes.

## Consequences

- All six findings are dispositioned (WP-MXK-0007 evidence).
- The mutation check now covers 40 defences, and each disabled defence fails the suite at the
  test aimed at it.
- Adding these checks first masked 10 older defences, because older forgeries lacked a
  principal or an outcome. The forgery helper now makes each forgery valid in every respect
  except the one under test.
- Stated limits, unchanged:
  - replay does not re-check host policy for Assistant acts;
  - `kernel`-actor records are not authenticated;
  - both rest on the log not being engine-writable.
- Whether the kernel is represented as an enforcement boundary remains the Principal
  Operator's decision.

Human-Curated, AI-Enabled (HCAE)
