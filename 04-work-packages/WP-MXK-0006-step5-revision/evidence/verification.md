# WP-MXK-0006 verification

## Advisor findings and their disposition

| Finding (Principal Advisor, 2026-09-28, REVISE) | Reproduced | Disposition | Tests |
|---|---|---|---|
| A signature covers the action, not the recorded effects | Yes: a waiver replayed as an abort | Replay derives effects and decision kinds per action type | A a_valid_signature_cannot_carry_another_acts_effects (53), a_signed_act_must_also_be_one_the_kernel_would_record (3) |
| `clear_halt` and open do not check the action type | By code reading | Covered by derivation; `clear_halt` kernel-scope; open type-bound | same, plus A forged_record[intercepted_*] |
| Small-order public keys verify arbitrary messages | Yes: the identity key, with R = identity and S = 0 | Small-order keys and nonces rejected; subgroup check; the registry refuses weak keys | E small_order (orders 1/2/4/8), subgroup; Z weak keys |
| "Canonical JSON" is unspecified and allows NaN | By code reading | Defined signing domain; the SPEC names it the MxM signing serialization | Z domain (7), fixed serialization, malformed envelope |
| Open with a null scope is defaulted after signing | By code reading | `opening_act` resolves the opening, the signer signs it, replay requires it exactly | A an_open_must_sign_the_resolved_unit |
| Evidence and halt records barely validated | By code reading | Kernel-written; linked once to an awaiting act | A evidence_records_must_answer_an_act (5) |
| Anchor failure applies state; a crash leaves the anchor behind | Partly. A lagging anchor was not treated as tampering: `verify` flags only a head behind the anchor, or a changed hash at the anchor. The anchor was simply never moved forward. | Lag moved forward on catch-up; a missing anchor halts; the SPEC states exactly what applies on failure | A a_lagging_anchor..., a_deleted_anchor_halts, blocker1 |
| "Never raise" is overstated | By code reading | Side effects recorded and denied; log read errors halt; the SPEC names what still raises | A a_failing_memory_write..., a_failing_tool... |
| Host policy is not re-checked on replay | Accepted as a limit | Stated in SPEC §7 and §8 and in ADR-MXK-0004; the log not being engine-writable is a deployment precondition | — |

## Suites

- `python3 -m pytest -q 05-mxm-construct`: 184 passed, 3 xfailed (the strict F-08, F-18 and
  F-20 gaps).
- The stdlib runner on the enforcement suites reports 149 passed and 3 xfailed, matching pytest
  and pinned by the release test.

## Mutation check

The script is `evidence/mutations.py` (run from `05-mxm-construct/means/`).
Thirty-three defences were each disabled in a scratch copy, and all 33 fail the suite.

The first run caught 29. The 4 misses were tests that reached a different check first:

- the kernel-scope `clear_halt` rule;
- decision kinds per action type;
- re-anchoring on catch-up;
- the waiver rationale on replay.

Isolating tests were added for each, and each now catches its mutation.

Human-Curated, AI-Enabled (HCAE)
