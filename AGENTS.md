# AI Development Instructions

## 1. Scope discipline

- Implement only the approved task or specification.
- Do not silently expand scope.
- If the requested change conflicts with repository behavior, architecture, contracts, or tests, stop and report the conflict.
- Do not reinterpret an approved acceptance criterion without explicit approval.

## 2. Repository safety

- Never work directly on `main` or `master`.
- Use a dedicated branch for every logical change.
- Do not modify unrelated files.
- Do not delete existing code, tests, configuration, or documentation merely to make a task easier.
- Preserve backward compatibility unless the approved specification explicitly permits a breaking change.

## 3. Verification

Before declaring work complete:

- Inspect the final diff.
- Run all repository-defined relevant tests.
- Run relevant lint, type-check, build, and validation commands when available.
- Report observed command results, not assumptions.
- Never claim a check passed if it was not actually run.

If a required verification command fails:

- Do not hide or ignore the failure.
- Diagnose the failure.
- Fix it if it is within the approved scope.
- Otherwise report the task as blocked.

## 4. Tests

- Do not remove, skip, weaken, or rewrite existing tests solely to make implementation pass.
- Add or update tests when behavior changes and the repository has an applicable test system.
- Tests must verify observable behavior rather than merely mirror implementation details.

## 5. Security

Never:

- Commit passwords, tokens, API keys, certificates, or secrets.
- Disable authentication, authorization, validation, or security controls to complete a task.
- Bypass permission checks.
- Log secrets or sensitive credentials.
- Introduce insecure defaults merely for convenience.

## 6. Data and database safety

Unless explicitly approved by the specification:

- Do not drop tables or columns.
- Do not destructively rewrite stored data.
- Do not change schema semantics.
- Do not change financial, accounting, permission, or audit rules.
- Do not remove migrations or data-integrity protections.

Database migrations must be explicit and reviewable.

## 7. Error handling

- Do not silently swallow errors.
- Do not replace real failures with fake success responses.
- Preserve useful error context.
- Handle relevant failure and retry paths where appropriate.

## 8. Dependencies

- Do not add or upgrade dependencies unless required by the approved task.
- Prefer existing repository capabilities over introducing new libraries.
- Explain any new dependency in the pull request.

## 9. Pull requests

Each implementation should:

- Use one branch per logical change.
- Keep the diff focused.
- Preserve approved acceptance criteria in the PR description.
- Include verification performed and observed results.
- State known limitations or unresolved risks.

Do not merge, deploy, release, or publish unless explicitly authorized.

## 10. Stop conditions

Stop and ask for clarification instead of guessing when:

- Acceptance criteria conflict.
- Required behavior is ambiguous.
- A breaking change appears necessary but was not approved.
- A destructive database operation appears necessary.
- Authentication, authorization, payment, financial calculation, or production infrastructure behavior would materially change outside the approved scope.
