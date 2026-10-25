import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[4]
SCRIPT = Path('05-mxm-construct/means/scripts/aide.py')
spec = importlib.util.spec_from_file_location('aide', SOURCE / SCRIPT)
aide = importlib.util.module_from_spec(spec)
spec.loader.exec_module(aide)


class AideTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'workspace with spaces'
        shutil.copytree(SOURCE, self.root, ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc', 'local'))
        self.git('init', '-b', 'test')

    def git(self, *args):
        return subprocess.run(['git', '-C', str(self.root), *args],
                              check=True, capture_output=True, text=True)

    def run_tool(self, command):
        return subprocess.run([sys.executable, str(self.root / SCRIPT), command],
                              cwd=self.temp.name, capture_output=True, text=True)

    def test_clean_structure(self):
        self.assertEqual(aide.verify(self.root), [])

    def test_missing_surface_fails(self):
        (self.root / '05-mxm-construct/meta-harness/morals.md').unlink()
        self.assertTrue(any('morals.md' in error for error in aide.verify(self.root)))
        self.assertEqual(self.run_tool('start').returncode, 1)

    def test_broken_local_link_fails(self):
        with (self.root / 'MEMORY.md').open('a') as f:
            f.write('\n[bad](missing.md)\n')
        self.assertTrue(any('Broken' in error for error in aide.verify(self.root)))

    def test_profile_wrong_shape_fails(self):
        (self.root / '05-mxm-construct/meta-harness/profile.json').write_text('[]')
        self.assertTrue(any('profile' in error for error in aide.verify(self.root)))

    def test_nonlocal_link_fails(self):
        with (self.root / 'MEMORY.md').open('a') as f:
            f.write('\n[bad](../)\n')
        self.assertTrue(any('nonlocal' in error for error in aide.verify(self.root)))

    def test_caller_directory_independent(self):
        result = self.run_tool('start')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('personal-aide', result.stdout)
        self.assertIn('Onboarding: pending', result.stdout)
        for name in ('mission.md', 'mind.md', 'morals.md'):
            self.assertIn(name, result.stdout)

    def test_dirty_wrap_refused_clean_wrap_passes(self):
        self.assertEqual(self.run_tool('wrap').returncode, 1)
        self.git('add', '.')
        self.git('-c', 'user.name=Test', '-c', 'user.email=test@example.invalid',
                 '-c', 'commit.gpgsign=false', 'commit', '-m', 'fixture')
        self.assertEqual(self.run_tool('wrap').returncode, 0)
        (self.root / 'untracked.txt').write_text('pending work')
        self.assertEqual(self.run_tool('wrap').returncode, 1)

    def test_memory_preserves_provenance_and_does_not_overwrite(self):
        paths = [aide.remember(self.root, 'Preference', 'Test conversation', 'Concise please') for _ in range(2)]
        self.assertNotEqual(paths[0], paths[1])
        note = json.loads(paths[0].read_text())
        self.assertEqual(note['status'], 'candidate')
        self.assertEqual(note['source'], 'Test conversation')
        self.assertEqual(aide.verify(self.root), [])

    def test_memory_self_promotion_refused(self):
        path = aide.remember(self.root, 'Preference', 'Test', 'Short answers')
        note = json.loads(path.read_text())
        note['status'] = 'active'
        path.write_text(json.dumps(note))
        self.assertTrue(any('self-promote' in error for error in aide.verify(self.root)))

    def test_secret_input_refused_without_write(self):
        with self.assertRaises(ValueError):
            aide.remember(self.root, 'Credential', 'Test', 'password=' + 'example-value')
        self.assertEqual(list((self.root / '05-mxm-construct/memory').glob('*.json')), [])

    def test_cli_memory_round_trip(self):
        source = Path(self.temp.name) / 'note.txt'
        source.write_text('A harmless preference', encoding='utf-8')
        result = subprocess.run([sys.executable, str(self.root / SCRIPT), 'remember',
                                 '--title', 'Preference', '--source', 'Test conversation',
                                 '--file', str(source)], cwd=self.temp.name,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(list((self.root / '05-mxm-construct/memory').glob('*.json'))), 1)
        self.assertEqual(self.run_tool('verify').returncode, 0)

    def test_cli_secret_refused_without_echo(self):
        source = Path(self.temp.name) / 'note.txt'
        value = 'password=' + 'test-sensitive-value'
        source.write_text(value, encoding='utf-8')
        result = subprocess.run([sys.executable, str(self.root / SCRIPT), 'remember',
                                 '--title', 'Credential', '--source', 'Test',
                                 '--file', str(source)], cwd=self.temp.name,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertNotIn(value, result.stdout + result.stderr)

    def test_empty_note_refused(self):
        with self.assertRaises(ValueError):
            aide.remember(self.root, 'Empty', 'Test', '  ')


if __name__ == '__main__':
    unittest.main()
