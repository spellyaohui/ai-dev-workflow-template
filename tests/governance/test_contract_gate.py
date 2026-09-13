import unittest

from scripts.governance.contract_gate import ContractValidationError, validate_contract


VALID_PR = """Spec-Issue: #17
Spec-Version: v1
Risk-Level: LOW

## Contract Source
Approved Spec #17 v1.

## Acceptance Criteria
- Works as approved.

## Affected Contracts
- None.

## Verification
- Run tests.

## Non-goals
- No unrelated work.

## Known Risks / Limitations
- None known.
"""

VALID_ISSUE = {
    "body": """Status: APPROVED
Version: v1
Risk-Level: LOW

# Goal
Implement the approved change.
""",
}


def assert_invalid(testcase, pr_body=VALID_PR, issue=VALID_ISSUE):
    with testcase.assertRaises(ContractValidationError):
        validate_contract(pr_body, issue)


class ContractGateTests(unittest.TestCase):
    def test_valid_approved_contract_passes(self):
        result = validate_contract(VALID_PR, VALID_ISSUE)
        self.assertEqual(result.issue_number, 17)
        self.assertEqual(result.version, "v1")
        self.assertEqual(result.risk, "LOW")

    def test_missing_spec_issue_fails(self):
        assert_invalid(self, VALID_PR.replace("Spec-Issue: #17\n", ""))

    def test_missing_spec_version_fails(self):
        assert_invalid(self, VALID_PR.replace("Spec-Version: v1\n", ""))

    def test_missing_risk_level_fails(self):
        assert_invalid(self, VALID_PR.replace("Risk-Level: LOW\n", ""))

    def test_duplicate_metadata_fails(self):
        assert_invalid(self, VALID_PR + "\nSpec-Version: v1\n")

    def test_html_comment_only_metadata_fails(self):
        body = VALID_PR.replace(
            "Spec-Issue: #17\n", "<!-- Spec-Issue: #17 -->\n"
        )
        assert_invalid(self, body)

    def test_unapproved_issue_fails(self):
        issue = {"body": VALID_ISSUE["body"].replace("APPROVED", "READY_FOR_APPROVAL")}
        assert_invalid(self, issue=issue)

    def test_issue_version_mismatch_fails(self):
        issue = {"body": VALID_ISSUE["body"].replace("Version: v1", "Version: v2")}
        assert_invalid(self, issue=issue)

    def test_issue_risk_mismatch_fails(self):
        issue = {"body": VALID_ISSUE["body"].replace("Risk-Level: LOW", "Risk-Level: HIGH")}
        assert_invalid(self, issue=issue)

    def test_issue_reference_is_pr_fails(self):
        issue = dict(VALID_ISSUE)
        issue["pull_request"] = {"url": "https://example.invalid/pr/17"}
        assert_invalid(self, issue=issue)

    def test_empty_required_section_fails(self):
        body = VALID_PR.replace(
            "## Verification\n- Run tests.\n",
            "## Verification\n<!-- fill this later -->\n",
        )
        assert_invalid(self, body)

    def test_issue_form_fields_are_supported(self):
        issue = {
            "body": """### Spec Status
APPROVED

### Spec Version
v1

### Risk Level
LOW

### Goal
Implement it.
"""
        }
        result = validate_contract(VALID_PR, issue)
        self.assertEqual(result.risk, "LOW")


if __name__ == "__main__":
    unittest.main()
