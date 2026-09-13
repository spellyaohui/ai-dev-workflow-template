# V1 Setup — Personal GitHub Workflow

Perform setup once per generated business project.

## 1. Create the business repository

Create a public or private repository from `ai-dev-workflow-template`. Real private projects should remain private.

## 2. Connect Cursor

Grant Cursor GitHub access to the business repository only. Do not connect Cursor to the verifier-control repository.

## 3. Grant Grok GitHub access

Grant Grok access to the business repository. For a private repository, access is not considered proven until the literal private E2E succeeds.

## 4. Create/update the Grok Bots

Use the exact version-controlled contracts under `bots/grok/`:

- Planner / Spec Writer
- PR Producer
- PR Verifier
- Bug Reproducer

## 5. Create the private control repository

Create a private repository from `ai-verifier-control-template` for this business project.

Configure these secrets in the control repository UI; never paste their values into Issues, PRs, logs, docs, or chat:

```text
VERIFIER_GITHUB_TOKEN
MERGE_GOVERNOR_TOKEN
```

The verifier credential does not need merge authority. The Merge Governor credential must be limited to the permissions required to inspect and merge eligible target PRs.

## 6. Configure the main Ruleset

Protect `main` and require these exact status contexts:

```text
Validate PR Contract
Validate Verifier Evidence
```

Do not configure bypass actors for normal operation. Protect deletion and non-fast-forward updates.

## 7. Run Governance Preflight

Run the `Governance Preflight` workflow. Local governance assets must PASS. External integration checks may remain WARN until the private E2E physically proves them.

## 8. Run the private-repository E2E

V1 is not READY until Grok can read the private repo, Cursor can create a private PR, Publisher can post formal Review evidence, and Merge Governor can automatically merge a LOW-risk PR and verify `main`.
