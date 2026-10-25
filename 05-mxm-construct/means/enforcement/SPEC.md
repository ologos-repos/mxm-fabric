# MxM Kernel Specification

**Title:** Multi-Mode Meta-Harness — Enforcement Kernel  
**Status:** Binding v0.2. Reconciled in the source meta-harness WP-TMH-0016; continues in this repository (WP-MXK line). v0.2: signed act-bound authorizations and one event log (ADR-MXK-0003, revised by ADR-MXK-0004 and ADR-MXK-0005)  
**Companion:** MxM diagram and narrative  
**Implementation:** `05-mxm-construct/means/enforcement/mxm`  

---

## 0. One line

The aide holds no authority of its own. The will comes from the operator.  
This document defines the mechanism that makes that sentence true.

---

## 1. Purpose

MxM is a harness that loads *before* work begins. A model is untrusted compute. The kernel is trusted code. Side effects exist only if the kernel commits them.

This spec binds:

- the Principal Governance Triad
- the six surfaces (Mind, Morals, Mission always-loaded; Memory, Methods, Means pointer-shaped)
- the work chain and its gates
- mutation rights, failure behavior, evidence, attribution

If a behavior is not in this spec, the kernel must refuse it.

---

## 2. Non-goals

- Making the model “reason more morally” by prompt alone
- Enforcing the *quality* of Mind (questioning assumptions) as a hard gate
- Replacing the Operator with an autonomous closer
- Hot-reloading constitution from a directory the Assistant can write
- Letting Assistant and Advisor share write credentials

---

## 3. Threat model

The Assistant may:

- propose illegal tool calls
- claim Acceptance in text
- invent Memory
- try to rewrite Mind, Morals, or Mission
- retry a denied call with different wording
- impersonate the Advisor or the Operator

The kernel assumes all of the above will happen. Enforcement is at side-effect boundaries, not in generated prose.

Trusted:

- The Operator's and Advisor's signing keys, held in their own processes and never by the engine
- The trust registry (their public keys) and constitution files on disk, owned by the Operator
- The log anchor, where the engine cannot write
- Kernel source the Assistant cannot write
- Event-log appends performed by a conforming kernel (every kernel re-validates every record on replay, so a record written any other way halts the kernel instead of taking effect)

Untrusted:

- every Assistant proposal
- every Advisor *recommendation* (the challenge record is trusted once the kernel writes it; the prose is not)
- model summaries of what it “did”

---

## 4. Principals

| Principal | Kind | Authority |
|---|---|---|
| Principal Operator | Human | Terminal. Decides. Signs Acceptance. Publishes constitution. |
| Principal Assistant | AI | Acts. One identity across workers. Proposes; never commits privileged effects. |
| Principal Advisor | AI | Challenges. Independent review. May block Acceptance. Holds no send/deploy tokens. |
| Lead Operator | Human | Sits *beneath* the triad, not as peer. Executes Operator will inside a domain. |
| Architecture Authority | Human | Sits *beneath* the triad, not as peer. Owns kernel and constitution schema. Cannot override Operator Acceptance. |

v0.1 encodes three actors on every call: `operator`, `assistant`, `advisor`. Lead Operator and Architecture Authority are organizational roles; they use the `operator` actor when acting under delegation recorded in Evidence.

### Identity rule

Assistant workers inherit posture (constitution pin + WorkUnit scope). They do not inherit Operator or Advisor credentials. “One identity, many workers” means shared pin and mission, isolated execution tokens.

---

## 5. Objects

### 5.1 Constitution

Always-loaded. Present before the first turn. Frozen for the life of a WorkUnit.

```
Constitution {
  version: string
  mind: string            # reasoning canon, rendered into Assistant context
  mission: {
    identity: string
    scope: string
    role: string          # must include: aide, not peer
  }
  morals: Morals
}
```

**Pin.** `pin = SHA-256(canonical JSON of {version, mind, mission, morals})`.  
Stored on the WorkUnit at creation. Every `propose` re-hashes the loaded constitution and halts on mismatch.

**Mutation.** Only the Operator (or Architecture Authority under recorded delegation) may publish a new constitution file. The Assistant has no write path. A new version does not apply to in-flight WorkUnits; they keep their pin or are aborted by the Operator.

