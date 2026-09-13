import unittest

from scripts.governance.state import WorkflowSnapshot, derive_state


def snap(**overrides):
    data = dict(
        spec_status='APPROVED',
        pr_exists=False,
        pr_open=False,
        pr_merged=False,
        implementation_started=False,
        contract_ok=None,
        verifier_ok=None,
        verifier_verdict=None,
        merge_eligible=False,
        main_verified=False,
        completion_recorded=False,
        automation_failed=False,
    )
    data.update(overrides)
    return WorkflowSnapshot(**data)


class WorkflowStateTests(unittest.TestCase):
    def test_draft(self):
        self.assertEqual(derive_state(snap(spec_status='DRAFT')), 'DRAFT')

    def test_ready_for_approval(self):
        self.assertEqual(
            derive_state(snap(spec_status='READY_FOR_APPROVAL')),
            'READY_FOR_APPROVAL',
        )

    def test_approved(self):
        self.assertEqual(derive_state(snap()), 'APPROVED')

    def test_implementing(self):
        self.assertEqual(
            derive_state(snap(implementation_started=True)),
            'IMPLEMENTING',
        )

    def test_pr_open(self):
        self.assertEqual(
            derive_state(snap(pr_exists=True, pr_open=True, implementation_started=True)),
            'PR_OPEN',
        )

    def test_verifying(self):
        self.assertEqual(
            derive_state(
                snap(
                    pr_exists=True,
                    pr_open=True,
                    implementation_started=True,
                    contract_ok=True,
                    verifier_ok=False,
                )
            ),
            'VERIFYING',
        )

    def test_blocked_from_contract_failure(self):
        self.assertEqual(
            derive_state(snap(pr_exists=True, pr_open=True, contract_ok=False)),
            'BLOCKED',
        )

    def test_blocked_from_verifier_block(self):
        self.assertEqual(
            derive_state(
                snap(pr_exists=True, pr_open=True, contract_ok=True, verifier_verdict='BLOCK')
            ),
            'BLOCKED',
        )

    def test_hold(self):
        self.assertEqual(
            derive_state(
                snap(pr_exists=True, pr_open=True, contract_ok=True, verifier_verdict='HOLD')
            ),
            'HOLD',
        )

    def test_pass(self):
        self.assertEqual(
            derive_state(
                snap(
                    pr_exists=True,
                    pr_open=True,
                    contract_ok=True,
                    verifier_ok=True,
                    verifier_verdict='PASS',
                )
            ),
            'PASS',
        )

    def test_merge_ready(self):
        self.assertEqual(
            derive_state(
                snap(
                    pr_exists=True,
                    pr_open=True,
                    contract_ok=True,
                    verifier_ok=True,
                    verifier_verdict='PASS',
                    merge_eligible=True,
                )
            ),
            'MERGE_READY',
        )

    def test_merged_not_completed(self):
        self.assertEqual(
            derive_state(snap(pr_exists=True, pr_open=False, pr_merged=True)),
            'MERGED',
        )

    def test_post_merge_verified(self):
        self.assertEqual(
            derive_state(
                snap(pr_exists=True, pr_open=False, pr_merged=True, main_verified=True)
            ),
            'POST_MERGE_VERIFIED',
        )

    def test_completed_requires_recorded_completion(self):
        self.assertEqual(
            derive_state(
                snap(
                    pr_exists=True,
                    pr_open=False,
                    pr_merged=True,
                    main_verified=True,
                    completion_recorded=True,
                )
            ),
            'COMPLETED',
        )

    def test_automation_failure_wins(self):
        self.assertEqual(derive_state(snap(automation_failed=True)), 'FAILED')


if __name__ == '__main__':
    unittest.main()
