# ADR-MXK-0007 — EAF v0.2 architecture baseline ratified

- **Status:** Decided
- **Decision authority:** Principal Operator, 2026-10-23 ("Proceed")
- **Rationale:** Process-only. This record ratifies a document baseline; it
  introduces no new requirements and asserts no implementation conformance.
- **Documents ratified:**
  - `02-systems-baseline/2.2-architecture/SPEC-MXM-EAF-0001.md` (v0.2.1)
  - `02-systems-baseline/2.2-architecture/MXM-REFERENCE-ARCHITECTURE-0001.md` (v0.2.0)
  - `02-systems-baseline/2.2-architecture/MXM-CONFORMANCE-MODEL-0001.md` (v0.2.0)
  - `02-systems-baseline/2.2-architecture/MXM-CAPABILITY-CONTRACTS-0001.md` (v0.2.0)
- **Evidence input:** External architecture evaluation (GPT, 2026-10-23), filed
  with verification annotations in `02-systems-baseline/2.5-verification/`.

## Context

The four documents entered this repository on 2026-10-23 as the EAF v0.2 set,
each carrying a Proposed status. An external evaluation the same day flagged
the lag between the documents' working role as the architecture baseline and
their unratified status fields, and recommended reconciliation against the
authoritative decision record rather than silent status edits. No such record
existed. This ADR is that record.

## Decision

1. **The four documents are approved** as the MxM Fabric architecture
   baseline at the versions named above.
2. **Their Status fields are updated** to record this approval and cite this
   ADR. The SPEC's internal decision-status line is updated to match.
3. **Approval covers the architecture baseline only.** It asserts nothing
   about implementation conformance. Per the conformance model, Specified,
   Implemented, Verified, Operational, and Authoritative are independently
   evidenced attributes; ratification moves none of them.
4. **The SPEC's Target (`ologos-repos/mxm-fabric`) is unchanged.** It names
   the publication target, not the current development home
   (the development repository).

## Alternatives considered

- **Leave the statuses Proposed.** Rejected: the record would understate the
  baseline's standing, and external readers could not distinguish a ratified
  baseline from a draft.
- **Edit the status fields without a decision record.** Rejected: a silent
  change with no authoritative trail, the failure mode the evaluation named.

## Consequences

The four status fields cite this ADR. Follow-on conformance work (capability
evidence population, cross-runtime enforcement demonstration, an EAF/IFA
minimum implementation, TMF validation) proceeds under its own work packages
and is not authorized or prejudged by this record. A substantive change to a
ratified document requires a new decision record or a version increment.

## Verification

Each ratified document's Status field cites ADR-MXK-0007; the SPEC's
decision-status line agrees; the layout verifier and the test suite pass on
the tree carrying this record.

Human-Curated, AI-Enabled (HCAE)
