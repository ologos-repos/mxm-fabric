# Means

## Available in this checkout

Python 3.10+ standard-library tool: [aide.py](scripts/aide.py).
Run it with `python` or `python3` from the repository root:

- `start`: print MxM, required posture, profile, memory index and Git status.
- `verify`: check this starter's structural contract; nonzero on failure.
- `wrap`: verification plus a clean Git working tree requirement.
- `remember --title TITLE --source SOURCE --file PATH`: retain a UTF-8 note as
  a candidate with UTC timestamp, source and unique ID. Review before committing.

`start` works from another working directory when given this script's absolute
path. No hardcoded home directories, package installs or network calls are used.
Git must be on PATH; Python must be installed. No API key is required for these
tools. `start` does not start a Codex model; open the workspace in Codex separately.

## Discover on the target machine

Codex shell, file editing, search and account-integrated tools depend on the
installed interface and granted permissions. Inventory them during onboarding.
Record only verified capabilities in profile.json and the onboarding record.

## Not installed

The reference web console, email/Telegram bridges, desktop control, voice cloning,
remote GPU services, scheduled agents, native-memory adapters and the reference
preflight/delegation infrastructure are not part of this release. They need
separate requirements, target-machine checks and account authorization.

## Companion rationale

`05-mxm-construct/means/` contains portable executable scripts and their tests.
This README is the canonical Means contract; implementation stays in scripts/.
