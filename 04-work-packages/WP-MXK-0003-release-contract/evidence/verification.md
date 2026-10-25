# WP-MXK-0003 verification

## Parity (stdlib runner vs real pytest), kernel suite
- `conformance.py --stdlib 05-mxm-construct/means/enforcement/tests`: 31 passed, 4 xfailed, 0 failed, 0 xpassed(strict).
- `pytest -q` on the same suite: 31 passed, 4 xfailed.

## Air-gap proof
The release was built from the branch (22 files) and verified inside `unshare -rn`, a
network namespace with only loopback, using `python3 -I -S`, where pytest is not importable:
- `release.py verify rel --expect <aggregate>`: `ok: true`, no problems. This covers
  integrity, containment and conformance; conformance ran in its own `-I -S` child.
- After appending one line to `mxm/kernel.py`: `ok: false`, `modified:
  05-mxm-construct/means/enforcement/mxm/kernel.py`.

## Repository suite
65 passed, 4 xfailed (13 new contract tests). The layout check passes.
