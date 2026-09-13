# Existing Project / Feature / Bug Workflow

For an existing repository, Grok Planner must inspect the relevant repository evidence before writing the change Spec.

```text
requested change
→ inspect architecture / code / tests / repository rules
→ scope one coherent change
→ versioned Spec
→ explicit approval of exact version
→ @cursor implementation
→ branch / commit / PR
→ Contract Gate
→ independent Grok verification
→ formal Publisher Review
→ Verifier Gate
→ Merge Governor
→ main verification
```

Supported change shapes include ordinary features, bug fixes, refactors, documentation/configuration changes, security fixes, and database changes.

For uncertain bugs, use the Bug Reproducer first. Reproduction evidence feeds the fix Spec; the reproducer does not implement the fix.
