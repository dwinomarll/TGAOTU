# T.G.A.O.T.U. Quality SOP

> Quality is not a vibe. It is a gate.

---

## Purpose

T.G.A.O.T.U. is meant to operate without Edwin managing every step. That only
works if the organization can reject weak work by itself.

This SOP defines how quality is measured, when a task may advance, how defects
are classified, and what evidence must exist before delivery.

---

## Quality Doctrine

1. A deliverable is not accepted because an agent says it is done.
2. A deliverable is accepted only when the required gates pass with evidence.
3. Every phase must preserve upstream intent: Vision, PRD, UI-SPEC, BLUEPRINT,
   Task Manifest, and collaboration gate input.
4. A missing artifact is a failure, not a warning.
5. Ambiguous quality language is forbidden: no "looks good", "seems fine", or
   "probably works".
6. Defects are routed by severity and owner, not by panic.
7. Repeated defects become process data for OPS-1 and EFF-1.

---

## Universal Quality Gates

Every task must pass these gates before handoff:

| Gate | Required Evidence | Owner |
|---|---|---|
| Scope Gate | Output matches manifest and does not add uncommissioned scope. | Assigned worker |
| Artifact Gate | All required output artifacts exist at expected paths. | Assigned worker |
| Validation Gate | Validation command or review checklist passes. | QA-1 |
| Handoff Gate | Handoff includes evidence, assumptions, open questions, and next action. | Sender + OPS-1 |
| Log Gate | Activity and handoff logs are present for meaningful work. | Sender + OPS-1 |
| Security Gate | No secrets, unsafe access, or unverified credential handling. | IT-1 |
| Delivery Gate | Success signal is confirmed and visible to Edwin. | DEVOPS-1 + EVA-COO |

No phase may advance if any required gate fails.

---

## Defect Severity

| Severity | Meaning | Action |
|---|---|---|
| S0 Blocker | Breaks safety, secrets, data integrity, or delivery. | Stop work, escalate to EVA-COO and correct owner. |
| S1 Critical | Required artifact, validation, or core behavior is missing/broken. | Return to owner; SUP-1 joins after repeated failure. |
| S2 Major | Core workflow works but has visible defect, drift, or incomplete evidence. | Fix before handoff. |
| S3 Minor | Non-blocking polish or documentation gap. | Log and fix before final delivery when practical. |
| S4 Note | Observation or improvement idea. | Log for OPS-1/EFF-1; does not block. |

Severity is assigned by QA-1, OPS-1, IT-1, or EVA-COO depending on the defect
type. Security and credential issues default to S0 until IT-1 verifies impact.

---

## Quality Report

QA-1 writes a Quality Report for each phase or structural org change that needs
acceptance.

Location:

```text
factory/active/<app-name>/qa-reports/phase-<n>-quality.md
```

For org-structure work, use:

```text
org/reports/quality/<YYYY-MM-DD>-<topic>.md
```

The report must include:

- verdict: pass, fail, or blocked
- scope assessment
- artifact list
- validation evidence
- defects by severity
- owner for each defect
- required next action
- log references

---

## Acceptance Rules

PASS requires all of the following:

- Required artifacts exist.
- Validation command or checklist passed.
- No S0, S1, or S2 defects remain open.
- S3 defects are either fixed or explicitly accepted by EVA-COO.
- Handoff and activity logs exist.
- Security gate is clear or marked not applicable.
- The next owner can continue without asking Edwin to reconstruct context.

FAIL means the owner must repair the work before handoff.

BLOCKED means the work cannot be judged because evidence, access, or required
context is missing. BLOCKED work routes to OPS-1, IT-1, or EVA-COO depending on
cause.

---

## Department Responsibilities

| Department | Quality Duty |
|---|---|
| Executive Ops | Enforce acceptance rules and final delivery quality. |
| Product | Ensure requirements preserve Edwin's intent and remove ambiguity. |
| Design | Ensure flows, states, accessibility, and user experience are complete. |
| Architecture | Ensure phases, dependencies, validation commands, and file boundaries are sound. |
| Engineering | Produce only assigned artifacts and include implementation evidence. |
| QA | Validate outputs, classify defects, and write quality reports. |
| DevOps | Confirm runtime/deployment evidence and rollback path. |
| Operations | Watch handoff quality, queue health, missing evidence, and repeated process defects. |
| IT / Systems | Verify access, secrets safety, infrastructure readiness, and security concerns. |
| Finance | Flag budget/cost risk before paid resources are consumed. |
| HR | Track agent quality, onboarding gaps, and role performance. |
| Customer Success | Confirm delivered value remains useful after delivery. |
| Growth | Ensure outward claims match verified capabilities. |

---

## Escalation

- S0 goes to EVA-COO immediately, plus IT-1 when security or access is involved.
- Repeated S1/S2 after two repair attempts goes to SUP-1.
- Repeated process defects go to OPS-1 and EFF-1.
- Bad validation commands go to ARCH-1.
- Missing credentials or access go to IT-1.
- Budget-impacting fixes go to CFO-1 once active; until then, EVA-COO holds the gate.

---

## Required Cross-References

Every Quality Report should reference:

- Task Manifest or org task that triggered the work.
- Input artifacts reviewed.
- Output artifacts checked.
- Validation command or checklist used.
- Activity log and handoff log entries.
- Defect owners and next action.
