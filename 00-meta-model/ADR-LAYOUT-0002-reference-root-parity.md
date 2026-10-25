# ADR-LAYOUT-0002: Adopt current reference root structure

Date: 2026-09-08. Status: implemented under JD's direct layout instruction.
Requirement: the root and template must match the reference implementation's current structure.

Adopt 00-meta-model, 01-strategic-baseline, 02-systems-baseline,
03-solutions-baseline, 04-work-packages, 05-mxm-construct and 06-operations.
Root doorway files are AGENTS.md, CLAUDE.md, MXM.md, MEMORY.md and README.md.
Only .git, .github, .claude and .gitignore are additionally allowed at root.

Move repo decisions and optional profiles beneath 00-meta-model. Put the five
posture/pointer contracts in 05-mxm-construct/meta-harness; the canonical Means
contract is 05-mxm-construct/means/README.md. Separate executable scripts,
durable memory/wiki/session focus, and operations runbooks. Profile.json stays
beside Mission as the single identity binding. Claude imports AGENTS.md, which
imports required posture. Codex explicitly reads those same files and MXM.md.

This supersedes the earlier template default of General Work with absent MxM,
the flat six-file construct and independent decisions/profiles roots. Historical
ADRs remain as evidence, not current setup instructions. The template now defaults
to the Meta-Harness profile at JD's direction. A future General Work profile
needs a deliberate separate declaration and checker; silently removing the
construct would break this template's declared contract.

The portable checker validates structure and bootstrap declarations. It does not
copy the reference implementation's personal infrastructure, full gate implementation or native-memory
adapters, and it does not prove a model loaded or obeyed the files.
