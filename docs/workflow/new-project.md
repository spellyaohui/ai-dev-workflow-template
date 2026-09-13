# New Project Workflow

For a non-trivial new project, do not send one giant implementation request to Cursor.

```text
project goal
→ Grok Planner creates roadmap
→ roadmap is split into independently deliverable phases
→ one versioned Spec per phase
→ user explicitly approves exact phase Spec
→ PR Producer hands approved Spec to Cursor
→ Cursor implements one focused PR
→ independent verification
→ risk-aware merge
→ post-merge verification
→ next phase
```

Typical phases may include architecture, data model, core domain behavior, UI, integrations, testing, and release readiness, but the project decides the actual decomposition.

Every implementation phase must have observable acceptance criteria and a self-contained GitHub Spec. `READY_FOR_APPROVAL` is not approval.
