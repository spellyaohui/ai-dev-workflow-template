from __future__ import annotations

from dataclasses import dataclass
import json
import os
import re
import sys

from scripts.governance.common import GitHubAPIError, github_get_json, strip_html_comments
from scripts.governance.contract_gate import ContractValidationError, parse_pr_contract


@dataclass(frozen=True)
class VerifierEvidence:
    reviewer: str
    review_id: int
    verified_head: str
    spec_issue: int
    spec_version: str
    risk: str


class VerifierValidationError(ValueError):
    pass


def _exact(pattern: str, body: str) -> str | tuple[str, ...] | None:
    matches = re.findall(pattern, body, flags=re.M)
    if len(matches) != 1:
        return None
    return matches[0]


def validate_verifier_evidence(
    pull_request: dict,
    reviews: list[dict],
) -> VerifierEvidence:
    pr_author = ((pull_request.get("user") or {}).get("login") or "").strip()
    head_sha = ((pull_request.get("head") or {}).get("sha") or "").strip().lower()
    if not head_sha or not re.fullmatch(r"[0-9a-f]{40}", head_sha):
        raise VerifierValidationError("Current pull request head SHA is missing or invalid.")

    try:
        contract = parse_pr_contract(pull_request.get("body") or "")
    except ContractValidationError as exc:
        raise VerifierValidationError(str(exc)) from exc

    decision_states = {"APPROVED", "CHANGES_REQUESTED", "DISMISSED"}
    latest_by_reviewer: dict[str, dict] = {}
    for candidate in reviews:
        reviewer = ((candidate.get("user") or {}).get("login") or "").strip()
        state = (candidate.get("state") or "").upper()
        if not reviewer or state not in decision_states:
            continue
        review_id = int(candidate.get("id") or 0)
        current = latest_by_reviewer.get(reviewer)
        if current is None or review_id > int(current.get("id") or 0):
            latest_by_reviewer[reviewer] = candidate

    valid: list[VerifierEvidence] = []
    for reviewer, candidate in latest_by_reviewer.items():
        if (candidate.get("state") or "").upper() != "APPROVED":
            continue
        if reviewer.lower() == pr_author.lower():
            continue
        if (candidate.get("author_association") or "").upper() not in {
            "OWNER",
            "COLLABORATOR",
        }:
            continue

        review_commit = (candidate.get("commit_id") or "").lower()
        if review_commit != head_sha:
            continue

        body = strip_html_comments(candidate.get("body") or "")
        verdict = _exact(r"^VERDICT:\s*(PASS|BLOCK|HOLD)\s*$", body)
        spec = _exact(r"^SPEC:\s*#([1-9][0-9]*)\s+(v[1-9][0-9]*)\s*$", body)
        verified_head = _exact(r"^VERIFIED_HEAD:\s*([0-9a-fA-F]{40})\s*$", body)
        risk = _exact(r"^RISK:\s*(LOW|HIGH)\s*$", body)

        if not isinstance(verdict, str) or verdict != "PASS":
            continue
        if not (isinstance(spec, tuple) and len(spec) == 2):
            continue
        if not isinstance(verified_head, str) or verified_head.lower() != head_sha:
            continue
        if not isinstance(risk, str):
            continue

        spec_issue, spec_version = spec
        if int(spec_issue) != contract.issue_number or spec_version != contract.version:
            continue
        if contract.risk == "HIGH" and risk != "HIGH":
            continue

        valid.append(
            VerifierEvidence(
                reviewer=reviewer,
                review_id=int(candidate.get("id") or 0),
                verified_head=head_sha,
                spec_issue=contract.issue_number,
                spec_version=contract.version,
                risk=risk,
            )
        )

    if not valid:
        raise VerifierValidationError(
            "No valid independent verifier PASS review exists for the current head SHA and Spec."
        )

    return max(valid, key=lambda evidence: evidence.review_id)


def main() -> int:
    repository = os.environ.get("GITHUB_REPOSITORY", "")
    token = os.environ.get("GITHUB_TOKEN", "")
    event_path = os.environ.get("GITHUB_EVENT_PATH", "")
    if not repository or not event_path:
        print("::error::Missing GITHUB_REPOSITORY or GITHUB_EVENT_PATH.")
        return 1

    try:
        with open(event_path, "r", encoding="utf-8") as handle:
            event = json.load(handle)
        event_pr = event.get("pull_request") or {}
        pr_number = event.get("number") or event_pr.get("number")
        if not pr_number:
            raise VerifierValidationError("Unable to determine pull request number.")
        current_pr = github_get_json(
            f"https://api.github.com/repos/{repository}/pulls/{pr_number}",
            token,
            "verifier-gate",
        )
        reviews = github_get_json(
            f"https://api.github.com/repos/{repository}/pulls/{pr_number}/reviews?per_page=100",
            token,
            "verifier-gate",
        )
        if not isinstance(current_pr, dict) or not isinstance(reviews, list):
            raise VerifierValidationError("GitHub API returned unexpected verifier data.")
        evidence = validate_verifier_evidence(current_pr, reviews)
    except (OSError, json.JSONDecodeError, GitHubAPIError, VerifierValidationError) as exc:
        print("Verifier Gate: FAIL")
        print(f"::error::{exc}")
        return 1

    print("Verifier Gate: PASS")
    print(f"Verified independent PASS evidence from reviewer `{evidence.reviewer}`.")
    print(f"Verified head SHA: {evidence.verified_head}")
    print(f"Spec: #{evidence.spec_issue} {evidence.spec_version}")
    print(f"Risk: {evidence.risk}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
