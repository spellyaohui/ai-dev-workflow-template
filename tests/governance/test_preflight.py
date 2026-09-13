import tempfile
import unittest
from pathlib import Path

from scripts.governance.preflight import CheckResult, check_repository, exit_code


REQUIRED = [
    'AGENTS.md',
    '.cursor/rules/core-ai-guardrails.mdc',
    '.cursor/rules/testing.mdc',
    '.cursor/rules/security.mdc',
    '.cursor/rules/database-safety.mdc',
    '.cursor/rules/pr-workflow.mdc',
    '.github/ISSUE_TEMPLATE/spec.yml',
    '.github/PULL_REQUEST_TEMPLATE.md',
    '.github/ai-governance.yml',
    '.github/workflows/pr-contract-gate.yml',
    '.github/workflows/verifier-gate.yml',
    '.github/workflows/verifier-gate-refresh.yml',
    'bots/grok/planner-spec-writer.md',
    'bots/grok/pr-producer.md',
    'bots/grok/pr-verifier.md',
    'bots/grok/bug-reproducer.md',
]


class PreflightTests(unittest.TestCase):
    def make_root(self, missing=None):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        missing = set(missing or [])
        for rel in REQUIRED:
            if rel in missing:
                continue
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('x\n', encoding='utf-8')
        return temp, root

    def test_all_local_assets_pass_and_external_integrations_warn(self):
        temp, root = self.make_root()
        self.addCleanup(temp.cleanup)
        results = check_repository(root)
        self.assertEqual(exit_code(results), 0)
        self.assertTrue(any(r.status == 'WARN' and r.name == 'grok-private-access' for r in results))
        self.assertTrue(any(r.status == 'WARN' and r.name == 'cursor-private-access' for r in results))
        self.assertFalse(any(r.status == 'FAIL' for r in results))

    def test_missing_required_asset_fails(self):
        temp, root = self.make_root(missing={'AGENTS.md'})
        self.addCleanup(temp.cleanup)
        results = check_repository(root)
        self.assertEqual(exit_code(results), 1)
        self.assertIn(CheckResult('FAIL', 'asset:AGENTS.md', 'missing required governance asset'), results)


if __name__ == '__main__':
    unittest.main()
