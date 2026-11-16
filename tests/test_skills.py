import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('registry', ROOT / 'tools/skills_registry.py')
registry = importlib.util.module_from_spec(spec)
spec.loader.exec_module(registry)
audit_spec = importlib.util.spec_from_file_location('source_audit', ROOT / 'tools/verify_skill_sources.py')
audit = importlib.util.module_from_spec(audit_spec)
audit_spec.loader.exec_module(audit)


class SourceAuditTest(unittest.TestCase):
    def test_readiness_inventory_covers_all_sources(self):
        report = (ROOT / 'docs/REPOSITORY_READINESS.md').read_text()
        for name, _ in audit.sources():
            with self.subTest(name=name):
                self.assertIn(f'[{name}](', report)

    def test_content_and_symlink_comparison(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            left, right = root / 'left', root / 'right'
            left.mkdir()
            right.mkdir()
            for directory in (left, right):
                (directory / 'a').write_text('same')
                (directory / 'link').symlink_to('a')
            self.assertEqual(audit.compare(left, right), ([], [], []))
            (left / 'a').write_text('different')
            (left / 'extra').write_text('extra')
            (left / 'link').unlink()
            (left / 'link').symlink_to('other')
            self.assertEqual(audit.compare(left, right), ([], ['extra'], ['a', 'link']))

    def test_source_inventory_and_missing(self):
        entries = dict(audit.sources())
        self.assertIn('rea', entries)
        self.assertIn('anthropics-skills', entries)
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(audit.audit('rea', entries['rea'], Path(tmp))[0], 'MISSING')


class RegistryTest(unittest.TestCase):
    def test_all_sources_and_missing_frontmatter(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = ['skills/a/SKILL.md', 'community/rea/skills/x/SKILL.md',
                     'community/other/a b/SKILL.md', 'misc/no/SKILL.md']
            for i, rel in enumerate(paths):
                path = root / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('---\nname: example\ndescription: >\n  useful skill\n---\n' if i < 3 else '# No frontmatter\n')
            self.assertEqual(registry.build(root), 4)
            result = (root / 'SKILLS-REGISTRY.md').read_text()
            self.assertIn('community/rea/skills/x/SKILL.md', result)
            self.assertIn('a%20b/SKILL.md', result)
            self.assertIn('No frontmatter name', result)
            self.assertIn('useful skill', result)

    def test_missing_root_fails(self):
        with self.assertRaises(ValueError):
            registry.build('/nonexistent-skills-dir-test')


class InstallerTest(unittest.TestCase):
    def test_force_refuses_unmanaged_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'existing'
            root.mkdir()
            (root / 'important.txt').write_text('keep me')
            env = dict(os.environ, SKILLS_DIR=str(root))
            result = subprocess.run(['bash', str(ROOT / 'tools/install-skills.sh'), '--force'],
                                    env=env, text=True, capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual((root / 'important.txt').read_text(), 'keep me')

    def test_failure_is_reported_and_retry_works(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            bindir = base / 'bin'
            bindir.mkdir()
            git = bindir / 'git'
            git.write_text('''#!/usr/bin/env bash
url="${@: -2:1}"; dest="${@: -1}"
if [[ "$url" == *"flowsint.git" && "${FAIL_FLOWSINT:-}" == 1 ]]; then exit 1; fi
mkdir -p "$dest/.git" "$dest/skills/test"
printf '%s\\n' '---' 'name: test' 'description: test' '---' > "$dest/skills/test/SKILL.md"
''')
            git.chmod(0o755)
            env = dict(os.environ, PATH=str(bindir) + os.pathsep + os.environ['PATH'],
                       SKILLS_DIR=str(base / 'skills'), FAIL_FLOWSINT='1')
            command = ['bash', str(ROOT / 'tools/install-skills.sh')]
            result = subprocess.run(command, env=env, text=True, capture_output=True)
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('flowsint', result.stderr)
            self.assertFalse((base / 'skills/community/flowsint').exists())
            self.assertTrue((base / 'skills/SKILLS-REGISTRY.md').exists())
            env['FAIL_FLOWSINT'] = '0'
            result = subprocess.run(command, env=env, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((base / 'skills/community/flowsint/skills/test/SKILL.md').exists())
            self.assertFalse((base / 'skills/community/flowsint/.git').exists())
            self.assertIn('community/flowsint', (base / 'skills/SKILLS-REGISTRY.md').read_text())


if __name__ == '__main__':
    unittest.main()
