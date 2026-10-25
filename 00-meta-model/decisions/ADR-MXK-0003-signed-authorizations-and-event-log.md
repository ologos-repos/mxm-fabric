# ADR-MXK-0003 — Signed act-bound authorizations and one transactional event log

- **Status:** Decided; amended by [ADR-MXK-0004](ADR-MXK-0004-step5-revision.md) (effects derived on replay, key validation, signing domain, resolved opening, evidence linkage; claims corrected)
- **Work package:** `04-work-packages/WP-MXK-0005-authorizations-event-log/`
- **Decision authority:** Principal Operator, 2026-09-28 (source meta-harness issue 32: "All approved";
  increment 3 design)

## Context

In the enforcement core as reconciled (WP-TMH-0016), Operator and Advisor acts relied on a
verifier: a callable whose returned string conferred the role. State was split across
per-unit Evidence logs, halt-marker files, anchors and in-memory WorkUnits. The independent
Advisor review left five release blockers (source meta-harness issue 36):

1. malformed markers or anchors raise;
2. state is not transactional;
3. units do not survive a restart, and halt markers can be deleted undetectably;
4. port results are inconsistent;
5. internal handlers are reachable in-process.

The Principal Operator approved the remedy: signed, single-use, act-bound authorizations
issued outside the engine, and one transactional append-only event log from which
WorkUnits are rebuilt, with an externally anchored head. Every harness vendors this kernel
and may be air-gapped, so the remedy must use only the standard library.

## Decision

1. **Operator and Advisor acts are authorized by signatures, not by a verifier.** An
   authorization is an Ed25519 (RFC 8032) signature by a key in the kernel's trust registry.
   It covers the role, the unit, the act (the proposed action minus its actor), the
   constitution pin, a unique id and a validity window. The kernel refuses an act unless:
   - the signature verifies;
   - every binding matches;
   - the window contains its clock;
   - the id is unspent.

   An id is spent when the act carrying it is recorded. Keys can be retired at a log
   position.
2. **Asymmetric, because the kernel must not hold minting power.** HMAC is in the standard
   library, but its verifier holds the signing secret, so anything that can read the
   kernel's files could mint Operator authority. With Ed25519 the kernel holds public keys
   only. The implementation (`mxm/ed25519.py`) is pure Python, with a strict verifier that
   rejects non-canonical points and S >= L. It passes the RFC 8032 vectors and was
   cross-checked against OpenSSL and the `cryptography` package. It is not constant-time;
   that is harmless for verification, which holds no secret. Signing should run where no
   untrusted process can time it, or use any RFC 8032 implementation, since signatures
   interoperate.
3. **One event log holds all state.** WorkUnits, transitions, challenges, waivers,
   acceptances, halts, spent authorizations and all Evidence are records in one hash-chained
   log. A proposal holds one exclusive lock from reading the log to appending. Act records
   are written ahead of side effects, and receipts follow them. Every kernel on a data root
   rebuilds state by replaying, so units persist and processes share state.
4. **Authority is validated on every record, not at a method boundary.** One check runs
   before any record is appended, and again whenever any kernel replays it:
   - principal effects need a valid, unspent authorization;
   - effects come from their owning role;
   - transitions are legal chain steps.

   A record failing replay halts the kernel. This replaces "which method was called" (naming
   is not isolation) with "what the log can prove".
5. **Faults halt; they never raise.** Chain findings, a rewritten applied prefix, an
   unreadable anchor, and invalid records each halt the kernel for the rest of the process,
   and each is recorded once in the log. An unwritable anchor records a kernel halt, and the
   effect of the act being recorded does not run. A signed Operator `clear_halt` clears
   recorded halts. Integrity halts need out-of-band repair.
6. **Ports are consistent.** `open_package` returns a Decision (`opened`), and the new
   unit's id is the one the authorization names.
7. **Issuing is a principal-side tool.** `mxm_principal.py keygen` creates a 0600 key and
   adds its public half to the trust registry. `act` signs and submits one act from the
   principal's own process.

## Consequences

- Release blockers 1–5 are closed (TRACEABILITY.md maps each to its tests), and F-19 is
  closed.
- The MCP server (ADR-MXK-0002) now serves units opened by another process. Its known limit
  is gone. It needs `--trust` to replay Operator records, and it still holds no signing key.
- Deployment preconditions, stated rather than proven:
  - signing keys stay in the principals' processes;
  - the trust registry, constitution and anchor are not engine-writable.

  Without an anchor, a restarted kernel cannot detect truncation, or recomputation of
  unsigned records.
- An in-process caller can still mutate a kernel's in-memory cache. It cannot make the log
  carry an authority-bearing change, and a restart or any other kernel ignores the change.
- Memory writes (`mxm/memory.py`) remain side effects outside the log. Bringing memory under
  governed actions is roadmap step 6.
- Not decided here: release signing; a hardware-backed or constant-time signer; key
  distribution beyond a registry file.

Human-Curated, AI-Enabled (HCAE)
