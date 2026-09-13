import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class WorkflowSecurityTests(unittest.TestCase):
    def test_required_gates_use_trusted_base_code_only(self):
        for rel in [
            '.github/workflows/pr-contract-gate.yml',
            '.github/workflows/verifier-gate.yml',
        ]:
            text = (ROOT / rel).read_text(encoding='utf-8')
            self.assertNotIn('actions/checkout', text)
            self.assertNotIn('pull_request.head.sha', text)
            self.assertIn('pull_request.base.sha', text)
            self.assertIn('/tmp/trusted-governance', text)

    def test_verifier_refresh_does_not_execute_repository_code(self):
        text = (ROOT / '.github/workflows/verifier-gate-refresh.yml').read_text(encoding='utf-8')
        self.assertNotIn('actions/checkout', text)
        self.assertNotIn('scripts/governance/', text)
        self.assertIn('runs/{run_id}/rerun', text)


if __name__ == '__main__':
    unittest.main()
