from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys


REQUIRED_ASSETS = (
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
)


@dataclass(frozen=True)
class CheckResult:
    status: str
    name: str
    detail: str


def check_repository(root: Path) -> list[CheckResult]:
    results: list[CheckResult] = []
    for rel in REQUIRED_ASSETS:
        path = root / rel
        if path.is_file():
            results.append(CheckResult('PASS', f'asset:{rel}', 'present'))
        else:
            results.append(
                CheckResult('FAIL', f'asset:{rel}', 'missing required governance asset')
            )

    results.extend(
        [
            CheckResult(
                'WARN',
                'grok-private-access',
                'requires literal private-repository E2E proof',
            ),
            CheckResult(
                'WARN',
                'cursor-private-access',
                'requires literal private-repository E2E proof',
            ),
            CheckResult(
                'WARN',
                'publisher-control-repo',
                'requires private control-repository E2E proof',
            ),
            CheckResult(
                'WARN',
                'merge-governor-control-repo',
                'requires private control-repository E2E proof',
            ),
            CheckResult(
                'WARN',
                'main-ruleset',
                'repository Ruleset must be inspected/configured separately',
            ),
        ]
    )
    return results


def exit_code(results: list[CheckResult]) -> int:
    return 1 if any(result.status == 'FAIL' for result in results) else 0


def main() -> int:
    root = Path.cwd()
    results = check_repository(root)
    for result in results:
        print(f'{result.status} {result.name}: {result.detail}')
    return exit_code(results)


if __name__ == '__main__':
    sys.exit(main())
