# Objectives and key results

Ratified 2026-10-23 by the Principal Operator, approved as drafted (WP-MXK-0015). Drafted from this repository's own record. Key results are tied to
work-package gates rather than calendar dates, so progress is measured
by evidence landed, not time elapsed.

## O1. Prove the kernel's controls in operation

The enforcement core is implemented and verified at kernel scope. The
objective is demonstrated conformance where the kernel is consumed.

- KR1: WP-MXK-0010 closes with second-runtime evidence filed in
  2.5-verification, including the mutation check reproduced with the
  mxm-core API in the loop.
- KR2: Capability matrix shows CAP-08, 09, 12, 15 Verified in at least
  one consuming runtime beyond the reference harness.
- KR3: Zero capabilities carry an Operational or Authoritative
  attribute without filed deployment evidence. (Standing constraint,
  audited at every matrix update.)

## O2. Complete the construct

Stand up the components ADR-MXM-0002 owns under 05-mxm-construct.

- KR1: mxm-contracts v1 schemas adopted (WP-MXK-0014 phase 2) with
  compatibility tests green in CI.
- KR2: mxm-core headless API passes the runtime gate: authorization
  conformance at the API boundary reviewed and approved by the
  principal.
- KR3: TUI console consumes the same contracts and event stream as
  core, with console non-authority tests passing (no console path to a
  privileged effect except a core-issued, principal-bound approval).

## O3. Mature the baselines until the record reads true

- KR1: Zero template stubs remain in baselines 00-03 (from 9 at the
  2026-10-23 inventory: four in 01, five subsection READMEs in 02).
- KR2: The cross-baseline traceability spine (objectives to
  requirements to architecture to solutions to implementation to
  verification) is published in 2.5-verification and updated on change.
- KR3: Every architecture claim in 02 traces to at least one
  requirement, and every requirement to the baseline document that
  owns it.

## O4. Keep the published record honest and current

- KR1: The capability traceability matrix is refreshed within one
  work-package closure of any evidence change (WP-MXK-0011).
- KR2: Each closed work package files its evidence in the repository
  before its disposition is recorded as done.
- KR3: The Zenodo record and the repository's Publications section
  agree at all times; new publications are added on deposit, never in
  advance of it.

Human-Curated, AI-Enabled (HCAE)
