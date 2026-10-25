# Layout verification, 2026-09-08

Direct local execution on Linux, Python 3.10 and Git. No independent reviewer
or remote model run was used.

- Portable layout gate: PASS.
- Layout regression suite: 8 PASS (valid layout, unexpected file/directory,
  missing operations, flat shadow surface, fenced inactive import, wrong loading,
  missing Codex explicit-read instruction).
- Lifecycle suite: 13 PASS after relocation and gate integration.
- Start and wrap wrappers invoked from /tmp: start prints required posture and
  ACTIVE-FOCUS; wrap refuses the dirty development checkout as intended.
- Local Markdown link scan: no broken targets.
- git diff --check: PASS.

The template and Jeff's repository carry identical layout-checker source and
canonical paths. Jeff keeps his operator profile; the template uses UNCONFIGURED.
These checks establish portable structural parity with the reference implementation, not full runtime
feature parity or target-machine activation. Actual Codex/Claude first-session
loading on the operator's machine remains an onboarding check.

Publication: integrate the tested commit, push main, compare the live remote
SHA with local main, and run session-wrap on the clean integrated checkout.
The final handoff reports that observed result.
