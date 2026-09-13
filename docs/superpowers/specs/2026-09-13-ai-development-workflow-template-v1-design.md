Status: READY_FOR_APPROVAL
Version: v1

# AI Development Workflow Template V1 — Design Spec

## 1. Goal

Create a reusable personal AI software-development workflow template that lets one developer use Grok Bots + Cursor Cloud Agent + GitHub as a governed delivery pipeline for both new projects and changes to existing projects.

Target operating model:

```text
User goal
→ Grok Planner / Spec Writer
→ user approves exact Spec
→ approved GitHub Spec Issue
→ PR Producer
→ @cursor
→ Cursor Cloud Agent implementation
→ Cursor branch / commit / PR
→ GitHub Contract Gate
→ Grok independent verification
→ Verifier Publisher formal Review
→ Verifier Gate
→ Merge Governor
→ merge to main
→ post-merge verification
→ completed
```

For LOW-risk work, once the exact Spec has been approved, the remainder of the flow may continue automatically through merge and post-merge verification. For HIGH/UNKNOWN-risk work, final merge still requires explicit human approval.

## 2. V1 Scope

V1 is intentionally optimized for a single personal GitHub account / single maintainer.

In scope:
- personal GitHub repositories
- public and private business repositories
- Grok Bot planning / producing / verifying
- Cursor Cloud Agent as primary implementation agent
- GitHub Issues / PRs / Actions / Rulesets as governance substrate
- separate private verifier-control repository
- automated LOW-risk merge
- explicit human merge approval for HIGH/UNKNOWN risk
- new projects
- features in existing projects
- bug fixes
- refactors
- documentation / configuration changes
- database changes with explicit risk handling
- post-merge verification of `main`

Out of scope for V1:
- organization/team workflows
- multiple maintainers / multi-approver policies
- CODEOWNERS-driven team governance
- organization-wide Rulesets
- generalized production deployment automation
- release orchestration across arbitrary environments
- V2 design work

## 3. Repository Topology

Maintain three distinct purposes:

### 3.1 Existing validation repository

`spellyaohui/ai-dev-workflow-test`

Purpose: preserve the evidence and history of the workflow validation already completed. It is not converted into the production template.

### 3.2 Public main template

`ai-dev-workflow-template`

Properties:
- public
- GitHub Template Repository enabled
- contains no secrets
- usable to create either public or private business repositories
- contains project-side governance assets, bot contracts, setup docs, and validation workflows

### 3.3 Private control template

`ai-verifier-control-template`

Properties:
- private
- used to create one private verifier-control repository per project
- no Cursor connection
- no implementation code
- holds Publisher and Merge Governor workflows
- stores separate credentials for verifier publishing and merge authority

A generated project's control repository must remain private.

## 4. Role Model and Separation of Duties

V1 uses five logical roles with strict separation.

### 4.1 Grok Planner / Spec Writer

Responsibilities:
- understand the user's goal
- inspect an existing repository when relevant
- for a new project, create a project-level plan and split work into independently deliverable phases
- for an existing project, limit scope to the requested change
- produce a versioned, implementation-ready Spec
- identify affected contracts, acceptance criteria, tests, and risk

Must not:
- implement code
- create implementation commits
- self-approve the Spec
- verify its own implementation
- merge

### 4.2 PR Producer

Responsibilities:
- accept only an explicitly APPROVED versioned Spec
- hand implementation to Cursor, normally from the approved GitHub Issue with `@cursor`
- preserve exact Spec identity in the PR contract

Must not:
- implement code itself
- act as independent verifier
- merge

### 4.3 Cursor Cloud Agent

Responsibilities:
- create its own implementation branch
- change only approved scope
- commit changes
- open/update the PR
- run relevant repository-defined tests and checks
- report observed results

Must not:
- approve its own Spec
- grant itself verifier PASS
- bypass governance checks
- merge

### 4.4 Grok Verifier + Verifier Publisher

Grok Verifier responsibilities:
- independently read the exact approved Spec
- inspect current PR diff, tests, CI, and evidence
- verify the exact current PR head SHA
- independently re-evaluate risk
- output only `PASS`, `BLOCK`, or `HOLD`