### 5.2 Morals

```
Morals {
  hard_stops: Rule[]      # DENY
  soft_stops: Rule[]      # CONFIRM (Operator must approve this action)
  trust_scope: {
    tools: string[]
    identities: string[]  # usually ["assistant"] for acting tools
    data_classes: string[]
  }
  attribution: string     # kernel stamp; default "Human-Curated, AI-Enabled"
}
```

```
Rule {
  effect: string          # tool name or effect class: send | deploy | memory_write | constitution_write | ...
  match: object           # subset match against Action fields (channel, env, target, ...)
}
```

**Evaluation order:** hard stop → tool not in trust_scope → soft stop → ALLOW.

**Invariant:** no channel outranks the Operator. Effects in class `send`, `deploy`, `public`, `pay` are hard-stopped unless a Rule explicitly lists them as soft-stop *and* the Operator has set `operator_ok` on that Action. v0.1 default constitution hard-stops those classes.

### 5.3 Action

```
Action {
  type: "tool" | "advance" | "memory_write" | "method_run" | "challenge" | "accept" | "waive_challenge"
  actor: "operator" | "assistant" | "advisor"
  tool?: string
  effect?: string
  args: object
  channel?: string
  env?: string
  target?: string
  to?: ChainState          # for advance
  operator_ok: bool        # only meaningful if actor is operator or kernel copied a prior Operator grant
}
```

### 5.4 WorkUnit

```
WorkUnit {
  id: string
  package_id: string
  pin: string
  scope: string
  state: ChainState
  advisor_challenge: Challenge | null
  challenge_waived: bool
  acceptance: Acceptance | null
  method_id: string | null
  ad_hoc: bool
}
```

### 5.5 Work chain

```
package → unit → run → evidence → acceptance → integration → disposition
```

Legal transition: exactly one step forward. No skips. No backwards except Operator `abort` (terminal, not a reverse).

| From | To | Gate |
|---|---|---|
| (create) | package | Operator-signed package exists |
| package | unit | Operator or kernel with package scope; constitution pinned |
| unit | run | Means bound; if a Method exists for this unit type it must be selected unless Operator marks ad_hoc |
| run | evidence | At least one kernel Evidence record of kind receipt, deny, or note |
| evidence | acceptance | Actor is operator. If advisor_challenge is set and not waived, blocked |
| acceptance | integration | acceptance present |
| integration | disposition | integration recorded; then Memory commit/flush |

**Acceptance** is an Operator act. The kernel records `{actor: operator, unit_id, ts, pin}`. Model text containing “accepted” is not Acceptance.

**Advisor station.** After Evidence, before Acceptance. Advisor writes a Challenge or an explicit Clear. Challenge locks Acceptance until Operator waives or constitutionally supersedes.

---

## 6. Surfaces — binding notes

Each surface has: owner, load time, mutation rule, failure behavior.

### 6.1 Mind

| | |
|---|---|
| Owner | Operator / Architecture Authority |
| Load | Always, before first turn; rendered into Assistant system context |
| Mutation | New constitution version only; in-flight pin unchanged |
| Failure | Not mechanically scored. Failure of *process* is enforced via Methods (script over judgment) and Evidence (claims without receipts are non-evidence) |

Mind text SHOULD require: define terms, question assumptions, update on evidence. The kernel does not parse those sentences.

### 6.2 Morals

| | |
|---|---|
| Owner | Operator |
| Load | Always; compiled to `morals.check(action)` |
| Mutation | Constitution publish only |
| Failure | Hard stop → DENY + halt side effect + Evidence. Soft stop → NeedsOperator, no side effect. Trust-scope miss → DENY |

### 6.3 Mission

| | |
|---|---|
| Owner | Operator |
| Load | Always; `scope` copied onto WorkUnit |
| Mutation | Constitution publish only |
| Failure | Tool or advance whose declared target is outside `scope` → DENY (`out_of_mission`) |

v0.1 scope check is string containment against `action.target` or `action.args.scope` when present. Empty target is allowed only for tools listed as `scope_optional`.

### 6.4 Memory

