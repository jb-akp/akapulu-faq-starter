"""Behavioral checks for installation, source evidence, and draft API protection."""
import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import subprocess
import tempfile
import unittest
from unittest.mock import patch

KIT = Path(__file__).resolve().parents[1]
SCRIPTS = KIT / '.agents/skills/akapulu-faq/scripts'
sys.path.insert(0, str(SCRIPTS))
import verify_sources
import akapulu_api
spec = importlib.util.spec_from_file_location('installer', KIT / 'install.py')
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)

class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.project = self.root / 'project'
        shutil.copytree(KIT / 'tests/fixtures/clearbrief', self.project)
        # Keep the regression fixture a draft even after the actual demo is connected.
        path = self.project / 'akapulu/scenario.json'
        data = json.loads(path.read_text())
        data['nodes']['faq']['functions'][0]['knowledge_base_id'] = 'PLACEHOLDER_CREATE_KNOWLEDGE_BASE_FIRST'
        path.write_text(json.dumps(data))

    def test_install_preserves_existing_files_and_is_repeatable(self):
        protected = {'AGENTS.md': 'Existing project instructions\n', '.env': 'EXAMPLE_EXISTING_VALUE=sentinel\n',
                     '.agents/skills/unrelated/SKILL.md': 'Unrelated skill\n'}
        for name, content in protected.items():
            path = self.project / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        installer.install(self.project)
        installer.install(self.project)
        for name, content in protected.items():
            self.assertEqual((self.project / name).read_text(), content)
        self.assertEqual((self.project / '.gitignore').read_text().splitlines().count('.env'), 1)

    def test_install_refuses_differing_existing_skill(self):
        installer.install(self.project)
        path = self.project / '.agents/skills/akapulu-faq/SKILL.md'
        path.write_text('User customizations\n')
        with self.assertRaises(SystemExit):
            installer.install(self.project)
        self.assertEqual(path.read_text(), 'User customizations\n')

    def test_each_agent_installs_complete_helpers_and_preserves_project(self):
        for agent, (relative, instruction, _) in installer.TARGETS.items():
            with self.subTest(agent=agent):
                project = self.root / agent
                project.mkdir()
                for name in ('AGENTS.md', 'CLAUDE.md', '.env'):
                    (project / name).write_text('preserve-me\n')
                result = subprocess.run([sys.executable, str(KIT / 'install.py'), str(project), '--agent', agent], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                dest = project / relative
                self.assertTrue((dest / 'SKILL.md').is_file())
                self.assertTrue((dest / 'references/api.md').is_file())
                for name in ('AGENTS.md', 'CLAUDE.md', '.env'):
                    self.assertEqual((project / name).read_text(), 'preserve-me\n')
                # Run the installed copy from an unrelated cwd: catches broken relative paths/imports.
                result = subprocess.run([sys.executable, str(dest / 'scripts/verify_sources.py'), str(self.project)], cwd=self.root, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                installer.install(project, agent)

    def test_conflicting_target_stops_before_creating_credentials(self):
        for agent, (relative, _, _) in installer.TARGETS.items():
            with self.subTest(agent=agent):
                project = self.root / ('conflict-' + agent)
                dest = project / relative
                dest.mkdir(parents=True)
                (dest / 'SKILL.md').write_text('custom skill')
                with self.assertRaises(SystemExit):
                    installer.install(project, agent)
                self.assertFalse((project / '.env').exists())
                self.assertFalse((project / '.gitignore').exists())
                self.assertEqual((dest / 'SKILL.md').read_text(), 'custom skill')

    def test_new_project_key_file_private_and_instructions_match_agent(self):
        for agent, (relative, instruction, _) in installer.TARGETS.items():
            with self.subTest(agent=agent):
                project = self.root / ('fresh-' + agent)
                installer.install(project, agent)
                self.assertIn(relative + '/SKILL.md', (project / instruction).read_text())
                self.assertEqual((project / '.env').stat().st_mode & 0o777, 0o600)
                self.assertIn('AKAPULU_API_KEY=\n', (project / '.env').read_text())

    def test_draft_passes_but_ready_rejects_placeholder(self):
        self.assertIn('DRAFT', verify_sources.verify(self.project))
        with self.assertRaises(ValueError):
            verify_sources.verify(self.project, ready=True)

    def test_monthly_to_annual_is_rejected_even_if_manifest_also_changed(self):
        for name in ('knowledge.txt', 'sources.json'):
            path = self.project / 'akapulu' / name
            path.write_text(path.read_text().replace('The Team plan costs $49 per month', 'The Team plan costs $49 per year'))
        with self.assertRaisesRegex(ValueError, 'exact supported passage'):
            verify_sources.verify(self.project)

    def test_missing_evidence_rejected(self):
        path = self.project / 'akapulu/knowledge.txt'
        path.write_text(path.read_text() + 'There is a money-back guarantee.\n')
        with self.assertRaisesRegex(ValueError, 'matching evidence'):
            verify_sources.verify(self.project)

    def test_changed_snapshot_rejected(self):
        path = self.project / 'akapulu/sources/home.json'
        data = json.loads(path.read_text())
        data['text'] += ' altered'
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, 'snapshot changed'):
            verify_sources.verify(self.project)

    def test_draft_cannot_create_scenario_or_read_key(self):
        args = argparse.Namespace(file=str(self.project / 'akapulu/scenario.json'), avatar=None)
        with patch.object(akapulu_api, 'key_or_die') as key, patch.object(akapulu_api, 'request') as request:
            with self.assertRaises(SystemExit):
                akapulu_api.cmd_scenario_create(args)
            key.assert_not_called()
            request.assert_not_called()

if __name__ == '__main__':
    unittest.main()
