# WP-MXK-0005 verification

## Suites

- `python3 -m pytest -q 05-mxm-construct`: 106 passed, 3 xfailed. The xfails are the
  strict F-08, F-18 and F-20 gaps; F-19 was promoted.
- `python3 -I -S conformance.py --stdlib 05-mxm-construct/means/enforcement/tests`:
  71 passed, 3 xfailed, 0 failed. This matches pytest, and the release test pins the parity.

## Ed25519 cross-checks (development evidence, not part of the offline suite)

- RFC 8032 §7.1 TEST 1–3: public keys and signatures match both `cryptography` 43.0.0 and
  `mxm.ed25519`.
- 300 random seeds and messages: public keys and signatures are byte-identical with
  `cryptography`. Each implementation verifies the other's signatures. Every single-bit
  signature change and every message change is rejected. Cost is about 14 ms per sign, verify
  and negative check.
- OpenSSL 3.5.6 `pkeyutl -sign -rawin` over an authorization-domain message produces the same
  bytes as `mxm.ed25519.sign`, and `mxm.ed25519.verify` accepts it.

## Mutation check

Each defence was disabled in a scratch copy of the enforcement tree, then the suite was
run. All 21 mutations fail the suite:

- replay signature check
- principal effects need an authorization
- effect ownership by role
- transition check on replay
- port authorization
- single use
- act binding
- unit binding
- pin binding
- expiry
- signature validity
- key role
- key retirement
- chain verification on scan
- in-process prefix check
- Ed25519 S < L
- open-record consistency
- kernel-scope limits
- new unit id on open
- anchor verification
- port halt check

The first run caught 11 of 14. The misses were tests that reached a different check first.
Targeted tests were added (ownership-only forgeries, an unanchored running-kernel prefix
change, Ed25519 malleability, intercepted-authorization forgeries), and each was confirmed
to catch its mutation.

Human-Curated, AI-Enabled (HCAE)