Publisher responsibilities:
- mechanically publish a formal GitHub Review based on valid verifier evidence
- bind PASS to the exact current head SHA and exact Spec identity

Must not:
- modify implementation code
- merge

### 4.5 Merge Governor

Responsibilities:
- perform final merge eligibility evaluation
- re-read current PR state rather than trusting stale conversational state
- verify current head is still the verified head
- verify required checks
- verify formal Review validity
- verify risk classification
- for LOW risk, perform automatic merge when all gates are satisfied
- for HIGH/UNKNOWN risk, wait for explicit human merge approval
- perform post-merge verification of `main`

Must not:
- disable or alter required checks to make a PR mergeable
- modify Rulesets as a workaround
- force-push `main`
- weaken tests
- infer human approval for HIGH/UNKNOWN risk

Core trust principle:

```text
planner != implementer != verifier != merger
```

## 5. Main Template Contents

The public `ai-dev-workflow-template` must contain at least:

```text
AGENTS.md
.cursor/rules/
  core-ai-guardrails.mdc
  testing.mdc
  security.mdc
  database-safety.mdc
  pr-workflow.mdc
.github/
  ISSUE_TEMPLATE/spec.yml
  PULL_REQUEST_TEMPLATE.md
  ai-governance.yml
  workflows/
    pr-contract-gate.yml
    verifier-gate.yml
    verifier-gate-refresh.yml
    governance-preflight.yml
bots/
  grok/
    planner-spec-writer.md
    pr-producer.md
    pr-verifier.md
    bug-reproducer.md
docs/
  setup/
  workflow/
  upgrade.md
VERSION
CHANGELOG.md
```

The existing validated guardrails and gate behavior from `ai-dev-workflow-test` are the baseline to preserve unless this Spec explicitly changes them.

## 6. Control Template Contents

The private `ai-verifier-control-template` must contain at least:

```text
.github/workflows/
  publish-verifier-review.yml
  merge-governor.yml
docs/setup.md
```

The generated private control repo must use two distinct credentials:

```text
VERIFIER_GITHUB_TOKEN
MERGE_GOVERNOR_TOKEN
```

Security boundary:
- `VERIFIER_GITHUB_TOKEN` may publish verification Reviews but does not need merge authority.
- `MERGE_GOVERNOR_TOKEN` owns only the permissions needed for merge-governor behavior.
- neither secret is stored in the public template or business repo.
- Cursor must not be connected to the control repo.

## 7. Versioned Grok Bot Contracts

The four files under `bots/grok/` are authoritative, version-controlled Bot role definitions.

### 7.1 `planner-spec-writer.md`
Must define:
- new-project planning
- existing-repository analysis
- task decomposition
- versioned Spec structure
- acceptance criteria requirements
- risk declaration
- stop/clarification conditions
- prohibition on implementation and merge

### 7.2 `pr-producer.md`
Must define:
- only APPROVED Spec may be implemented
- exact Spec issue/version must be preserved
- Cursor handoff behavior
- no direct implementation
- no verification
- no merge

### 7.3 `pr-verifier.md`
Must define:
- approved Spec is authoritative
- actual diff / tests / CI are evidence
- AI claims alone are not evidence
- PASS/BLOCK/HOLD
- exact head-SHA binding
- stale PASS invalidation
- independent risk re-evaluation
- no implementation or merge

### 7.4 `bug-reproducer.md`
Must define:
- reproduction-first behavior
- use the exact procedure three times before varying one variable when practical
- preserve reproduction evidence
- do not implement fixes
- no branch/PR/cloud coding as part of reproduction

Bot definitions must change through governed repository changes so workflow rules and Bot behavior cannot silently drift apart.

## 8. Spec and PR Contract

The approved GitHub Spec Issue is the sole implementation contract.

Rules:
- `READY_FOR_APPROVAL` is not approval.
- implementation begins only after explicit approval of the exact versioned Spec.
- approved Spec must be self-contained enough that Producer, Cursor, Verifier, and Merge Governor do not depend on private chat context.
- PR body must reference the exact Spec Issue and version exactly once.
- Contract Gate must reject missing, duplicated, mismatched, malformed, unapproved, or comment-hidden contract metadata.
- a new Spec version requires explicit approval of that exact version.

## 9. Risk Model

V1 uses only two merge-risk levels:

```text
LOW
HIGH
```

Any ambiguity is treated as HIGH:

```text
UNKNOWN => HIGH
```

Risk may be upgraded by independent validation but must not be silently downgraded by Cursor, Producer, or Merge Governor.

If an approved Spec is HIGH, that execution remains HIGH unless a newly versioned Spec explicitly changes the classification and is separately approved.

### 9.1 Mandatory HIGH categories

At minimum:
- destructive database changes
- dropping tables/columns
- irreversible migrations
- bulk destructive data rewrites
- authentication
- authorization / RBAC / permission boundaries
- payments
- finance / accounting / billing calculations
- secrets / credentials / certificates
- GitHub Ruleset / branch protection / required-check changes
- `.github/workflows/**` changes that affect CI, validation, deployment, publishing, or merge authority
- `.cursor/rules/**`
- `AGENTS.md`
- governance / verifier / publisher / Merge Governor logic
- production deployment or infrastructure
- Docker/Kubernetes/Terraform/cloud infrastructure changes with production impact
- large destructive deletions or plausible data-loss risk
- security policy / encryption / audit / privacy core logic
- high-privilege dependencies or material supply-chain-risk changes
- any case where verifier risk classification is uncertain
- Spec risk and actual diff risk disagree

### 9.2 Typical LOW categories

Examples when no HIGH condition is triggered:
- ordinary UI/page/style work
- ordinary business features outside auth/finance/infrastructure boundaries
- non-destructive bug fixes
- tests
- documentation
- ordinary logging/error-message improvements
- local refactors that preserve behavior
- non-sensitive configuration
- ordinary API/CRUD functionality without HIGH-risk semantics
- performance work that does not change safety/data semantics

## 10. Central Governance Configuration

The main template must provide `.github/ai-governance.yml` as the single project-side policy configuration entry point.

It must express at least:

```yaml
risk_policy:
  unknown_is_high: true

auto_merge:
  low_risk: true
  high_risk: false

post_merge_verification:
  enabled: true

high_risk_paths:
  - ".github/workflows/**"
  - ".cursor/rules/**"
  - "AGENTS.md"

high_risk_categories:
  - database-destructive
  - auth
  - rbac
  - payment
  - finance
  - secrets
  - governance
  - deployment
  - infrastructure
```

The exact schema may add fields required by implementation, but policy must not be duplicated inconsistently across multiple workflows.

## 11. Merge Policy

### 11.1 LOW risk

After the user explicitly approves the exact Spec, LOW-risk work may run automatically through implementation, verification, formal Review, merge, and post-merge verification.

Automatic merge is allowed only when Merge Governor freshly verifies all conditions, including:
- PR is open and mergeable
- current head SHA matches the head bound to valid PASS evidence
- Contract Gate passes
- Verifier Gate passes
- required CI/checks pass
- formal Review is valid and not stale/superseded/dismissed
- current risk remains LOW
- no new commit/rebase/update invalidated prior verification

### 11.2 HIGH or UNKNOWN risk

Even after all checks pass, Merge Governor must not merge until explicit human approval is given for that exact PR/current head.

PASS is verification evidence, not human merge approval.

### 11.3 Merge Governor fail-closed behavior

If any current state cannot be proven, stop rather than merge.

Merge Governor may never make a PR mergeable by weakening governance.

## 12. Task State Machine

V1 uses an explicit logical state machine:

```text
DRAFT
→ READY_FOR_APPROVAL
→ APPROVED
→ IMPLEMENTING
→ PR_OPEN
→ VERIFYING
→ PASS
→ MERGE_READY
→ MERGED
→ POST_MERGE_VERIFIED
→ COMPLETED
```

Exceptional states:

```text
BLOCKED
HOLD
FAILED
```

Semantics:
- `BLOCKED`: a known issue prevents progress.
- `HOLD`: evidence or an external dependency is insufficient for a decision.
- `FAILED`: automation/integration execution itself failed.

State must be derivable from GitHub repository evidence (Issue/PR/head/check/review/merge facts), not private conversational memory. Bot status summaries may report the derived state, but chat text is not authoritative state.

Any exceptional/unknown condition disables automatic merge.

## 13. Stale Evidence and Retry Behavior

