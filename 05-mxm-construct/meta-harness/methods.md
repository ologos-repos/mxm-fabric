# Methods

## Scope

Methods is the surface for all disciplined practice: how work is done,
whether the work is reasoning, research, engineering, or operations.
Mind governs how the agent thinks; Methods governs how the agent works.
Three families sit under this surface:

1. Reasoning and research practice: the research workflows of the
   Epistemic Assurance Framework (EAF), evaluation rubrics, and
   verification and validation gates.
2. Software delivery and operations practice: DevSecOps, GitOps,
   Everything as Code, the Scaled Agile Framework (SAFe), and PR-based
   change control.
3. Systems engineering practice: Model-Based Systems Engineering (MBSE)
   and the Modular Open Systems Approach (MOSA).

Boundary rules:

- Methods names the practice; Means holds the capability that executes
  it. GitOps is a method. The git platform, the runners, and the
  scanners are Means.
- An approach lives in Methods; the artifacts of the approach live in
  their own homes. MOSA the practice sits here; the interface standards
  it produces sit in Standards. A GitOps pipeline's rules live in
  policy; GitOps the practice lives here.
- Everything as Code governs what can be expressed as code. What cannot
  be expressed as code is described, specified, and verified, not
  codified; that discipline is also a method, held here.

The numbered procedure below is the standing method for work in this
repository. Product repositories may carry their own methods files under
the same scope.

1. Start by grounding in current instructions, memory, Git state and the actual
   tools available. `aide.py start` prints those local inputs without network calls.
2. Define success before implementation. Use a work package for significant work,
   with explicit authority, acceptance criteria and checks. Small tasks need only
   proportional tracking. Product changes belong in that product's repository.
3. Make significant changes in a dedicated branch/worktree. Preserve unrelated
   edits. Run meaningful tests covering failures and boundaries, not just a mirror
   of implementation. Inspect UI changes in the actual UI when relevant.
4. Verify against an identifiable artifact. Record the commands, result and
   environment. Independent review, when requested and available, is distinct
   from self-review; do not silently launch paid or parallel workers.
5. Commit the relevant code and documentation together. Confirm the exact remote
   ref after authorized publication. A push return code is not the whole check.
6. Before handoff, update memory and disposition, run `verify`, tests and `wrap`,
   and name remaining blockers. Wrap does not grant permission to push or merge.
7. When a recurring error is mechanically detectable, turn the lesson into a
   test or bounded guard. Otherwise retain its rationale as a method.

For onboarding follow [onboarding](../../06-operations/runbooks/ONBOARDING.md).
