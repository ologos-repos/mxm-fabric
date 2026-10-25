# Enforcement core: SPEC-to-test traceability

This is the worklist toward the release artifact for the enforcement core. It was reconciled
in the source meta-harness (WP-TMH-0016, R-14) and continues here; WP-MXK-0005 adds the
authorization and event-log rows. The goal is two tests for every normative item: a positive
test showing the authorized path works, and a negative test showing the unauthorized path
fails closed. The rows below show where that holds and where it does not yet.

Test file abbreviations:

- `C` = `tests/test_conformance.py`
- `A` = `tests/test_adversarial.py`
- `E` = `tests/test_ed25519.py`
- `Z` = `tests/test_authz.py`

The tests use fixed test keys (`tests/mxm_testing.py`). They prove how the kernel decides
given a signature, and that the log carries no authority-bearing change without one. They do
not prove that a deployment keeps signing keys, the trust registry and the anchor out of the
engine's reach (SPEC §7, §8).

**Mutation check.** Each defence was disabled in turn in a scratch copy, 40 in all (WP-MXK-0007):

- **Authorization:** signature, role, unit, pin and act binding; single use; expiry; key
  retirement.
- **Replay:** replay authorization; effect ownership; transition checks; effects derived
  from the action; decision kinds per action type; per-type preconditions; kernel-scope
  `clear_halt`.
- **Opening and evidence:** new unit id on open; the resolved opening; evidence linkage and
  authorship; halt authorship; signed principal records and principal attribution; closing
  outcomes (validation, `not_executed`, `unknown`, unwritable evidence).
- **Chain and anchor:** chain, anchor and prefix checks; anchor lag and loss; the port halt
  check.
- **Cryptography and encoding:** Ed25519 S < L; small-order rejection; the subgroup and
  trust-registry key checks; the signing domain.

The suite fails for every one, each at the test aimed at it. The records are in
`04-work-packages/WP-MXK-0005-authorizations-event-log/evidence/` (21) and
`04-work-packages/WP-MXK-0006-step5-revision/evidence/` (33) and
`04-work-packages/WP-MXK-0007-act-outcomes/evidence/` (40).

Status meanings:

- **Verified:** both tests exist and pass.
- **Tracked gap:** the negative is a strict xfail naming its recommendation. It flips to an
  unexpected pass, which fails the suite, when the fix lands.
- **Pending:** no test yet.

## SPEC §11 conformance