| | |
|---|---|
| Owner | Kernel; Operator may inspect and prune |
| Load | Pointer; loaded when WorkUnit is active and on Disposition |
| Mutation | Kernel `memory.write` after policy check. Assistant proposes `memory_write`. Durable kinds: `decision`, `acceptance`, `method`. Scratch flushes on Disposition |
| Failure | Unaccepted run artifacts cannot be written as `decision`. Auto-flush drops scratch |

### 6.5 Methods

| | |
|---|---|
| Owner | Architecture Authority registers; Operator enables per unit type |
| Load | Pointer; loaded when unit type has a registered Method |
| Mutation | New numbered file in `methods/` owned outside Assistant write paths. Promotion of ad-hoc work to Method requires Operator Acceptance of a `method` Memory record |
| Failure | If Method exists and unit is not `ad_hoc`, freeform `tool` runs other than the Method entrypoint → DENY (`method_required`) |

Methods are importable Python callables registered by id. The Assistant does not `exec` source.

### 6.6 Means

| | |
|---|---|
| Owner | Kernel broker |
| Load | Pointer; bound at `unit → run` |
| Mutation | Tool registry is kernel code. Credentials never enter model context |
| Failure | Unknown tool → DENY. Privileged tool without Operator grant → DENY or CONFIRM |

---

## 7. Kernel API

The actor is bound by the entrypoint, never read from the proposal (reconciliation R-16).

```
kernel.assistant_propose(unit_id, proposal: dict) -> Decision                  # the ONLY model-facing entrypoint
kernel.operator_propose(unit_id, action, authorization) -> Decision            # operator surface only
kernel.advisor_propose(unit_id, action, authorization) -> Decision             # advisor surface only
```

`assistant_propose` discards any `actor` or `operator_ok` in the proposal and acts as
`assistant`.

**Authorizations (ADR-MXK-0003).** An Operator or Advisor act needs an authorization: an
Ed25519 signature (RFC 8032) by a key in the kernel's trust registry, over a body that names:

- the role, which must match the key's role and the port;
- the WorkUnit (for `open_package`, the id the new unit will get);
- the act itself: every field of the proposed action except the actor. For `open_package`
  the act is the fully resolved opening from `kernel.opening_act(...)`: scope, unit type,
  ad hoc, required method and constitution version, with no default applied after signing;
- the constitution pin;
- a unique id and a validity window.

The kernel denies `unverified_operator` / `unverified_advisor`, with the specific problem as
the payload (`missing`, `malformed`, `unknown_key`, `wrong_role`, `key_retired`,
`bad_signature`, `wrong_unit`, `wrong_pin`, `act_mismatch`, `expired`, `replayed`), unless
all of these hold:

- the signature verifies;
- every binding matches the act being proposed;
- the window contains the kernel's clock (with 60 s of skew);
- the id has not been spent.

An authorization is spent when the kernel records the act that carries it, whatever that
act's decision. The kernel holds public keys only. A key may be retired at a log position
(`valid_through_seq`): records up to that position still verify, and nothing later does.

The signed body uses the MxM signing serialization. It is not a general canonical-JSON
scheme; it is deterministic only over a restricted value domain:

- objects with string keys, arrays, strings, booleans, null;
- integers of magnitude below 2^53;
- no floats, NaN or infinities.

Objects are written with keys sorted by Unicode code point, no whitespace, and unescaped
UTF-8. A body outside that domain cannot be signed, and verifies as `malformed`.

Verification rejects:

- non-canonical point and scalar encodings (S >= L);
- small-order public keys and nonces.

Trust-registry keys must also lie in the prime-order subgroup, and a registry containing any
other key is refused when loaded.

**What this does and does not establish.** A trusted key's signature proves that the key
holder authorized this action on this unit under this constitution, once. The signature
covers the action, not the recorded effects. What makes the effects authorized is that replay
derives them from the action and its decision, and refuses any record whose effects differ
(§8). Taken together, an Operator or Advisor effect in the log is exactly the effect of an
action its role's key signed. The same proof does not reach further:

- The kernel cannot tell who holds a key.
- Keeping signing keys in the principals' own processes, and the trust registry,
  constitution and anchor out of the engine's reach, is the deployment's job.
- In-process code can still mutate the kernel's in-memory cache. It cannot make the log
  carry an authority-bearing change that way, and a restarted kernel, or any other kernel
  on the log, rebuilds state from the log alone.
