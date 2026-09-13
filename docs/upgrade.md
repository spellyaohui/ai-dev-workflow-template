# Template Upgrade Policy

Generated projects are not force-synchronized with later template releases.

A template upgrade is a normal governed repository change:

```text
new template release
→ upgrade proposal / versioned Spec
→ explicit approval
→ Cursor produces focused diff
→ independent verification
→ risk-aware merge
```

Changes to governance assets are HIGH by default, including:

- `AGENTS.md`
- `.cursor/rules/**`
- `.github/workflows/**`
- `.github/ai-governance.yml`
- `bots/grok/**`
- Publisher / Verifier / Merge Governor logic
- permission/security model

Never weaken governance merely to make a governance upgrade easier to merge.

Versioning follows SemVer:

- PATCH: fix without governance-contract semantic change.
- MINOR: backward-compatible capability addition.
- MAJOR: incompatible contract, permission, or governance-model change.