| # | Requirement | Positive | Negative | Status |
|---|---|---|---|---|
| 1 | Assistant cannot obtain ALLOW on send/deploy/pay/public | C happy_path | C s11_1; A f16 unlock_privileged_tools | Verified |
| 2 | Assistant cannot advance to Acceptance | C s11_3 (Operator accepts) | C s11_2; A f16 payload_cannot_claim | Verified |
| 3 | Acceptance blocked while an unwaived challenge exists | C s11_3 (after waiver) | C s11_3; A f19 kernels_sharing_a_log | Verified |
| 4 | Pin change mid-unit halts | C happy_path | C s11_4; A p3 on_disk_edit | Verified |
| 5 | Disposition flushes scratch, keeps durable | C s11_5 | — | Pending negative |
| 6 | Attribution is kernel-applied | C s11_6 | — | Pending negative |
| 7 | Advisor has no privileged tools | — | C s11_7 | Pending positive |
| 8 | Registered Method blocks freeform tools | C s11_8 (method_run) | C s11_8 | Verified |
| 9 | No Assistant proposal field obtains an Operator or Advisor act | C happy_path | A f16 payload_cannot_claim, unlock_privileged_tools | Verified |
| 10 | Operator/Advisor acts need a valid, single-use, act-bound authorization | C every_act_is_one_chained_record; C principal_cli | A f16 open_package_requires_a_signed_operator_authorization, operator_port_denies_any_authorization (11 cases), single_use_across_kernels, retired_key, advisor_port_requires; E (all) | Verified |
| 11 | A tampered event log halts the kernel | A f17 the_log_is_one_hash_chain | A f17 tampered_log_halts (3 cases), halted_kernel_writes_one_halt_record, halt_persists_in_process | Verified |
| 11a | Truncation and recomputation are detected | A f17 anchor_detects_truncation, recomputed_chain_is_detected_with_an_anchor, running_kernel_detects_a_changed_prefix (2 cases), recomputed_signed_record_is_detected | A f17 without_an_anchor_unsigned_evidence_can_be_recomputed (documents the limit) | Verified with an anchor the engine cannot write; without one, only for signed records or a running kernel |
| 12 | State is rebuilt from the log; kernels sharing it see each other's commits | A f19 units_survive_restart, kernels_sharing_a_log; MCP stdio_round_trip | A f16 single_use_across_kernels | Verified |
| 13 | A record a conforming kernel would not write halts every kernel that replays it | A the_legitimate_pairings_still_replay | A forged_record_in_the_log_halts_every_kernel (10 cases); a_valid_signature_cannot_carry_another_acts_effects (53 cases); a_signed_act_must_also_be_one_the_kernel_would_record (3); evidence_records_must_answer_an_act (5); blocker5 in_process_bypass | Verified |
| 14 | Trust keys are valid prime-order-subgroup keys; small-order keys and nonces never verify | E rfc8032_known_answers | E small_order_keys_and_nonces_never_verify, key_outside_the_prime_order_subgroup; Z trust_registry_refuses_weak_keys | Verified |
| 15 | Signed bodies stay in the MxM signing domain; the opening is signed resolved | Z the_signing_serialization_is_fixed | Z values_outside_the_signing_domain (7 cases), envelope_outside_the_domain_is_malformed; A an_open_must_sign_the_resolved_unit | Verified |
| 16 | Principal records are signed (or are the kernel's unverified denial) and name their key's principal | A the_kernels_own_unverified_denials_still_replay | A a_principal_record_is_signed_or_is_the_kernels_unverified_denial (5 cases) | Verified |
| 17 | Every act owing evidence is closed once: done, failed, not_executed or unknown; an unwritable closing record halts | A every_outcome_is_closed_exactly_once | A a_closing_record_must_state_a_consistent_outcome (3), a_process_that_stops_mid_effect_leaves_an_unknown_outcome, an_unwritable_evidence_record_halts, blocker1 unwritable_anchor (not_executed) | Verified |

## SPEC §10 failure behavior

| Condition | Test | Status |
|---|---|---|
| Constitution pin mismatch → Halt | C s11_4 | Verified |
| Hard stop → Deny | C s11_1 | Verified |
| Soft stop without operator_ok → Confirm | — | Pending |
| Out of mission → Deny | A f08 (xfail, R-08) | Tracked gap |
| Illegal chain transition → Deny | — | Pending (port); replay: A forged_record[illegal_transition] |
| Non-operator Acceptance → Deny | C s11_2 | Verified |
| Acceptance while challenge open → Deny | C s11_3 | Verified |
| Integration without Acceptance → Deny | — | Pending |
| Assistant durable memory before Acceptance → Deny | — | Pending |
| Advisor privileged tool → Deny | C s11_7 | Verified |
| Unknown action type → Deny | — | Pending |
| Unknown WorkUnit → Deny | A unknown_unit | Verified |
| Act without a valid authorization → Deny | A f16 operator_port_denies_any_authorization | Verified |
| Waiver without an open challenge or a rationale → Deny | A r06_waiver | Verified |
| Event log fails verification → Halt | A f17 tampered_log_halts | Verified |
| Record fails replay → Halt | A forged_record_in_the_log_halts_every_kernel | Verified |
| Anchor unreadable / unwritable → Halt, never raise | A blocker1 (2 tests) | Verified |
| Anchor missing beside a non-empty log → Halt | A a_deleted_anchor_halts | Verified |
| Anchor lagging after a crash → moved forward, no halt | A a_lagging_anchor_is_moved_forward | Verified |
| Failed memory write → recorded, Deny, no raise | A a_failing_memory_write_is_recorded_and_denied | Verified |
| Failed tool → recorded receipt, Deny | A a_failing_tool_is_recorded_and_denied | Verified |

## Release blockers (source meta-harness issue 36)

| Blocker | Closed by | Test |
|---|---|---|
| 1 Malformed halt marker or anchor raises; anchor I/O unhandled | No halt markers; anchor faults become recorded halts | A blocker1 (2 tests) |
| 2 Halt, evidence, anchor and memory state not transactional | One log, one lock per proposal, write-ahead act records | A f19 kernels_sharing_a_log; A f17 tests |
| 3 Units do not survive restart; halt marker deletable | Units and halts are chain records | A f19 units_survive_restart; A f17 with_an_anchor_the_halt_survives |
| 4 `open_package` raises; other ports return Decisions | `open_package` returns a Decision | A f16 open_package_requires; C open_package_returns_a_decision |
| 5 Internal handlers reachable in-process | Authority is validated on every record, before append and on replay | A blocker5 in_process_bypass; A forged_record (10 cases) |

## Tracked gaps from the Findings and Recommendations Report

| Finding | Test | Recommendation |
|---|---|---|
| F-08 Mission scope substring match | A f08 (strict xfail) | R-08 |
| F-18 vacuous evidence gate | A f18 (strict xfail) | R-18 |
| F-19 units lost on restart | A f19 units_survive_restart (promoted, WP-MXK-0005) | R-19, closed |
| F-20 Assistant-authored durable decisions | A f20 (strict xfail) | R-11 |

## Verification boundary (WP-MXK-0009)

These rows implement REQ-MXK-VER-01 through REQ-MXK-VER-05 and SPEC §8A. Existing controls are
credited only for the property they actually establish. The general verification object and
assurance gate are tracked gaps until executable tests exist.

| Requirement | Existing evidence/control | Status / next control |
|---|---|---|
| VER-01 Independent assurance | Separate Operator/Advisor credentials and kernel receipts demonstrate architectural separation for authority/action paths | **Tracked gap:** no generic gate prevents a model from labeling its own factual/computational claim verified |
| VER-02 Computational authority separation | SPEC §§7–8; C/A authorization, receipt, replay and forged-record tests | **Verified for authority and external-effect records;** general factual claims remain outside kernel enforcement |
| VER-03 Explicit verification boundary | SPEC §7 states signature limits; §8 distinguishes decision/outcome and anchor limits | **Tracked gap:** no typed Verification record requiring property/evidence/limitations |
| VER-04 Resource/assurance honesty | Explicit failed/not_executed/unknown outcomes for action evidence | **Verified for action outcomes; tracked gap** for generic unsupported/unresolved/timeout/approximate claim states |
| VER-05 System-boundary claims | SPEC §8A normative documentation rule; WP-MXK-0008 claim ledger | **Tracked gap:** documentation/schema control, not runtime enforcement |

### New conformance items

| # | Requirement | Positive | Negative | Status |
|---|---|---|---|---|
| 18 | Generating inference cannot solely self-verify a claim requiring independent assurance | — | — | Pending |
| 19 | Verification states property, evidence/mechanism, limitations | — | — | Pending |
| 20 | Unsupported/unresolved/timeout/approximate/failed cannot become authoritative assertions | Existing action-outcome tests cover failed/not_executed/unknown only | — | Partial / Pending generic control |
| 21 | Generated prose cannot substitute for authoritative state or effect receipt | C/A authority, event-log and receipt tests | A forged-record and actor-claim tests | Verified for kernel-managed authority/effects |
| 22 | Capability/impossibility claim identifies component vs composite boundary | — | — | Pending documentation/schema control |