- Replay does not re-evaluate host policy (Morals, trust scope, the tool broker, Methods)
  for Assistant acts. It cannot, because that policy is host configuration. An engine that
  can write the log can therefore record an allowed Assistant act that policy would have
  denied, together with a receipt for it. No tool runs, but the unit's state and Evidence
  are falsified. Only the deployment precondition (the log is not engine-writable)
  prevents that. An anchor does not: it detects truncation and rewriting, not appends, and a
  kernel moves a lagging anchor forward over any appended record that passes validation.
  Validation proves that a record is one a conforming kernel could write. It does not prove
  that a kernel wrote it; records naming the `kernel` actor are not authenticated.

`Decision.kind` ∈ `allow | deny | confirm | halt | advanced | accepted | challenged | waived | opened | cleared`.

Operator-facing helpers (each takes the authorization for exactly its act):

```
kernel.opening_act(package_id, scope, unit_type, ad_hoc) -> dict                        # the resolved act to sign
kernel.open_package(package_id, authorization, scope, unit_type, ad_hoc) -> Decision   # kind "opened"; unit_id from the authorization
kernel.accept(unit_id, authorization)
kernel.waive_challenge(unit_id, note, authorization)   # needs an open challenge and a non-empty rationale
kernel.abort(unit_id, authorization)
kernel.clear_halt(authorization)                       # clears a recorded kernel halt; kernel scope
```

Advisor-facing:

```
kernel.challenge(unit_id, note, authorization)
kernel.clear_challenge(unit_id, authorization)  # advisor attests no challenge; does not accept
```

`mxm_principal.py keygen` creates a key and adds it to the trust registry.
`mxm_principal.py act` signs and submits one act from the principal's own process.

An unknown `unit_id` is denied (`unknown_unit`), not raised.

## 8. Evidence and state: one event log

All kernel state and all Evidence are records in one append-only, hash-chained JSONL log
(`events.jsonl` under the data root), written in the kernel's audit-chain format
(`mxm/audit_chain.py`). Each record has:

```
{ "v", "seq", "ts", "prev_hash", "hash", "kind", "unit_id", "actor", "payload",
  "operator", "engine", "run_id" }
```

`kind` is one of:

- `act`: one record per proposal. It carries the action, the authorization if any, the
  verified principal, the decision and its effects.
- `receipt`: a tool's or method's result.
- `memory`: a memory write or commit.
- `halt`: scope `unit` or `kernel`.
- `repair`: a crash-truncated trailing record was discarded.

WorkUnits, transitions, challenges, waivers, acceptances, halts and spent authorizations
exist only as these records. Every kernel rebuilds them by replaying the log, so units
survive a restart, and kernels sharing a data root see each other's commits.

**Transactions, decisions and outcomes.** A proposal holds an exclusive lock from reading
the log to appending its records. Two things are recorded separately.

**The act record's decision is the kernel's authorization.** It is written ahead of any side
effect, together with the state effects the authorization carries (for a tool, `unit` →
`run`).

**For an act that owes evidence, exactly one closing record states what happened.** Tool and
method runs owe a `receipt`; memory writes and the disposition commit owe a `memory` record.
The closing record's `outcome` is one of:

- `done`
- `failed`: carries the error. The Decision returned to the caller is then `deny`
  (`tool_failed`, `method_failed`, `memory_write_failed`, `memory_commit_failed`), while
  the logged act stays an authorized attempt.
- `not_executed`: the kernel halted while recording the act (for example, the anchor could
  not be written) and deliberately skipped the effect.
- `unknown`: the process that recorded the act stopped before its closing record. The next
  kernel to open the log, holding the lock, finds the obligation still open and closes it.
  The effect may or may not have happened.

If a closing record cannot be written after the effect ran, the effect's outcome is no
longer provable from the log. The Decision is a `halt`, and the kernel stops for the rest of
the process (`evidence_unwritable`). The next kernel closes the obligation as `unknown`. A
failed acceptance memory row is reported in the payload; the acceptance itself is the log
record.

**Validation.** Every record is validated before it is appended, and again by every kernel
that replays it:

- **Effects:** an act's effects must be exactly the effects its action type produces for
  its recorded decision, derived from the action and the current state. Each action type
  may record only its own effecting decisions (for example, a waiver only `waived`). A
  `deny` or `confirm` records none.
