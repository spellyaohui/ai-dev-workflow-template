# Risk, Verification, State, and Merge

## Risk

V1 exposes two merge-risk levels:

```text
LOW
HIGH
```

`UNKNOWN` or missing/ambiguous risk is treated as `HIGH`.

Typical LOW examples are ordinary UI changes, non-destructive bug fixes, tests, documentation, local behavior-preserving refactors, and ordinary CRUD/API work outside sensitive boundaries.

Mandatory HIGH areas include destructive database/data changes, auth/RBAC, payment/finance, secrets, governance, required-check/Ruleset changes, AI governance rules, deployment/infrastructure, security/privacy core logic, and ambiguous risk.

Risk may be escalated during verification. Approved `HIGH` may not be silently downgraded by Producer, Cursor, Verifier, or Merge Governor.

## Exact-head verification

A formal verifier PASS must contain:

```text
VERDICT: PASS
SPEC: #<issue> v<version>
VERIFIED_HEAD: <40-char current head SHA>
RISK: LOW|HIGH
```

A new commit, rebase, branch update, or force push changes the head and invalidates previous PASS evidence.

## Merge authority

`PASS` is not merge authorization.

- LOW + current valid PASS + required checks green + mergeable current PR => Merge Governor may auto-merge.
- HIGH/UNKNOWN => Merge Governor waits for explicit human approval of the exact current head.

Merge Governor must fail closed on stale evidence, conflicts, failed/pending required checks, ambiguous risk, API failures, or head movement.

## Completion

`MERGED` does not mean `COMPLETED`. The workflow must verify the expected change on `main`, record the merge SHA, and confirm immediate main checks are not failing before reporting completion.

Bot status messages are projections of GitHub evidence. Chat memory is not authoritative workflow state.
