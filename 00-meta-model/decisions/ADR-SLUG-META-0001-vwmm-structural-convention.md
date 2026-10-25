> Layout note (2026-09-08): current paths and profile are governed by
> `00-meta-model/ADR-LAYOUT-0002-reference-root-parity.md`; earlier layout statements
> below are retained as historical rationale.

# ADR-<SLUG>-META-0001 — VWMM structural convention

- **Status:** Proposed
- **Date:** YYYY-MM-DD
- **Deciders:** [principal], [aide]
- **Requirement trace:** none — pure process/mechanics decision, recorded explicitly rather
  than left implicit.

## Context

This repo adopts the VWMM structural convention (VSOK · WBS · MBSE · MOSA) declared the
org-wide standard by `mxm-assistant-001`'s `ADR-MXM-META-0001` (2026-08-07), inherited via
`jdlongmire/longmire-repo-template`.

[State any deviation this repo needs, and why. If none, say so — silence is not a record.]

## Decision

Baselines are `00-meta-model/`, `01-strategic-baseline/`, `02-systems-baseline/`,
`03-solutions-baseline/`, `04-work-packages/`, `decisions/`. All ordinals zero-padded.
`05-mxm-construct/` is additive and conditional — present only if this repo declares itself
Meta-Harness class in `MXM.md` (see `00-meta-model/ADR-MXM-0001-repository-target-layout.md`).

[Record the repo slug used in ADR and work-package ids.]

## Consequences

[What this makes easy, what it makes awkward, and what would trigger revisiting it.]