- **Authorization:** an Operator or Advisor record must carry an authorization that
  verifies against the trust registry for that role, is bound to the recorded act, unit
  and pin, was not spent by an earlier record, and whose key's principal is the recorded
  principal. The one exception is the kernel's own denial of an act whose authorization
  failed (`unverified_operator` / `unverified_advisor`), which records the problem, no
  principal and no effects. An Assistant record names no principal.
- **Ownership:** each authority-bearing effect (open, acceptance, waiver, abort,
  clear_halt; challenge) must come from the role that owns it.
- **Transitions:** state changes must be legal steps of the work chain. Per-type
  preconditions hold too: a waiver has an open challenge and a rationale, a clear finds no
  challenge, `clear_halt` is kernel-scope and finds a kernel halt, and an open names a new
  unit.
- **Evidence:** `receipt` and `memory` records must be written by the kernel and answer,
  once, an earlier act that owes that kind of evidence. They must state one outcome, and
  carry an error exactly when it is `failed`. `halt` records must be written by the kernel.

A record that fails replay was not written by a conforming kernel. It halts the kernel
(`invalid_record`) and takes no effect.

**Halts.** Chain findings (edited, deleted, reordered, corrupt) halt the kernel
(`evidence_tampered`). So does a change to a prefix the kernel already applied
(`evidence_rewritten`), an unreadable anchor (`anchor_unreadable`), a configured anchor
missing beside a non-empty log (`anchor_missing`), and an I/O error reading the log
(`log_unreadable`), and a closing record that cannot be written (`evidence_unwritable`). The halt
lasts for the rest of the process, and a `halt` record is appended once, so it survives a
restart. A constitution mismatch halts the unit, as a record.

When the anchor cannot be written, the act being recorded stays in the log with its state
change (the log is authoritative), the kernel records a kernel halt (`anchor_unwritable`),
and the act's external side effect does not run. A crash between an append and the anchor
write leaves the anchor behind a valid log. That is not tampering: the next kernel verifies
the log, replays it, and moves the anchor forward. Recorded kernel halts are cleared only by
a signed Operator `clear_halt`. Integrity halts cannot be cleared in-band; the log must be
repaired out of band.

What still raises: I/O errors acquiring the log lock (`OSError`), and invalid arguments to
the Python API, such as unknown proposal fields (`TypeError`), which the MCP layer reports
as a refused tool call.

**Anchor and limits.** With an anchor (the log head, kept where the engine cannot write),
tail truncation and whole-chain recomputation are detected. An anchor does not prevent
appends: a party that can write the log can append records that pass validation. That
means Assistant-level acts that host policy would deny (see §7), and it does not mean
Operator or Advisor effects. Without an anchor, a restarted kernel additionally cannot
detect truncation, or recomputation of records that carry no signature. It still detects
recomputation of any signed record, because the signature no longer verifies. A running
kernel also detects any change to a prefix it has already applied.

If Assistant summary disagrees with Evidence, Evidence wins. Integration and external
attribution MUST cite Evidence ids, not chat.

## 8A. Verification boundary

A model-generated statement is a proposal or claim, not verification merely because the model
expresses confidence, critiques itself, repeats the result, or another generative inference agrees.

For a verification result used to support a consequential factual, computational, or action claim,
the system SHALL identify:

- the property checked;
- the evidence source or mechanism used;
- material limitations of that check.

A verification result has no authority beyond that property. A receipt can establish what the
kernel recorded about an attempted external effect; it does not by itself establish every factual
claim contained in the tool's returned payload. A signature establishes authorization under §7;
it does not establish truth of the signed proposition.

Where qualified independent verification is required and available, the generative inference path
that produced the claim SHALL NOT be its sole verifier. Independence is functional: another sample,
prompt, model, or agent is not automatically an independent verifier merely because it is separate.

When required computation or verification cannot be completed within the supported resource or
assurance boundary, the result remains explicitly unresolved, unsupported, timed out, approximate,
or failed as applicable. Generated plausibility does not promote such a result to authoritative
state.

Capability and impossibility claims SHALL name their system boundary. A bound on a transformer,
model invocation, verifier, tool, or executor is not a bound on the composite harness unless a
separate argument establishes that system-level bound.

