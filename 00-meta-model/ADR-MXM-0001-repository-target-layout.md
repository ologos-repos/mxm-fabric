> Layout note (2026-09-08): current paths and profile are governed by
> `00-meta-model/ADR-LAYOUT-0002-reference-root-parity.md`; earlier layout statements
> below are retained as historical rationale.

# ADR-MXM-0001 — Repository target layout and MxM extension

- **Status:** Accepted
- **Date:** 2026-09-02
- **Deciders:** JD Longmire (principal), the aide
- **Requirement trace:** none — pure process/mechanics decision, recorded explicitly rather than
  left implicit, per this template's own convention that a decision tracing to no requirement
  says so rather than omitting the field.

## Numbering note

This is the first ADR recorded in this template's own `00-meta-model/` — there was no prior ADR
here to continue a sequence from, so it is `0001` in this repo's own numbering, not `0002`. It
**supersedes**, in content, `ADR-MXM-META-0001` (2026-08-07) recorded in a *different* repo,
`mxm-assistant-001`, which declared the
VWMM convention with `04-construct` and `05-work-packages` as the org-wide standard. That other
repo's own ADR sequence and numbering are not this file's to continue; this ADR only records
what changes in the shape *this template ships*, and why.

## Context

JD directed, 2026-08-30 (recorded in full in the reference
repository's own
`05-work-packages/WP-AFR-0001-architecture-findings-roadmap/roadmap.md`, "Operator
decisions already taken"): *"this will become the standard across all orgs even my
jdlongmire"* and *"all that I am the originator of which includes my assistants, this would be
recommended for any other partner or collaborator, and this only is scoped to new work and
getting the reference refactored."*

Scope is by origin and authority, not namespace: new JD-originated work (including work
performed by an AI aide on his behalf) adopts this standard wherever it is hosted;
partner- or collaborator-originated work receives it as a recommendation, not a mandate.
Existing repositories are grandfathered — this ADR governs repositories instantiated from this
template *after* it is recorded, not a retroactive migration of anything already built from the
prior shape.

The prior shape declared by `ADR-MXM-META-0001`: `00-meta-model/` · `01-strategic-baseline/` ·
`02-systems-baseline/` · `03-solutions-baseline/` · `04-construct/` · `05-work-packages/` ·
`decisions/`, with `mode.md` as the always-loaded, model-agnostic doorway. A batch review of that
shape (received 2026-08-30) found it workable for a from-scratch product repository but
under-specified for a richer one: no home for a second Git-forge convention, and a doorway file
name (`mode.md`) that doesn't read as a harness-neutral bootstrap contract to an arriving model
or human.

**What was actually found in this repository at the time this ADR was recorded** (verified by a
fresh clone, not assumed from prior documentation): `04-construct/` was not stub-empty — it
carried six one-line placeholder files (`mission.md`, `mind.md`, `morals.md`, `memory.md`,
`methods.md`, `means.md`), each explicitly marked "Template stub... delete the file if the
surface genuinely does not apply." No `.gitea/` directory existed to mirror into a new `.github/`
— the "admit both platform directories" change below therefore adds `.github/` with nothing to
mirror from, rather than alongside an existing `.gitea/` as an earlier draft of this change had
assumed.

## Decision

Four changes, recorded together because they are one coherent renumbering, not four independent
ones:

### 1. `mode.md` → `MXM.md`

The always-loaded, model-agnostic doorway file at repository root is renamed and its content
extended to also serve as the MxM bootstrap contract: profile/version declaration, repository-
class declaration, the six framework surfaces (path-mapped per class), loading rules, harness-
adapter mappings, memory/means entry points, and a conformance-gate statement — on top of the
Authority/Working-rules content the file already carried. `mode.md` names a mechanism; `MXM.md`
names the framework a reader is entering. `CLAUDE.md` is added as a one-line `@`-import adapter
pointing at it, so Claude Code's own auto-load convention resolves to `MXM.md` without carrying
independent content of its own.

### 2. `05-work-packages/` → `04-work-packages/`

The prior scheme numbered `04-construct` ahead of `05-work-packages`. Making construct conditional
(change 3) leaves a gap at `04` for the majority of repositories that carry no construct surface
at all. Collapsing work packages to `04` keeps the baseline `00`–`04` contiguous for every
repository regardless of class, and reserves `05` exclusively for the conditional extension.
`01`–`03` are unaffected.

### 3. `04-construct/` → conditional `05-mxm-construct/`

Renamed, renumbered, and made **conditional**: present only for a repository that declares
itself Meta-Harness class in `MXM.md`. A General Work repository — the default profile, and what
most template-instantiated repositories are — does not carry it at all.

**Not shipped populated by default.** The six stub files found in this repository's own
`04-construct/` (one line each, explicitly marked as placeholders to delete if unused) are exactly
the "empty surface is worse than an absent one" failure this template already warns against
elsewhere. Shipping `05-mxm-construct/` absent by default and documenting how to add it — rather
than shipping it pre-populated with the same six stubs under a new path — applies that lesson
structurally instead of relying on each new repository's author to remember to delete it. A
Meta-Harness-class repository builds six real files here (`mission.md`, `mind.md`, `morals.md`,
`memory.md`, `methods.md`, `means.md`) from scratch, or by adapting a lived-in example (the reference repository's
own `meta-harness/` directory is one) — not by resurrecting empty stubs. The pre-migration stub
content remains recoverable from this repository's git history if a starting shape is wanted.

GitHub template repositories cannot conditionally include files at instantiation time, so "absent
by default" means: not present on this template's own default branch. A repository author who
needs the Meta-Harness class adds the directory themselves after instantiating.

### 4. Explicit repository-class declaration

`MXM.md` gains a required field naming exactly one class: **General Work** (default) or
**Meta-Harness**. This did not exist as an explicit declaration before — the difference between
"a repository with a harness identity layer" and "a repository without one" was implicit in which
directories happened to exist. A conditional directory needs a machine-checkable reason to be
conditional on; declaring the class explicitly is what a later conformance check can assert
against, rather than inferring intent from directory presence alone (which cannot distinguish
"deliberately General Work" from "Meta-Harness, but not built yet").

### 5. Admit `.github/` as a platform directory

This repository carried no `.gitea/` directory at the time of this decision — there was nothing
to mirror. `.github/` is added regardless, with a `README.md` explaining why it's present and
empty, so a repository instantiated from this template is forge-agnostic from creation rather
than implying a single Git host by omission. Populate it (`workflows/`, `ISSUE_TEMPLATE/`,
`pull_request_template.md`) as a specific downstream repository actually needs CI or process
templates.

## Why profile overlays stay additive, not a fork of the baseline

The prior scheme already supports **profile overlays** — `profiles/research-programme.md` layers
the Lakatosian apparatus on top of the base VWMM tree for TRT-class repositories, without
replacing it. This ADR's change 3 continues that pattern: `05-mxm-construct/` is purely additive
on top of the shared `00`–`04` baseline, never a different tree for Meta-Harness repositories.
That property — the baseline path shape is the same everywhere, only the additive layers vary —
is what keeps a generic conformance check or work-package script meaningful across every
repository instantiated from this template, regardless of class.

## Consequences

- Every repository instantiated from this template after this ADR is recorded carries `MXM.md`
  and `CLAUDE.md` at root, `00`–`03` baselines, and `04-work-packages/`, unconditionally;
  `05-mxm-construct/` only if the repository declares Meta-Harness class.
- `decisions/ADR-SLUG-META-0001-vwmm-structural-convention.md` (the stub every new repository
  fills in) is updated to name the new baseline list, so a repository instantiated after this
  point records the current shape, not the superseded one.
- No existing repository built from the prior shape is migrated by this ADR. It governs
  repositories instantiated after this point.
- This ADR is the reference point a later conformance script checks a declaring repository
  against.

## Open items

- The operational-layer extension point some richer repositories may eventually need (a
  `06-operations/`-shaped directory, for a repository with registry/ops content) is deliberately
  **not** specified here — this ADR's scope is the template's default shape for new repositories,
  and a repository that needs more than `00`–`05` records that extension in its own `decisions/`
  when it actually needs it, rather than this template pre-reserving a slot speculatively.
