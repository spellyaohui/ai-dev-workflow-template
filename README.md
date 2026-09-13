# AI Development Workflow Template

A reusable personal development workflow for **Grok Bots + Cursor Cloud Agent + GitHub**.

The repository is the project-side half of a governed AI delivery system. It turns an explicitly approved GitHub Spec into a Cursor implementation, requires independent exact-head verification, and hands merge authority to a separate private control repository.

## Core flow

```text
User goal
→ Grok Planner / Spec Writer
→ explicit approval of exact Spec
→ approved GitHub Spec Issue
→ Grok PR Producer
→ @cursor
→ Cursor branch / commit / PR
→ Validate PR Contract
→ Grok PR Verifier
→ Verifier Publisher formal Review
→ Validate Verifier Evidence
→ Merge Governor
→ main
→ post-merge verification
```

## Merge policy

- `LOW`: after exact Spec approval, the workflow may continue automatically through merge when every current gate passes.
- `HIGH`: all gates may pass, but merge still waits for explicit human approval of the exact current PR head.
- `UNKNOWN`: treated as `HIGH`.
- A verifier `PASS` is evidence only; it is never merge authorization.

## Repository contents

- `AGENTS.md` and `.cursor/rules/`: implementation guardrails.
- `.github/ISSUE_TEMPLATE/spec.yml`: versioned implementation Spec form.
- `.github/PULL_REQUEST_TEMPLATE.md`: PR contract.
- `.github/ai-governance.yml`: central risk/auto-merge policy.
- `.github/workflows/`: Contract Gate, Verifier Gate lifecycle, and Preflight.
- `bots/grok/`: version-controlled Grok role contracts.
- `scripts/governance/`: testable governance logic.
- `tests/governance/`: negative and lifecycle tests.

## Start here

Read [`docs/setup/README.md`](docs/setup/README.md), then run the Governance Preflight and the required private-repository E2E before treating a generated project as READY.

V1 is designed for one personal GitHub maintainer. It does not standardize production deployment.