**Implementation status.** Existing authorization, receipt, event-log, and replay controls enforce
parts of these semantics for actions and recorded outcomes. A general typed verification object and
assurance-level gate are not implemented in v0.2. Conformance items 18–22 track that work explicitly.

## 9. Attribution

Every artifact leaving the harness (file written at Integration, Memory `decision`, exported receipt) is stamped by the kernel with `morals.attribution` (default `Human-Curated, AI-Enabled`). The model cannot choose a different stamp.

---

## 10. Failure behavior (normative)

| Condition | Behavior |
|---|---|
| Constitution pin mismatch | `Halt`, no side effect |
| Hard stop | `Deny`, WorkUnit remains in current state, Evidence recorded |
| Soft stop without operator_ok | `Confirm`, no side effect |
| Out of mission | `Deny` |
| Illegal chain transition | `Deny` |
| Non-operator Acceptance | `Deny` |
| Acceptance while challenge open | `Deny` (`blocked_by_advisor`) |
| Integration without Acceptance | `Deny` |
| Assistant memory write as `decision` before Acceptance | `Deny` |
| Advisor calls privileged tool | `Deny` |
| Unknown action type | `Deny` |
| Unknown WorkUnit | `Deny` (`unknown_unit`) |
| Operator or Advisor act without a valid, unspent authorization for exactly that act | `Deny` (`unverified_operator` / `unverified_advisor`; payload names the problem) |
| Event log fails verification | `Halt` (`evidence_tampered`), kernel-wide, recorded |
| A record fails replay validation | `Halt` (`invalid_record`), kernel-wide, recorded |
| Anchor unreadable / unwritable | `Halt` (`anchor_unreadable` / `anchor_unwritable`); never an exception |
| Operator waiver with no open challenge, or empty rationale | `Deny` (`no_open_challenge` / `waiver_requires_rationale`) |

After Deny, the Assistant may propose a legal alternative. The kernel does not retry.

---

## 11. Conformance

A kernel conforms to MxM v0.1 if all of the following pass:

1. Assistant cannot obtain ALLOW on a hard-stopped send/deploy/pay/public effect.
2. Assistant cannot advance `evidence → acceptance`.
3. Acceptance while an unwaived Challenge exists is denied.
4. Pin change mid-unit causes Halt.
5. Disposition flushes scratch and keeps acceptance/decision/method records.
6. Attribution stamp is kernel-applied.
7. Advisor broker has no privileged tool tokens.
8. Registered Method blocks freeform tools unless `ad_hoc` was set by Operator.
9. No field of an Assistant proposal can obtain an Operator or Advisor act.
10. Operator and Advisor acts need a valid, single-use authorization bound to exactly that act, unit and pin.
11. A tampered event log halts the kernel.
12. State is rebuilt from the event log: units survive restart, and kernels sharing a log decide against each other's commits.
13. A record that a conforming kernel would not write (unsigned or mis-signed principal effect, spent authorization, effect from the wrong role, illegal transition) halts every kernel that replays it.\n14. A consequential claim requiring qualified independent verification cannot be marked verified solely by its generating inference path.\n15. A verification record identifies the property checked, evidence source or mechanism, and material limitations.\n16. Unsupported, unresolved, timed-out, approximate, and failed verification states cannot be promoted to authoritative assertions.\n17. Generated prose cannot substitute for authoritative state or an external-effect receipt.\n18. Computational capability/impossibility metadata distinguishes component from composite-system boundaries.

`tests/test_conformance.py` (positive) and `tests/test_adversarial.py` (negative) are the
executable form of this section; `TRACEABILITY.md` maps each item to its tests.

---

## 12. Versioning

- Spec version and constitution `version` are independent.
- WorkUnits record both.
- Breaking schema changes increment spec major and require Architecture Authority + Operator publish.

---

## 13. Glossary

- **Pin** — hash binding a WorkUnit to one constitution.
- **Propose** — untrusted request. Not a side effect.
- **Commit** — kernel performs a side effect or state change.
- **Channel** — any path out of the harness.
- **Ad-hoc** — Operator-authorized Run without a Method.
- **Clear** — Advisor attestation of no challenge; not Acceptance.
