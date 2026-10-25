# WP-MXK-0001 verification

## Process home and protection
- The self-hosted repository was created private and seeded from the ref mirror at `cf49b83`.
  `ls-remote` shows the same `main` on both hosts.
- `main` protection, read back from the host API:
  - `enable_push: false`;
  - `enable_status_check: true`, with `status_check_contexts: ["CI / conformance (pull_request)"]`;
  - `block_admin_merge_override: true`.

## The gate, proven on PR #2
| Head | Check | Merge attempt | Result |
|---|---|---|---|
| e4f2a0b | CI / conformance pending | `POST /pulls/2/merge` | HTTP 405, refused |
| e4f2a0b | CI / conformance success | `POST /pulls/2/merge` | HTTP 200, merged as `bb3ed6c` |

## Ref mirror
- Write deploy key scoped to the mirror repository only; the private key stays in the
  root-only state directory.
- `mxm-kernel-mirror.timer` runs every 10 minutes. It uses its own status file, so it
  does not overwrite the meta-harness mirror's status.
- First run: 1/1 refs, identical. After the PR #2 merge: 2/2 refs identical, with `main` at
  `bb3ed6c` on both hosts.
