# Solution configuration: the vendored-kernel deployment pattern

Status: the fabric's first solution configuration, written under
WP-MXK-0015 step 4. It describes the one deployment pattern that is
in use today, released as
`mxm-kernel-v0.2.0` (first tagged release, 2026-10-23). It configures no code; the components live
in 05 and the operating instructions in 06. Decision record:
ADR-MXK-0001 (release and vendoring contract).

## Intent

Every meta-harness, including air-gapped ones, carries its own
self-contained, enforced copy of the MxM kernel, with no runtime
dependency on this repository. The harness must be able to prove,
offline, that its copy is exactly a released kernel and that the copy
still conforms.

## Topology

```text
this repository (source of truth; tag mxm-kernel-vX.Y.Z)
        |  release.py build
        v
release tree + release-manifest.json (per-file SHA-256, aggregate pin)
        |  release.py install --expect AGGREGATE
        v
consuming harness
  mxm-kernel.lock.json (pinned version + aggregate)
  vendored kernel: enforcement + MCP framework + release tooling
  harness-side: engine registration of the MCP server, operator
  profile binding, anchor storage outside the engine's write reach
```

Authority flows down (releases, pins, operator grants); evidence flows
up. Fixes found in a harness return as proposals and ship in a new
release. A vendored copy is never edited in place.

## Components assembled

- **Enforcement core** (`means/enforcement`): kernel decisions,
  authorizations, event log.
- **MCP framework** (`means/mcp`): dependency-free, stdlib, stdio;
  ships inside the release. Registering it with each engine is
  harness-side.
- **Release tooling** (`means/release`): ships inside every release,
  so a harness never needs this repository to verify one.
- **Conformance runner** (`conformance.py`): a standard-library
  stand-in for the pytest features the suites use, run in isolated
  mode (`python -I -S`); the suites' results are tested to match real
  pytest on the kernel suite.

## Assembly procedure

1. Build the release from a clean source tree; the manifest records
   name, version, source commit, minimum Python (3.10), platform
   (POSIX), conformance suites, and hashes.
2. Verify the release offline, in order: integrity (every file
   matches its pin; nothing missing or extra; aggregate matches),
   containment (no imports beyond the standard library and the
   release itself), conformance (the shipped suites pass).
3. Install into the harness with the expected aggregate. Install
   refuses an unverified release or a wrong pin, copies, re-verifies
   the copy in place, and writes the lock file.
4. Configure the harness side: bind the operator profile
   (`profile.json`, from the principal's confirmed instructions;
   template placeholders grant no authority), pin the constitution,
   place the event-log anchor where the engine cannot write, and
   register the MCP server with the engine.

## Acceptance criteria

A deployment of this pattern is accepted when, in the harness, with
network egress disabled:

- `release.py verify` passes against the recorded pin;
- the lock file's aggregate equals the expected aggregate;
- the conformance suites pass in isolated mode;
- a fresh session in the harness loads the canonical posture through
  the bootstrap adapters (structural checks alone are not evidence,
  ADR-LAYOUT-0002).

## Update and rollback

Update is re-vendoring: build or receive a new release, verify, install
over the old copy, and the lock file moves to the new aggregate.
Rollback is the same operation with the previous release and its
aggregate. There is no in-place patching state to reason about; a
deployment is always exactly one pinned release.

## Limits

- POSIX-only at this writing: the audit chain uses `fcntl`
  (recorded in the manifest's platform field).
- Release signing (authority beyond integrity) is not decided in
  ADR-MXK-0001 and is not claimed here.
- Console-era topologies (mxm-core service, TUI and web clients) are
  not part of this pattern; they will be written when WP-MXK-0014
  phases 3-4 exist to configure.

Human-Curated, AI-Enabled (HCAE)
