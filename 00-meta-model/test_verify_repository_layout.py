import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest

SOURCE=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('layout', SOURCE/'00-meta-model/verify-repository-layout.py')
layout=importlib.util.module_from_spec(spec)
spec.loader.exec_module(layout)


class LayoutTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        for path in layout.REQUIRED:
            dest=self.root/path
            dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(SOURCE/path,dest)

    def test_current_layout(self):
        self.assertEqual(layout.verify(self.root), [])

    def test_extra_root_directory(self):
        (self.root/'decisions').mkdir()
        self.assertTrue(any('Unexpected root' in e for e in layout.verify(self.root)))

    def test_extra_root_file(self):
        (self.root/'mode.md').write_text('shadow doorway')
        self.assertTrue(any('Unexpected root' in e for e in layout.verify(self.root)))

    def test_missing_operations(self):
        (self.root/'06-operations/README.md').unlink()
        self.assertTrue(any('06-operations' in e for e in layout.verify(self.root)))

    def test_flat_shadow_surface(self):
        (self.root/'05-mxm-construct/mind.md').write_text('A competing canonical surface')
        self.assertTrue(any('Shadow' in e for e in layout.verify(self.root)))

    def test_fenced_import_is_not_active(self):
        (self.root/'CLAUDE.md').write_text('# Claude adapter\n\nExample only, not active:\n```\n@AGENTS.md\n```\n')
        self.assertTrue(any('Claude adapter' in e for e in layout.verify(self.root)))

    def test_wrong_loading(self):
        p=self.root/'MXM.md'
        p.write_text(p.read_text().replace('Always-loaded','Optional'))
        self.assertTrue(any('loading' in e for e in layout.verify(self.root)))

    def test_missing_codex_instruction(self):
        p=self.root/'AGENTS.md'
        p.write_text(p.read_text().replace('explicitly','implicitly'))
        self.assertTrue(any('Codex' in e for e in layout.verify(self.root)))


if __name__ == '__main__':
    unittest.main()
