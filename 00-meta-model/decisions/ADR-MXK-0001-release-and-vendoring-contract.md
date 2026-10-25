# ADR-MXK-0001 — Release and vendoring contract

- **Status:** Decided
- **Work package:** `04-work-packages/WP-MXK-0003-release-contract/`

## Context

Every standalone meta-harness, including air-gapped ones, carries its own self-contained,
enforced copy of this kernel. It has no runtime dependency on this repository. That only
holds if a harness can prove, offline, that its copy is exactly a released kernel and that
the copy still conforms. One assumption would quietly break the claim: the conformance suite
uses pytest, a third-party package that an air-gapped harness may not have.

## Decision

1. **A release is a manifest-pinned tree.** `release.json` names the release paths. `release.py
   build` copies them and writes `release-manifest.json`, which contains:
   - the name, version and source commit;
   - the minimum Python version and the platform;
   - the conformance suites;
   - a SHA-256 per file, plus an aggregate SHA-256 over the sorted `digest  path` lines.

   The release tooling ships inside every release, so a harness never needs this repository
   to verify one.
2. **Verification is offline and fails closed.** `release.py verify` checks, in order:
   - **Integrity:** every file matches its pin; nothing is missing or extra; the aggregate
     matches the harness's expected pin.
   - **Containment:** no file imports anything outside the Python standard library and the
     release itself. Test files may also import `pytest`, which the runner supplies.
   - **Conformance:** the shipped suites pass.
3. **Conformance runs on the standard library alone.** `conformance.py` supplies a minimal
   stand-in for the pytest features the suites use (fixtures, `tmp_path`, `parametrize`,
   strict `xfail`, `raises`) and refuses any feature it does not implement. Verification
   launches it in isolated mode without site-packages (`python -I -S`), so it cannot lean on
   anything installed outside the release. Its results are tested to match real pytest on
   the kernel suite.
4. **Vendoring is copy, verify, lock.** `release.py install --expect AGGREGATE`:
   - refuses an unverified release or a wrong pin;
   - copies the release into the harness;
   - re-verifies the copy there;
   - writes `mxm-kernel.lock.json` recording the pinned version and aggregate.

   A vendored copy is never edited in place. Changes arrive as a new release.
5. **Every change stays releasable.** CI builds a release and verifies it in isolated mode on
   every pull request.

## Consequences

- A harness proves its kernel with one offline command against its recorded pin.
- New kernel code must be standard-library only, or it fails containment. A test that uses a
  pytest feature the runner lacks fails loudly rather than being skipped.
- Known limit: the audit chain uses `fcntl`, so releases are POSIX-only. This is recorded
  in the manifest's `platform`.
- Not decided here: release signing (authority, beyond integrity). It pairs with the planned
  signed act-bound authorizations.

Human-Curated, AI-Enabled (HCAE)
