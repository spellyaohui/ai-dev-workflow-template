from __future__ import annotations

from dataclasses import dataclass
import json
import os
import re
import sys

from scripts.governance.common import GitHubAPIError, github_get_json, strip_html_comments


REQUIRED_SECTIONS = (
    "Contract Source",
    "Acceptance Criteria",
    "Affected Contracts",
    "Verification",
    "Non-goals",
    "Known Risks / Limitations",
)


@dataclass(frozen=True)
class ContractResult:
    issue_number: int
    version: str
    risk: str


class ContractValidationError(ValueError):
    def __init__(self, errors: list[str] | tuple[str, ...]):
        self.errors = tuple(errors)
        super().__init__("; ".join(self.errors))


def _exact_field(pattern: str, body: str, field: str, errors: list[str]) -> str | None:
    matches = re.findall(pattern, body, flags=re.M)
    if len(matches) != 1:
        errors.append(f"Expected exactly one valid `{field}` field; found {len(matches)}.")
        return None
    return matches[0]


def _section_content(body: str, title: str) -> str | None:
    pattern = rf"(?ms)^##\s+{re.escape(title)}\s*$\n(.*?)(?=^##\s+|\Z)"
    match = re.search(pattern, body)
    if not match:
        return None
    return match.group(1).strip()


def parse_pr_contract(pr_body: str) -> ContractResult:
    body = strip_html_comments(pr_body or "")
    errors: list[str] = []

    issue = _exact_field(
        r"^Spec-Issue:\s*#([1-9][0-9]*)\s*$", body, "Spec-Issue", errors
    )
    version = _exact_field(
        r"^Spec-Version:\s*(v[1-9][0-9]*)\s*$", body, "Spec-Version", errors
    )
    risk = _exact_field(
        r"^Risk-Level:\s*(LOW|HIGH)\s*$", body, "Risk-Level", errors
    )

    for title in REQUIRED_SECTIONS:
        content = _section_content(body, title)
        if content is None:
            errors.append(f"Missing required PR section: `{title}`.")
        elif not content:
            errors.append(f"Required PR section is empty: `{title}`.")

    if errors:
        raise ContractValidationError(errors)

    assert issue is not None and version is not None and risk is not None
    return ContractResult(issue_number=int(issue), version=version, risk=risk)


def _issue_field(issue_body: str, field: str, legacy: str, form_heading: str, value: str) -> str:
    body = strip_html_comments(issue_body or "")
    legacy_matches = re.findall(legacy, body, flags=re.M | re.I)
    form_pattern = rf"(?ms)^###\s+{re.escape(form_heading)}\s*$\s*({value})\s*(?=^###|\Z)"
    form_matches = re.findall(form_pattern, body)
    matches = [*legacy_matches, *form_matches]
    if len(matches) != 1:
        raise ContractValidationError(
            [f"Spec Issue must contain exactly one valid {field}; found {len(matches)}."]
        )
    return matches[0].upper() if field in {"status", "risk"} else matches[0]


def validate_contract(pr_body: str, issue: dict) -> ContractResult:
    result = parse_pr_contract(pr_body)
    errors: list[str] = []

    if "pull_request" in issue:
        errors.append(f"Referenced #{result.issue_number} is a pull request, not a Spec Issue.")

    issue_body = issue.get("body") or ""
    if not errors:
        try:
            status = _issue_field(
                issue_body,
                "status",
                r"^Status:\s*(APPROVED)\s*$",
                "Spec Status",
                r"APPROVED",
            )
            version = _issue_field(
                issue_body,
                "version",
                r"^Version:\s*(v[1-9][0-9]*)\s*$",
                "Spec Version",
                r"v[1-9][0-9]*",
            )
            risk = _issue_field(
                issue_body,
                "risk",
                r"^Risk-Level:\s*(LOW|HIGH)\s*$",
                "Risk Level",
                r"LOW|HIGH",
            )
        except ContractValidationError as exc:
            errors.extend(exc.errors)
        else:
            if status != "APPROVED":
                errors.append(f"Spec Issue #{result.issue_number} is not APPROVED.")
            if version != result.version:
                errors.append(
                    f"Spec version mismatch: PR declares `{result.version}` but Issue #{result.issue_number} declares `{version}`."
                )
            if risk != result.risk:
                errors.append(
                    f"Spec risk mismatch: PR declares `{result.risk}` but Issue #{result.issue_number} declares `{risk}`."
                )

    if errors:
        raise ContractValidationError(errors)
    return result


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
        pr_body = (event.get("pull_request") or {}).get("body") or ""
        parsed = parse_pr_contract(pr_body)
        issue = github_get_json(
            f"https://api.github.com/repos/{repository}/issues/{parsed.issue_number}",
            token,
            "pr-contract-gate",
        )
        if not isinstance(issue, dict):
            raise ContractValidationError(["GitHub Issue response was not an object."])
        validate_contract(pr_body, issue)
    except (OSError, json.JSONDecodeError, GitHubAPIError, ContractValidationError) as exc:
        print("PR Contract Gate: FAIL")
        if isinstance(exc, ContractValidationError):
            for error in exc.errors:
                print(f"::error::{error}")
        else:
            print(f"::error::{exc}")
        return 1

    print("PR Contract Gate: PASS")
    print("Contract metadata, approved Spec identity, risk, and required sections are valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
