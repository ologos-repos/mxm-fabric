# Migration inventory (phase-1 baseline, frozen 2026-10-23)

Baseline: development repository main @ 176f3031, 163 files, the tree assessed for the construct consolidation (ADR-MXM-0002, WP-MXK-0014). Frozen as phase-1 evidence. Source: the consolidation assessment in the working coordination record, 2026-10-23.

| Current path | Disposition | Notes |
|---|---|---|
| `.github/workflows/ci.yml` | Retain in place | RETAIN. No path filters; runs verifier + pytest from root. Update only if canonical paths move. |
| `.gitignore` | Retain in place | RETAIN. |
| `00-meta-model/ADR-LAYOUT-0002-reference-root-parity.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `00-meta-model/ADR-MXM-0001-repository-target-layout.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `00-meta-model/README.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `00-meta-model/decisions/ADR-MXK-0001-release-and-vendoring-contract.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `00-meta-model/decisions/ADR-MXK-0002-self-contained-mcp-framework.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `00-meta-model/decisions/ADR-MXK-0003-signed-authorizations-and-event-log.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `00-meta-model/decisions/ADR-MXK-0004-step5-revision.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `00-meta-model/decisions/ADR-MXK-0005-signed-principal-records-and-act-outcomes.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `00-meta-model/decisions/ADR-MXK-0006-verification-boundary.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `00-meta-model/decisions/ADR-MXK-0007-eaf-v02-baseline-ratification.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `00-meta-model/decisions/ADR-SLUG-META-0001-vwmm-structural-convention.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `00-meta-model/decisions/README.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `00-meta-model/profiles/README.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `00-meta-model/profiles/research-programme.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `00-meta-model/test_verify_repository_layout.py` | Retain in place | RETAIN; extend with negative cases for any new canonical paths. |
| `00-meta-model/verify-repository-layout.py` | Retain / amend first | RETAIN, AMEND FIRST in any migration (R-11): ROOT_FILES allowlist, SURFACES map, required-files list, shadow-surface checks all pin current paths. |
| `00-meta-model/work-model.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `01-strategic-baseline/1.1-vision/.gitkeep` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `01-strategic-baseline/1.1-vision/README.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `01-strategic-baseline/1.2-strategy/.gitkeep` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `01-strategic-baseline/1.2-strategy/README.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `01-strategic-baseline/1.3-objectives-krs/.gitkeep` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `01-strategic-baseline/1.3-objectives-krs/README.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `01-strategic-baseline/1.4-alignment-references/.gitkeep` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `01-strategic-baseline/1.4-alignment-references/README.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `01-strategic-baseline/README.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `02-systems-baseline/2.1-requirements/.gitkeep` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `02-systems-baseline/2.1-requirements/EAF-requirements.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `02-systems-baseline/2.1-requirements/README.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `02-systems-baseline/2.1-requirements/REQ-MXK-VER.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `02-systems-baseline/2.2-architecture/.gitkeep` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `02-systems-baseline/2.2-architecture/MXM-CAPABILITY-CONTRACTS-0001.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `02-systems-baseline/2.2-architecture/MXM-CONFORMANCE-MODEL-0001.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `02-systems-baseline/2.2-architecture/MXM-REFERENCE-ARCHITECTURE-0001.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `02-systems-baseline/2.2-architecture/README.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `02-systems-baseline/2.2-architecture/SPEC-MXM-EAF-0001.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `02-systems-baseline/2.2-architecture/agentic-ai-ecosystem-reference-architecture/README.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `02-systems-baseline/2.2-architecture/agentic-ai-ecosystem-reference-architecture/agentic-ai-ecosystem-reference-architecture.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `02-systems-baseline/2.2-architecture/agentic-ai-ecosystem-reference-architecture/hero.png` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `02-systems-baseline/2.2-architecture/agentic-ai-ecosystem-reference-architecture/plate.jpg` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `02-systems-baseline/2.2-architecture/agentic-ai-ecosystem-reference-architecture/plate.svg` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `02-systems-baseline/2.2-architecture/essays/README.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `02-systems-baseline/2.2-architecture/essays/agentic-enterprise-architecture/agentic-enterprise-architecture.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `02-systems-baseline/2.2-architecture/essays/agentic-enterprise-architecture/figure-1-reference-model.jpg` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `02-systems-baseline/2.2-architecture/essays/agentic-enterprise-architecture/figure-2-model-as-code.png` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `02-systems-baseline/2.2-architecture/essays/agentic-enterprise-architecture/figure-3-model-operated.png` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `02-systems-baseline/2.2-architecture/essays/agentic-enterprise-architecture/hero.png` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `02-systems-baseline/2.2-architecture/essays/harness-engineering/harness-engineering.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `02-systems-baseline/2.2-architecture/essays/harness-engineering/hero.png` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `02-systems-baseline/2.2-architecture/essays/the-governed-control-system/fig-loop.png` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `02-systems-baseline/2.2-architecture/essays/the-governed-control-system/hero.png` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `02-systems-baseline/2.2-architecture/essays/the-governed-control-system/the-governed-control-system.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `02-systems-baseline/2.2-architecture/mxm-explainer/README.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `02-systems-baseline/2.2-architecture/mxm-explainer/hero.png` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `02-systems-baseline/2.2-architecture/mxm-explainer/introducing-mxm.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `02-systems-baseline/2.2-architecture/mxm-explainer/mxm-diagram.png` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `02-systems-baseline/2.2-architecture/mxm-explainer/mxm-diagram.svg` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `02-systems-baseline/2.2-architecture/mxm-explainer/mxm-narrative.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `02-systems-baseline/2.3-behavior/.gitkeep` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `02-systems-baseline/2.3-behavior/README.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `02-systems-baseline/2.4-interfaces/.gitkeep` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `02-systems-baseline/2.4-interfaces/README.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `02-systems-baseline/2.5-verification/.gitkeep` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `02-systems-baseline/2.5-verification/2026-10-23-gpt-architecture-evaluation.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `02-systems-baseline/2.5-verification/README.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `02-systems-baseline/2.5-verification/capability-traceability.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `02-systems-baseline/2.5-verification/layout-evidence.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `02-systems-baseline/README.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `03-solutions-baseline/README.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `04-work-packages/README.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `04-work-packages/TEMPLATE/package.yaml` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `04-work-packages/WP-MXK-0001-stand-up/README.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `04-work-packages/WP-MXK-0001-stand-up/evidence/verification.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `04-work-packages/WP-MXK-0001-stand-up/package.yaml` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `04-work-packages/WP-MXK-0002-enforcement-core/README.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `04-work-packages/WP-MXK-0002-enforcement-core/package.yaml` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `04-work-packages/WP-MXK-0003-release-contract/README.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `04-work-packages/WP-MXK-0003-release-contract/evidence/verification.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `04-work-packages/WP-MXK-0003-release-contract/package.yaml` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `04-work-packages/WP-MXK-0004-mcp-framework/README.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `04-work-packages/WP-MXK-0004-mcp-framework/evidence/verification.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `04-work-packages/WP-MXK-0004-mcp-framework/package.yaml` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `04-work-packages/WP-MXK-0005-authorizations-event-log/README.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `04-work-packages/WP-MXK-0005-authorizations-event-log/evidence/verification.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `04-work-packages/WP-MXK-0005-authorizations-event-log/package.yaml` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `04-work-packages/WP-MXK-0006-step5-revision/README.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `04-work-packages/WP-MXK-0006-step5-revision/evidence/mutations.py` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `04-work-packages/WP-MXK-0006-step5-revision/evidence/verification.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `04-work-packages/WP-MXK-0006-step5-revision/package.yaml` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `04-work-packages/WP-MXK-0007-act-outcomes/README.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `04-work-packages/WP-MXK-0007-act-outcomes/evidence/mutations.py` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `04-work-packages/WP-MXK-0007-act-outcomes/evidence/verification.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `04-work-packages/WP-MXK-0007-act-outcomes/package.yaml` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `04-work-packages/WP-MXK-0008-transformer-limitations/README.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `04-work-packages/WP-MXK-0008-transformer-limitations/evidence/sikka-sikka-2025-audit.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `04-work-packages/WP-MXK-0008-transformer-limitations/package.yaml` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `04-work-packages/WP-MXK-0009-verification-boundary/package.yaml` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `04-work-packages/WP-MXK-0010-cross-runtime-conformance/package.yaml` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `04-work-packages/WP-MXK-0011-capability-assessment/package.yaml` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `04-work-packages/WP-MXK-0012-eaf-ifa-minimum-implementation/package.yaml` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `04-work-packages/WP-MXK-0013-tmf-governed-retrieval/package.yaml` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `04-work-packages/WP-TEMPLATE-0002-layout/README.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `04-work-packages/WP-TEMPLATE-0002-layout/package.yaml` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `05-mxm-construct/means/README.md` | Retain in place (phases 1-4) | Part of the means/ substrate. Relocation only under decision D1 option C at phase 5, as a release-contract change. |
| `05-mxm-construct/means/enforcement/SPEC.md` | Retain in place (phases 1-4) | Part of the means/ substrate. Relocation only under decision D1 option C at phase 5, as a release-contract change. |
| `05-mxm-construct/means/enforcement/TRACEABILITY.md` | Retain in place (phases 1-4) | Part of the means/ substrate. Relocation only under decision D1 option C at phase 5, as a release-contract change. |
| `05-mxm-construct/means/enforcement/constitutions/default.json` | Retain in place (phases 1-4) | Part of the means/ substrate. Relocation only under decision D1 option C at phase 5, as a release-contract change. |
| `05-mxm-construct/means/enforcement/methods/001_echo_draft.py` | Retain in place (phases 1-4) | Part of the means/ substrate. Relocation only under decision D1 option C at phase 5, as a release-contract change. |
| `05-mxm-construct/means/enforcement/mxm/__init__.py` | Retain in place (phases 1-4) | Part of the means/ substrate. Relocation only under decision D1 option C at phase 5, as a release-contract change. |
| `05-mxm-construct/means/enforcement/mxm/audit_chain.py` | Retain in place (phases 1-4) | Part of the means/ substrate. Relocation only under decision D1 option C at phase 5, as a release-contract change. |
| `05-mxm-construct/means/enforcement/mxm/authz.py` | Retain in place (phases 1-4) | Part of the means/ substrate. Relocation only under decision D1 option C at phase 5, as a release-contract change. |
| `05-mxm-construct/means/enforcement/mxm/chain.py` | Retain in place (phases 1-4) | Part of the means/ substrate. Relocation only under decision D1 option C at phase 5, as a release-contract change. |
| `05-mxm-construct/means/enforcement/mxm/constitution.py` | Retain in place (phases 1-4) | Part of the means/ substrate. Relocation only under decision D1 option C at phase 5, as a release-contract change. |
| `05-mxm-construct/means/enforcement/mxm/ed25519.py` | Retain in place (phases 1-4) | Part of the means/ substrate. Relocation only under decision D1 option C at phase 5, as a release-contract change. |
| `05-mxm-construct/means/enforcement/mxm/eventlog.py` | Retain in place (phases 1-4) | Part of the means/ substrate. Relocation only under decision D1 option C at phase 5, as a release-contract change. |
| `05-mxm-construct/means/enforcement/mxm/exceptions.py` | Retain in place (phases 1-4) | Part of the means/ substrate. Relocation only under decision D1 option C at phase 5, as a release-contract change. |
| `05-mxm-construct/means/enforcement/mxm/kernel.py` | Retain in place (phases 1-4) | Part of the means/ substrate. Relocation only under decision D1 option C at phase 5, as a release-contract change. |
| `05-mxm-construct/means/enforcement/mxm/means.py` | Retain in place (phases 1-4) | Part of the means/ substrate. Relocation only under decision D1 option C at phase 5, as a release-contract change. |
| `05-mxm-construct/means/enforcement/mxm/memory.py` | Retain in place (phases 1-4) | Part of the means/ substrate. Relocation only under decision D1 option C at phase 5, as a release-contract change. |
| `05-mxm-construct/means/enforcement/mxm/methods.py` | Retain in place (phases 1-4) | Part of the means/ substrate. Relocation only under decision D1 option C at phase 5, as a release-contract change. |
| `05-mxm-construct/means/enforcement/mxm/morals.py` | Retain in place (phases 1-4) | Part of the means/ substrate. Relocation only under decision D1 option C at phase 5, as a release-contract change. |
| `05-mxm-construct/means/enforcement/mxm/types.py` | Retain in place (phases 1-4) | Part of the means/ substrate. Relocation only under decision D1 option C at phase 5, as a release-contract change. |
| `05-mxm-construct/means/enforcement/mxm_principal.py` | Retain in place (phases 1-4) | Part of the means/ substrate. Relocation only under decision D1 option C at phase 5, as a release-contract change. |
| `05-mxm-construct/means/enforcement/tests/mxm_testing.py` | Retain in place | Test bootstrap inserts sys.path relative to the test file; a package move breaks it until updated in the same commit. |
| `05-mxm-construct/means/enforcement/tests/test_adversarial.py` | Retain in place | Test bootstrap inserts sys.path relative to the test file; a package move breaks it until updated in the same commit. |
| `05-mxm-construct/means/enforcement/tests/test_authz.py` | Retain in place | Test bootstrap inserts sys.path relative to the test file; a package move breaks it until updated in the same commit. |
| `05-mxm-construct/means/enforcement/tests/test_conformance.py` | Retain in place | Test bootstrap inserts sys.path relative to the test file; a package move breaks it until updated in the same commit. |
| `05-mxm-construct/means/enforcement/tests/test_ed25519.py` | Retain in place | Test bootstrap inserts sys.path relative to the test file; a package move breaks it until updated in the same commit. |
| `05-mxm-construct/means/mcp/mxm_mcp/__init__.py` | Retain in place (phases 1-4) | Part of the means/ substrate. Relocation only under decision D1 option C at phase 5, as a release-contract change. |
| `05-mxm-construct/means/mcp/mxm_mcp/delegation.py` | Retain in place (phases 1-4) | Part of the means/ substrate. Relocation only under decision D1 option C at phase 5, as a release-contract change. |
| `05-mxm-construct/means/mcp/mxm_mcp/kernel_tools.py` | Retain in place (phases 1-4) | Part of the means/ substrate. Relocation only under decision D1 option C at phase 5, as a release-contract change. |
| `05-mxm-construct/means/mcp/mxm_mcp/server.py` | Retain in place (phases 1-4) | Part of the means/ substrate. Relocation only under decision D1 option C at phase 5, as a release-contract change. |
| `05-mxm-construct/means/mcp/mxm_mcp_server.py` | Retain in place (phases 1-4) | Part of the means/ substrate. Relocation only under decision D1 option C at phase 5, as a release-contract change. |
| `05-mxm-construct/means/mcp/tests/test_mcp.py` | Retain in place | Test bootstrap inserts sys.path relative to the test file; a package move breaks it until updated in the same commit. |
| `05-mxm-construct/means/release/conformance.py` | Retain in place (phases 1-4) | Part of the means/ substrate. Relocation only under decision D1 option C at phase 5, as a release-contract change. |
| `05-mxm-construct/means/release/release.json` | Retain in place | RETAIN. Defines the vendored kernel: release_paths = means/enforcement, means/mcp, means/release. Any relocation of those trees is a release-contract change (ADR-MXK-0001), not a file move. |
| `05-mxm-construct/means/release/release.py` | Retain in place | RETAIN in place. Pins CONFIG_REL and the conformance runner path as literals. |
| `05-mxm-construct/means/release/tests/test_release.py` | Retain in place | Test bootstrap inserts sys.path relative to the test file; a package move breaks it until updated in the same commit. |
| `05-mxm-construct/means/scripts/aide.py` | Retain in place | RETAIN in place (phases 1-4). Carries ~10 literal '05-mxm-construct/...' path references plus MXM.md/MEMORY.md; any move of meta-harness, memory, or scripts requires a same-commit update here. |
| `05-mxm-construct/means/scripts/session-start.py` | Retain in place | RETAIN in place. Invoked by literal path from AGENTS.md; verifier-required file. |
| `05-mxm-construct/means/scripts/session-wrap.py` | Retain in place | RETAIN in place. Same pinning as session-start.py. |
| `05-mxm-construct/means/scripts/tests/test_aide.py` | Retain in place | Test bootstrap inserts sys.path relative to the test file; a package move breaks it until updated in the same commit. |
| `05-mxm-construct/memory/README.md` | Retain in place | Already at the spec's target location under 05-mxm-construct. |
| `05-mxm-construct/memory/meta-context/current/ACTIVE-FOCUS.md` | Retain in place | Already at the spec's target location under 05-mxm-construct. |
| `05-mxm-construct/memory/wiki/index.md` | Retain in place | Already at the spec's target location under 05-mxm-construct. |
| `05-mxm-construct/meta-harness/memory.md` | Retain in place | Already at the spec's target location under 05-mxm-construct. |
| `05-mxm-construct/meta-harness/methods.md` | Retain in place | Already at the spec's target location under 05-mxm-construct. |
| `05-mxm-construct/meta-harness/mind.md` | Retain in place | Already at the spec's target location under 05-mxm-construct. |
| `05-mxm-construct/meta-harness/mission.md` | Retain in place | Already at the spec's target location under 05-mxm-construct. |
| `05-mxm-construct/meta-harness/morals.md` | Retain in place | Already at the spec's target location under 05-mxm-construct. |
| `05-mxm-construct/meta-harness/profile.json` | Retain in place | RETAIN in place. Verifier-required; aide.py reads it by literal path; the aide_name fixture is test-coupled. |
| `06-operations/README.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `06-operations/catalog/README.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `06-operations/runbooks/ONBOARDING.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `06-operations/runbooks/RECOVERY.md` | Retain in place | Numbered backbone (00-06) is preserved by the spec; no move proposed. |
| `AGENTS.md` | Retain in place | RETAIN as discovery adapter to MXM.md (already minimal, already non-doctrinal). |
| `CLAUDE.md` | Retain in place | RETAIN as Claude Code adapter (@AGENTS.md import chain). Empirically required for automatic discovery. |
| `LICENSE` | Retain in place | RETAIN (standard tooling). |
| `MEMORY.md` | Retain in place | RETAIN (operational memory index). Low-stakes; no consolidation needed. |
| `MXM.md` | Retain in place | RETAIN as canonical bootstrap. Spec R-02 would demote it; assessment recommends against (see D2). |
| `README.md` | Retain in place | RETAIN (repository face: title, Publications, viewpoint embeds). Not a shim; do not stub. |