A verifier PASS is valid only for the exact head SHA it verified.

Any new commit, rebase, or equivalent head change invalidates previous PASS evidence.

Typical recovery:

```text
failure/BLOCK
→ Cursor fixes within the same task/PR when scope still matches
→ new commit
→ head changes
→ previous PASS invalid
→ Contract / CI / verifier evaluation re-run
```

A previous successful run never authorizes a changed head.

## 14. New-Project Workflow

For a new project:

```text
user describes project
→ Planner creates project-level roadmap
→ Planner decomposes into small independently deliverable phases
→ one implementation Spec per phase
→ user approves exact phase Spec
→ Cursor implementation
→ verification / merge policy
→ main
→ next phase
```

The Planner must not ask Cursor to implement an entire non-trivial project in one giant PR when the work can be safely decomposed.

Typical phases may include:
- base architecture
- data model
- core business logic
- UI
- integrations
- testing
- release readiness

The exact decomposition follows the project rather than a rigid universal list.

## 15. Existing-Project / Feature / Bug Workflow

For an existing project:

```text
user describes desired change
→ Planner reads relevant repository architecture/tests/code
→ Planner scopes one coherent change
→ versioned Spec
→ user explicit approval
→ Cursor implementation
→ independent verification
→ risk-aware merge
→ post-merge verification
```

Supported task shapes include:
- feature
- bug fix
- refactor
- security fix
- documentation/configuration
- database change

Bug reproduction may use the separate Bug Reproducer before implementation.

## 16. Preflight

The main template must include `.github/workflows/governance-preflight.yml`.

Preflight is diagnostic only; it must not silently create credentials, weaken security, or make external authorization choices for the user.

It should report whether repository-side assets/configuration appear present, including:
- Spec template
- PR contract template
- Contract Gate
- Verifier Gate
- governance config
- required-check/Ruleset expectations where readable
- auto-merge policy configuration

It must clearly distinguish external capabilities that require real E2E proof, such as:
- Grok access to a private repo
- Cursor access to a private repo
- Publisher operation from private control repo
- Merge Governor operation from private control repo

No OAuth/PAT/secret value is printed.

## 17. Private Repository Requirement

Private business repositories are a hard V1 requirement, not a theoretical compatibility claim.

V1 must not be declared complete until a real private-repository E2E proves:

```text
Grok Planner reads private repo
→ private approved Spec
→ Producer triggers Cursor
→ Cursor creates private-repo branch/commit/PR
→ Grok Verifier reads private PR/diff
→ Publisher formal Review
→ Verifier Gate
→ LOW risk
→ Merge Governor automatically merges
→ main post-merge verification succeeds
```

If Grok private-repository access cannot be made to work reliably under supported permissions, V1 is BLOCKED and must report the limitation rather than silently fall back to public repositories.

## 18. Post-Merge Verification

`MERGED` is not equal to `COMPLETED`.

After every merge, the workflow must verify at minimum:
- PR is actually merged
- expected verified source head was merged
- merge commit (or equivalent merged history) is reachable from `main`
- expected change is present on `main`
- relevant immediate main-branch checks are not failing
- final merge SHA is recorded in completion evidence

Only then may the task become `COMPLETED`.

V1 does not attempt to standardize production deployment across arbitrary project types.

## 19. Failure Handling

The system fails closed.

Examples:
- CI failure => no Publisher PASS / no merge
- Grok `BLOCK` => Publisher REQUEST_CHANGES / verifier gate unsatisfied
- Grok `HOLD` => no merge
- API/permission failure => FAILED / no merge
- stale review => no merge
- PR conflict => no merge
- risk UNKNOWN => HIGH path
- required check missing/pending/red => no merge

No component may bypass Rulesets, remove failing checks, rewrite evidence, or downgrade safety merely to finish a task.

## 20. Template Initialization Flow

Expected one-time project setup:

```text
Use ai-dev-workflow-template
→ create public/private business repo
→ connect Cursor
→ grant Grok GitHub access to that repo
→ create/update Grok Bots from bots/grok/*.md
→ create private control repo from ai-verifier-control-template
→ configure VERIFIER_GITHUB_TOKEN
→ configure MERGE_GOVERNOR_TOKEN
→ configure main Ruleset / required checks
→ run governance preflight
→ run private-repo E2E
→ READY
```

