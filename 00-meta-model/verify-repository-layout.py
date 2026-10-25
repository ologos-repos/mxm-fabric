#!/usr/bin/env python3
"""Validate the portable MxM Meta-Harness root and bootstrap contract."""
import argparse
from pathlib import Path
import re

ROOT_DIRS = {'.git', '.github', '.gitea', '.claude', '.codex', *(f'{n:02}-{name}' for n, name in enumerate((
    'meta-model', 'strategic-baseline', 'systems-baseline', 'solutions-baseline',
    'work-packages', 'mxm-construct', 'operations')))}
ROOT_FILES = {'.git', '.gitignore', 'AGENTS.md', 'CLAUDE.md', 'LICENSE', 'MXM.md', 'MEMORY.md', 'README.md'}
SURFACES = {name: f'05-mxm-construct/meta-harness/{name.lower()}.md'
            for name in ('Mission', 'Mind', 'Morals', 'Memory', 'Methods')}
SURFACES['Means'] = '05-mxm-construct/means/README.md'
BASELINES = ('01-strategic-baseline/1.1-vision', '01-strategic-baseline/1.2-strategy',
             '01-strategic-baseline/1.3-objectives-krs', '01-strategic-baseline/1.4-alignment-references',
             '02-systems-baseline/2.1-requirements', '02-systems-baseline/2.2-architecture',
             '02-systems-baseline/2.3-behavior', '02-systems-baseline/2.4-interfaces',
             '02-systems-baseline/2.5-verification')
REQUIRED = tuple(SURFACES.values()) + tuple(p+'/README.md' for p in BASELINES) + (
    '00-meta-model/work-model.md', '01-strategic-baseline/README.md',
    '02-systems-baseline/README.md', '03-solutions-baseline/README.md',
    '04-work-packages/README.md', '06-operations/README.md',
    '05-mxm-construct/memory/wiki/index.md',
    '05-mxm-construct/memory/meta-context/current/ACTIVE-FOCUS.md',
    '05-mxm-construct/means/scripts/session-start.py',
    '05-mxm-construct/means/scripts/session-wrap.py',
    '05-mxm-construct/means/scripts/aide.py',
    '05-mxm-construct/meta-harness/profile.json',
    'AGENTS.md', 'CLAUDE.md', 'MXM.md', 'MEMORY.md', 'README.md')


def operative(text):
    text = re.sub(r'(?ms)^\s*(```|~~~).*?^\s*\1\s*$', '', text)
    return re.sub(r'(?s)<!--.*?-->', '', text)


def verify(root):
    root = Path(root)
    errors = []
    for p in root.iterdir():
        allowed = ROOT_DIRS if p.is_dir() else ROOT_FILES
        if p.name not in allowed:
            errors.append(f'Unexpected root entry: {p.name}')
    for path in REQUIRED:
        p = root / path
        if not p.is_file() or len(p.read_text(encoding='utf-8').strip()) < 40:
            errors.append(f'Missing or non-substantive file: {path}')
    for name in SURFACES:
        shadow = root / f'05-mxm-construct/{name.lower()}.md'
        if shadow.exists():
            errors.append(f'Shadow surface: {shadow.relative_to(root)}')
    def read(path):
        p = root / path
        return operative(p.read_text(encoding='utf-8')) if p.is_file() else ''
    agents = read('AGENTS.md')
    claude = read('CLAUDE.md')
    mxm = read('MXM.md')
    if not re.search(r'(?m)^@AGENTS\.md\s*$', claude):
        errors.append('Claude adapter must import AGENTS.md')
    if not re.search(r'\]\(MXM\.md\)', agents):
        errors.append('AGENTS.md must link the canonical MXM.md')
    for name in ('Mission', 'Mind', 'Morals'):
        if not re.search(r'(?m)^@'+re.escape(SURFACES[name])+r'\s*$', agents):
            errors.append(f'AGENTS.md missing active import: {name}')
    if not all(word in agents for word in ('Codex', 'explicitly')):
        errors.append('Codex explicit-read instructions missing')
    if not re.search(r'(?m)^\| Repository-class \| Meta-Harness \|$', mxm):
        errors.append('Meta-Harness profile declaration missing')
    for name,path in SURFACES.items():
        loading='Always-loaded' if name in ('Mission','Mind','Morals') else 'Pointer-shaped; read on need'
        row = re.search(r'(?m)^\| '+name+r' \|.*$', mxm)
        if not row or f']({path})' not in row.group() or loading not in row.group():
            errors.append(f'Canonical surface/loading declaration wrong: {name}')
    for name,path,companion in (('Memory',SURFACES['Memory'],'05-mxm-construct/memory/'),
                                ('Means',SURFACES['Means'],'05-mxm-construct/means/')):
        text=read(path)
        if '## Companion rationale' not in text or companion not in text:
            errors.append(f'{name} companion rationale missing')
    return errors


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args=parser.parse_args()
    errors=verify(args.root)
    for error in errors:
        print('FAIL: '+error)
    if not errors:
        print('PASS: portable MxM Meta-Harness layout and bootstrap contract')
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
