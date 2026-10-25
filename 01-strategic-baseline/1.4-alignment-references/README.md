# Alignment references: inherited conventions and authority

Ratified 2026-10-23 by the Principal Operator, approved as drafted (WP-MXK-0015). Drafted from this repository's own record.

## Authority chain

- **Principal Operator.** Terminal authority over this repository and
  the fabric program. Nothing is decided without the operator; agent
  work product is attributed Human-Curated, AI-Enabled (HCAE) only.
- **Decision records.** Architecture and structure decisions live in
  00-meta-model (ADR-MXM series for structure, ADR-MXK series for
  kernel decisions, ADR-LAYOUT for layout parity). A claim about what
  was decided resolves to an ADR, not to memory or correspondence.
- **Ratified baseline.** The EAF v0.2 document set (SPEC-MXM-EAF-0001,
  MXM-REFERENCE-ARCHITECTURE-0001, MXM-CONFORMANCE-MODEL-0001,
  MXM-CAPABILITY-CONTRACTS-0001), ratified 2026-10-23 by ADR-MXK-0007.
  Changes go through a new ADR or a version increment.
- **Work governance.** Bounded work packages in 04-work-packages, each
  with explicit scope halves and an authority boundary; gates named in
  a package are principal approvals, not formalities.

## Inherited conventions

- **The MxM construct.** Six surfaces (Mission, Mind, Morals, Memory,
  Methods, Means); three always loaded, three pointer-shaped; MXM.md
  is the canonical bootstrap and harness adapters route to it
  (ADR-MXM-0002).
- **The Principal Governance Triad.** Operator decides, Assistant acts,
  Advisor challenges; the Advisor's challenge returns to the Operator.
- **The work chain.** Work Package, WorkUnit, Run, Evidence,
  Acceptance, Integration, Disposition; each step verified before the
  next begins.
- **The SARS operating model** for architecture practice (Strategy,
  Architecture, Roadmaps, Standards), carried in the companion essays
  and the ecosystem viewpoint in 02-systems-baseline.

## External references

- Longmire, J. (JD), and Longmire, M., "Ordinal Systems Architecture:
  A Control Grammar for Enterprise AI Authority," Zenodo, 2026.
  doi 10.5281/zenodo.20334233.
- Longmire, J. (JD), "Governed Execution in Multi-Mode Agent
  Harnesses: Admission, Authority, Memory, Routing, and Closure
  Patterns (A Mx-Modes Companion)," Zenodo, 2026.
  doi 10.5281/zenodo.23367869.
- The Model Context Protocol, which the fabric's dependency-free MCP
  framework implements (05-mxm-construct/means/mcp).
- Ed25519 signatures (RFC 8032), the kernel's authorization and
  event-log signature scheme (ADR-MXK-0003).

Where an external reference and this repository disagree, the
repository's ratified records govern locally, and the disagreement is
filed as a finding rather than silently harmonized.

Human-Curated, AI-Enabled (HCAE)
