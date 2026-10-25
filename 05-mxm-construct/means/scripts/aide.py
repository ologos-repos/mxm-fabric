#!/usr/bin/env python3
"""Portable, explicit lifecycle checks for personal-aide; no network or model calls."""
import argparse
import importlib.util
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess
import sys
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[3]
SURFACES = ('mission', 'mind', 'morals', 'memory', 'methods', 'means')
REQUIRED = ('AGENTS.md', 'CLAUDE.md', 'MXM.md', 'MEMORY.md',
            '05-mxm-construct/meta-harness/profile.json',
            '06-operations/runbooks/ONBOARDING.md', '05-mxm-construct/means/README.md') + tuple(
                f'05-mxm-construct/meta-harness/{name}.md' for name in SURFACES if name != 'means')
SECRET = re.compile(
    r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|'
    r'\b(?:ghp_|github_pat_|sk-)[A-Za-z0-9_-]{20,}|'
    r'\b(?:password|token|api_key|secret)\s*[:=]\s*\S+', re.I)


def git(root, *args):
    result = subprocess.run(['git', '-C', str(root), *args],
                            capture_output=True, text=True, check=True)
    return result.stdout.strip()


def read_profile(root):
    return json.loads((root / '05-mxm-construct/meta-harness/profile.json').read_text(encoding='utf-8'))


def verify(root):
    gate_path = root / '00-meta-model/verify-repository-layout.py'
    if not gate_path.is_file():
        return ['Missing required layout gate']
    spec = importlib.util.spec_from_file_location('repository_layout', gate_path)
    gate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gate)
    errors = gate.verify(root)
    for name in REQUIRED:
        p = root / name
        if not p.is_file() or not p.read_text(encoding='utf-8').strip():
            errors.append(f'Missing or empty required file: {name}')
    try:
        profile = read_profile(root)
        if not isinstance(profile, dict):
            raise ValueError('profile must be an object')
        if profile.get('schema_version') != 1:
            errors.append('Unsupported profile schema')
        if not isinstance(profile.get('aide_name'), str) or not profile['aide_name'].strip():
            errors.append('Aide identity is required')
        if not isinstance(profile.get('principal_operator'), str) or not profile['principal_operator'].strip():
            errors.append('Principal operator is required')
        for key in ('operating_system', 'codex_interface', 'github_username'):
            if key not in profile or (profile[key] is not None and not isinstance(profile[key], str)):
                errors.append(f'Profile {key} must be a string or null')
        for key in ('work_priorities', 'communication_preferences'):
            value = profile.get(key)
            if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
                errors.append(f'Profile {key} must be a list of strings')
        if profile.get('onboarding_status') not in ('pending', 'complete'):
            errors.append('Invalid onboarding status')
    except (OSError, ValueError) as exc:
        errors.append(f'Invalid profile: {exc}')
    for entry in ('AGENTS.md', 'CLAUDE.md'):
        p = root / entry
        if p.is_file() and 'MXM.md' not in p.read_text(encoding='utf-8'):
            errors.append(f'{entry} does not route to MXM.md')
    mxm = root / 'MXM.md'
    if mxm.is_file():
        value = mxm.read_text(encoding='utf-8')
        for token in ('Meta-Harness', *[f'{s}.md' for s in SURFACES if s != 'means'], '05-mxm-construct/means/README.md'):
            if token not in value:
                errors.append(f'MXM.md missing declaration: {token}')
    markdown = [root / name for name in REQUIRED if name.endswith('.md')]
    markdown += list((root / '05-mxm-construct').rglob('README.md'))
    for p in markdown:
        if not p.is_file():
            continue
        content = p.read_text(encoding='utf-8')
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', content):
            if '://' in target or target.startswith('#'):
                continue
            target = target.split('#', 1)[0]
            resolved = (p.parent / target).resolve()
            if not resolved.is_relative_to(root.resolve()) or not resolved.exists():
                errors.append(f'Broken or nonlocal link in {p.relative_to(root)}: {target}')
        if SECRET.search(content):
            errors.append(f'Secret-shaped content in {p.relative_to(root)} (value redacted)')
    for p in (root / '05-mxm-construct/memory').glob('*.json'):
        try:
            note = json.loads(p.read_text(encoding='utf-8'))
            if not isinstance(note, dict):
                raise ValueError('note must be an object')
            for field in ('id', 'title', 'source', 'created_at', 'text'):
                if not isinstance(note.get(field), str) or not note[field].strip():
                    raise ValueError(f'missing {field}')
            if note.get('status') != 'candidate':
                raise ValueError('candidate records cannot self-promote')
            if note['id'] != p.stem:
                raise ValueError('note ID differs from filename')
            stamp = datetime.fromisoformat(note['created_at'])
            if stamp.tzinfo is None:
                raise ValueError('timestamp requires timezone')
            if SECRET.search(json.dumps(note)):
                raise ValueError('secret-shaped content (value redacted)')
        except (OSError, ValueError) as exc:
            errors.append(f'Invalid memory {p.name}: {exc}')
    return errors


