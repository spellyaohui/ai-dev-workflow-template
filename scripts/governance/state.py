from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WorkflowSnapshot:
    spec_status: str
    pr_exists: bool
    pr_open: bool
    pr_merged: bool
    implementation_started: bool
    contract_ok: bool | None
    verifier_ok: bool | None
    verifier_verdict: str | None
    merge_eligible: bool
    main_verified: bool
    completion_recorded: bool
    automation_failed: bool


def derive_state(snapshot: WorkflowSnapshot) -> str:
    if snapshot.automation_failed:
        return 'FAILED'

    verdict = (snapshot.verifier_verdict or '').upper()
    if verdict == 'BLOCK':
        return 'BLOCKED'
    if verdict == 'HOLD':
        return 'HOLD'

    if snapshot.pr_merged:
        if snapshot.main_verified:
            if snapshot.completion_recorded:
                return 'COMPLETED'
            return 'POST_MERGE_VERIFIED'
        return 'MERGED'

    status = (snapshot.spec_status or '').upper()
    if status == 'DRAFT':
        return 'DRAFT'
    if status == 'READY_FOR_APPROVAL':
        return 'READY_FOR_APPROVAL'

    if snapshot.pr_exists and snapshot.pr_open:
        if snapshot.contract_ok is False:
            return 'BLOCKED'
        if verdict == 'PASS' and snapshot.verifier_ok is True:
            return 'MERGE_READY' if snapshot.merge_eligible else 'PASS'
        if snapshot.contract_ok is True:
            return 'VERIFYING'
        return 'PR_OPEN'

    if status == 'APPROVED':
        if snapshot.implementation_started:
            return 'IMPLEMENTING'
        return 'APPROVED'

    return 'FAILED'
