# T.G.A.O.T.U. Logging SOP

> If it changed state, it gets logged. If another AI must understand it later,
> it gets logged clearly.

---

## Purpose

The autonomous organization depends on continuity. Logs are how one AI can
understand what another AI did without asking Edwin to reconstruct the story.

Logs are not decoration. They are operational memory.

---

## Required Logs

| Log | Format | Purpose |
|---|---|---|
| `org/logs/activity.ndjson` | NDJSON | Every meaningful action by any AI position. |
| `org/logs/handoffs.log` | Markdown/plain text | Team-to-team transfer notes. |
| `org/logs/supervisor.log` | Markdown/plain text | Failures, retries, root causes, repair attempts. |
| `org/prompts/prompt-audit.ndjson` | NDJSON | Prompts sent between agents and their outcomes. |
| `factory/active/<app>/BUILD_STATE.json` | JSON | Machine-readable phase state. |
| `factory/active/<app>/BUILD_STATE.md` | Markdown | Human-readable phase state. |
| `factory/active/<app>/qa-reports/*.md` | Markdown | Quality and validation evidence. |
| `org/reports/quality/*.md` | Markdown | Quality reports for organization-structure changes. |
| `org/logs/notifications.ndjson` | NDJSON | User notification events and delivery attempts. |

---

## Activity Log Entry

Every position writes one NDJSON object per meaningful action:

```json
{
  "ts": "2026-05-21T09:30:00-04:00",
  "position_id": "PM-1",
  "department": "Product",
  "app_name": "example-app",
  "phase": "prebuild",
  "action": "read_artifact",
  "artifact": "factory/active/example-app/VISION.md",
  "summary": "Read vision and extracted 5 must-haves.",
  "decision": null,
  "next_position": "DESIGN-1",
  "status": "complete"
}
```

Required fields:

| Field | Required | Notes |
|---|---:|---|
| `ts` | yes | EDT timestamp. |
| `position_id` | yes | AI position id. |
| `department` | yes | Functional department. |
| `app_name` | yes | App/build/org task name. |
| `phase` | yes | Phase number, `prebuild`, `delivery`, or `org`. |
| `action` | yes | Controlled verb. |
| `artifact` | yes | File/path/url touched or read. |
| `summary` | yes | One sentence result. |
| `decision` | no | Decision made, if any. |
| `next_position` | no | Who depends on this next. |
| `status` | yes | `started`, `complete`, `blocked`, `failed`. |

Allowed `action` values:

- `start_task`
- `read_artifact`
- `write_artifact`
- `make_decision`
- `run_validation`
- `create_handoff`
- `receive_handoff`
- `log_blocker`
- `escalate`
- `complete_task`
- `write_quality_report`
- `send_notification`
- `log_notification_failure`

---

## Handoff Log Entry

Use this format in `org/logs/handoffs.log`:

```markdown
## HANDOFF - [handoff_id]

- Time: [YYYY-MM-DD HH:mm EDT]
- From: [position_id]
- To: [position_id]
- App: [app_name]
- Phase: [phase/prebuild/delivery]
- Input artifacts:
  - [path]
- Output expected:
  - [artifact or result]
- Validation:
  - [command or quality gate]
- Open questions:
  - [none or question for Eva/SUP]
- Status: queued | accepted | blocked | complete
- Notes: [short operational note]
```

---

## Supervisor Log Entry

Use `org/logs/supervisor.log` when validation fails or a handoff is blocked:

```markdown
## SUPERVISOR EVENT - [event_id]

- Time: [YYYY-MM-DD HH:mm EDT]
- Reporting position:
- Failed command or gate:
- Error summary:
- Attempt count:
- Root cause hypothesis:
- Repair action:
- Result:
- Escalated to:
- Next step:
```

---

## Logging Rules

1. Log before and after meaningful work.
2. Never mark a task complete without a completion log.
3. Never hand off without a handoff log.
4. Never retry a failed validation without a supervisor log.
5. Never erase logs. Append only.
6. Keep summaries short, factual, and useful to the next AI.
7. Do not log secrets. Refer to secret names, never values.

---

## Department Log Responsibilities

| Department | Must log |
|---|---|
| Executive Ops | intake, routing, delivery, sync |
| Product | assumptions, requirements decisions, PRD handoff |
| Design | interaction model, UI decisions, design handoff |
| Architecture | stack decisions, phase graph, blueprint handoff |
| Engineering | files changed, validation results, implementation notes |
| QA | test results, failure classification, acceptance status |
| DevOps | deployment target, runtime status, verification evidence |
| Communications | notification event, channel attempt, fallback, delivery status |
| Finance | budget estimates, cost gates, spend warnings |
| Operations | queue health, blockers, handoff quality |
| HR | agent lifecycle events |
| IT | access, infrastructure health, security events |
| Customer Success | feedback, adoption, value confirmation |
| Growth | positioning, proposals, external-facing material |