def remember(root, title, source, text):
    if not all(value.strip() for value in (title, source, text)):
        raise ValueError('title, source and note text must be nonempty')
    if SECRET.search('\n'.join((title, source, text))):
        raise ValueError('Secret-shaped input refused; keep credentials in a credential manager')
    now = datetime.now(timezone.utc)
    note_id = now.strftime('%Y%m%dT%H%M%SZ') + '-' + uuid4().hex
    note = dict(id=note_id, title=title, source=source, text=text,
                created_at=now.isoformat(), status='candidate')
    folder = root / '05-mxm-construct/memory'
    folder.mkdir(parents=True, exist_ok=True)
    dest = folder / (note_id + '.json')
    with dest.open('x', encoding='utf-8') as handle:
        json.dump(note, handle, indent=2, ensure_ascii=False)
        handle.write('\n')
    return dest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    for cmd in ('start', 'verify', 'wrap'):
        commands.add_parser(cmd)
    notes = commands.add_parser('remember')
    notes.add_argument('--title', required=True)
    notes.add_argument('--source', required=True)
    notes.add_argument('--file', required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        errors = verify(ROOT)
        if errors:
            for error in errors:
                print('FAIL: ' + error, file=sys.stderr)
            return 1
        if args.command == 'remember':
            dest = remember(ROOT, args.title, args.source, args.file.read_text(encoding='utf-8'))
            print(f'Candidate saved: {dest.relative_to(ROOT)}. Review before committing.')
        elif args.command == 'start':
            for name in ('MXM.md', '05-mxm-construct/meta-harness/mission.md', '05-mxm-construct/meta-harness/mind.md',
                         '05-mxm-construct/meta-harness/morals.md', '05-mxm-construct/meta-harness/profile.json', 'MEMORY.md', '05-mxm-construct/memory/meta-context/current/ACTIVE-FOCUS.md'):
                print(f'\n=== {name} ===\n{(ROOT / name).read_text(encoding="utf-8")}')
            print('Git branch: ' + git(ROOT, 'branch', '--show-current'))
            print('Git status:\n' + (git(ROOT, 'status', '--short') or 'clean'))
            candidates = sorted((ROOT / '05-mxm-construct/memory').glob('*.json'))
            print('Candidate memory IDs (read relevant records; not accepted facts):')
            print('\n'.join(p.stem for p in candidates) or 'none')
            print('Onboarding: ' + read_profile(ROOT)['onboarding_status'])
        elif args.command == 'wrap':
            if git(ROOT, 'status', '--porcelain'):
                print('FAIL: uncommitted or untracked files; review and commit intended changes.', file=sys.stderr)
                return 1
            print('PASS: structural checks and clean checkout. Tests, publication and human acceptance are separate.')
        else:
            print('PASS: starter structural contract. No runtime or model-obedience claim.')
        return 0
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f'FAIL: {type(exc).__name__}: local operation failed; check input files and Git availability.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
