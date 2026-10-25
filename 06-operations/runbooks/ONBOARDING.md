# Start using YOUR-REPOSITORY

This is a personal aide workspace. Repository owners and collaborators can read committed memory. Store credentials in
your own credential manager, never in this repository.

## Get the workspace

Use your own GitHub and Codex accounts. For this private repository, the repository owner must grant your confirmed GitHub account access.

Install Git and Python 3.10 or newer if absent. Install or open your preferred
Codex interface using the [official quickstart](https://learn.chatgpt.com/docs/quickstart).
Then clone with your own authenticated Git client:

```text
git clone https://github.com/YOUR-OWNER/YOUR-REPOSITORY.git
cd YOUR-REPOSITORY
python 05-mxm-construct/means/scripts/aide.py start
```

Use `python3` on macOS/Linux if `python` is unavailable. On Windows use `python`
or `py -3` as appropriate for your Python installation. The implementation uses
portable Python/Git operations; only the development Linux host has been tested.

Open this folder as a project in the Codex desktop app or IDE. For CLI users,
start `codex` from this directory after installation/sign-in. Use this prompt:

> Start YOUR-REPOSITORY. Read AGENTS.md, MXM.md and the required MxM surfaces, run
> the session briefing, and help me finish onboarding. Tell me which files
> you loaded and what you still need to know about my setup.

Codex supports project AGENTS.md guidance; see
[official instruction discovery](https://learn.chatgpt.com/docs/agent-configuration/agents-md).
This repo changes no global AGENTS.md, Codex configuration, credentials, hooks
or existing projects. Its identity instructions apply when this workspace is
loaded. Cross-project global integration is a separate optional setup step.

## Personalize together

Tell the aide your preferred name, work priorities, communication preferences,
OS and Codex interface. It should update profile.json from your confirmed
answers, preserve unknowns as null, and record the source/date in MEMORY.md.
Confirm the permissions appropriate for your machine and actual tools. Use your own credentials and permission settings. Keep your chosen Codex model;
this repository does not pin or change it.

## Prove continuity

1. Ask it to record a harmless preference, with your confirmation and date.
2. Run `python 05-mxm-construct/means/scripts/aide.py verify` and the tests below.
3. Start a genuinely new Codex session in this folder. Ask it who it serves,
   what preference was saved, and which source supports the answer.
4. Give it a small real task. Check the result and its evidence before accepting.
5. Record the OS, interface/version, loaded files and result in MEMORY.md.

This clean-session check is pending; local Python tests cannot establish it.
For a manual candidate note, create a harmless UTF-8 text file in `06-operations/local/`:

```text
python 05-mxm-construct/means/scripts/aide.py remember --title "Preference to confirm" --source "Onboarding conversation" --file 06-operations/local/note.txt
python -m unittest discover -s 05-mxm-construct/means/scripts/tests -v
python 05-mxm-construct/means/scripts/aide.py wrap
```

Review and commit intended changes before wrap: it refuses a dirty checkout.
It does not push or prove remote synchronization. Review personal notes before
publication. A candidate note is not treated as confirmed merely by being saved.
