import unittest

from scripts.governance.verifier_gate import VerifierValidationError, validate_verifier_evidence

HEAD = "a" * 40
OTHER_HEAD = "b" * 40
VALID_PR_BODY = """Spec-Issue: #17
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


def pr(*, body=VALID_PR_BODY, author="cursor-agent", head=HEAD):
    return {
        "number": 1,
        "user": {"login": author},
        "head": {"sha": head},
        "body": body,
    }


def review(
    *,
    review_id=10,
    reviewer="verifier-bot",
    state="APPROVED",
    association="COLLABORATOR",
    commit_id=HEAD,
    verdict="PASS",
    spec_issue=17,
    spec_version="v1",
    verified_head=HEAD,
    risk="LOW",
    body=None,
):
    if body is None:
        body = (
            f"VERDICT: {verdict}\n"
            f"SPEC: #{spec_issue} {spec_version}\n"
            f"VERIFIED_HEAD: {verified_head}\n"
            f"RISK: {risk}\n"
        )
    return {
        "id": review_id,
        "user": {"login": reviewer},
        "state": state,
        "author_association": association,
        "commit_id": commit_id,
        "body": body,
    }


class VerifierGateTests(unittest.TestCase):
    def assert_invalid(self, pull_request=None, reviews=None):
        with self.assertRaises(VerifierValidationError):
            validate_verifier_evidence(pull_request or pr(), reviews or [])

    def test_no_pass_review_fails(self):
        self.assert_invalid(reviews=[])

    def test_pass_exact_head_and_spec_passes(self):
        result = validate_verifier_evidence(pr(), [review()])
        self.assertEqual(result.reviewer, "verifier-bot")
        self.assertEqual(result.verified_head, HEAD)
        self.assertEqual(result.risk, "LOW")

    def test_pass_stale_verified_head_fails(self):
        self.assert_invalid(reviews=[review(verified_head=OTHER_HEAD)])

    def test_review_commit_id_must_match_current_head(self):
        self.assert_invalid(reviews=[review(commit_id=OTHER_HEAD)])

    def test_spec_mismatch_fails(self):
        self.assert_invalid(reviews=[review(spec_issue=18)])

    def test_duplicate_review_metadata_fails(self):
        body = review()["body"] + "VERDICT: PASS\n"
        self.assert_invalid(reviews=[review(body=body)])

    def test_html_comment_metadata_does_not_count(self):
        body = (
            f"<!-- VERDICT: PASS -->\n"
            f"SPEC: #17 v1\n"
            f"VERIFIED_HEAD: {HEAD}\n"
            "RISK: LOW\n"
        )
        self.assert_invalid(reviews=[review(body=body)])

    def test_pr_author_self_review_fails(self):
        self.assert_invalid(reviews=[review(reviewer="cursor-agent")])

    def test_untrusted_author_association_fails(self):
        self.assert_invalid(reviews=[review(association="CONTRIBUTOR")])

    def test_later_changes_requested_supersedes_prior_approved(self):
        reviews = [
            review(review_id=10),
            review(review_id=11, state="CHANGES_REQUESTED", body="Please fix."),
        ]
        self.assert_invalid(reviews=reviews)

    def test_later_dismissed_supersedes_prior_approved(self):
        reviews = [
            review(review_id=10),
            review(review_id=11, state="DISMISSED", body="Dismissed."),
        ]
        self.assert_invalid(reviews=reviews)

    def test_comment_cannot_satisfy(self):
        self.assert_invalid(reviews=[review(state="COMMENTED")])

    def test_spec_high_cannot_be_downgraded_by_verifier_low(self):
        high_body = VALID_PR_BODY.replace("Risk-Level: LOW", "Risk-Level: HIGH")
        self.assert_invalid(pull_request=pr(body=high_body), reviews=[review(risk="LOW")])

    def test_spec_low_may_be_upgraded_by_verifier_high(self):
        result = validate_verifier_evidence(pr(), [review(risk="HIGH")])
        self.assertEqual(result.risk, "HIGH")


if __name__ == "__main__":
    unittest.main()