External account authorization and secrets remain explicit setup steps; V1 must not pretend they are safely automatable when they are not.

## 21. Template Versioning and Upgrade Policy

V1 template uses semantic versioning:

```text
PATCH  = fixes that do not change governance contract semantics
MINOR  = backward-compatible capability additions
MAJOR  = incompatible governance / contract / permission-model changes
```

Template includes:
- `VERSION`
- `CHANGELOG.md`
- `docs/upgrade.md`

Business projects are not force-synchronized with template updates.

A template upgrade into an existing project is itself a governed change:

```text
new template release
→ upgrade proposal / Spec
→ diff produced by Cursor
→ independent verification
→ governance change treated as HIGH when applicable
→ explicit merge approval when required
```

## 22. Governance Changes to the Templates

Changes to these assets are HIGH risk by default:
- `AGENTS.md`
- `.cursor/rules/**`
- `.github/workflows/**`
- `.github/ai-governance.yml`
- `bots/grok/**`
- verifier Publisher logic
- Merge Governor logic
- security/permission model

The governance system must not be bypassed merely because the subject of the change is governance itself.

## 23. V1 Validation Matrix

V1 must physically pass at least these five scenarios:

### Scenario A — LOW-risk auto-merge
- ordinary LOW-risk change
- approved Spec
- Cursor implementation
- Contract Gate success
- independent Grok PASS exact head
- Publisher formal PASS exact head
- Verifier Gate success
- Merge Governor automatically merges without a second human merge approval
- post-merge verification succeeds

### Scenario B — HIGH-risk merge hold
- task classified HIGH
- all implementation/verification checks may pass
- Merge Governor does not auto-merge
- merge occurs only after explicit human approval for the exact current PR/head

### Scenario C — Verifier BLOCK
- implementation violates approved Spec or evidence requirements
- Grok returns BLOCK
- Publisher records REQUEST_CHANGES
- required verifier gate remains unsatisfied/red
- merge is prevented

### Scenario D — stale PASS
- valid PASS exists for head A
- a new commit changes PR to head B
- PASS for A becomes invalid
- merge remains blocked until B is independently re-verified and republished

### Scenario E — private-repo literal E2E
- private business repo
- Grok can read Spec/PR/diff
- Cursor can implement and open PR
- Publisher can post valid formal Review
- Merge Governor can automatically merge a LOW-risk PR
- post-merge verification confirms change on private repo `main`

All five must pass before `v1.0.0` is declared complete.

## 24. V1 Definition of Done

V1 is complete only when all of the following are true:
- public `ai-dev-workflow-template` exists and is usable as a GitHub template repository
- private `ai-verifier-control-template` exists
- existing test repository remains preserved as validation evidence
- 4 Grok Bot contracts are version-controlled
- Cursor governance rules are present
- Spec/PR contracts are present
- Contract Gate is active
- Verifier Gate + Refresh are active
- `.github/ai-governance.yml` is authoritative policy input
- Publisher exists in private control template
- Merge Governor exists in private control template
- LOW-risk auto-merge works
- HIGH/UNKNOWN requires human merge approval
- Preflight exists
- state model is explicit and derived from GitHub evidence
- fail-closed behavior is enforced
- post-merge verification works
- new-project workflow is documented and tested
- existing-project feature/bug workflow is documented and tested
- private repository support is physically proven
- all five E2E validation scenarios pass
- template carries `v1.0.0`

## 25. Non-Goals / Safety Constraints

V1 must not:
- weaken the already validated exact-head PASS model
- treat bot text alone as evidence when GitHub facts are available
- allow Cursor to self-verify or self-merge
- store verifier/merge secrets in the public template
- expose secrets in logs or docs
- silently downgrade HIGH/UNKNOWN to LOW
- automatically merge HIGH/UNKNOWN work without explicit human approval
- make chat memory authoritative workflow state
- automatically deploy arbitrary projects to production
- claim private-repository support until the literal private E2E passes

## 26. Approval Gate

This document is the exact written V1 design Spec for final review.

`Status: READY_FOR_APPROVAL` is not approval.

Implementation of the two template repositories must not begin until the user explicitly approves **this exact `v1`**.
