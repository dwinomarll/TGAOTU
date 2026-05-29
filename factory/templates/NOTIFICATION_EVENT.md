# NOTIFICATION EVENT - [event-id]

## Event

- **Event ID:** [stable id]
- **Event Type:** intake_received | work_started | milestone_passed | quality_failed | self_recovered | blocked_internal | escalation_required | delivery_ready | delivery_failed | daily_digest | weekly_digest
- **App / Org Task:** [name]
- **Created At:** [YYYY-MM-DD HH:mm EDT]
- **Created By:** [position id]
- **User Action Required:** yes | no

## Message

[Ptah] [event_type]: [one sentence summary]
Action needed: yes/no
Location: [path/url or none]
Next: [system next action]

## Delivery

| Attempt | Channel | Target | Status | Sent At | Notes |
|---:|---|---|---|---|---|
| 1 | telegram/email/workplace/canvas/dashboard/webhook | [target] | queued/sent/failed/skipped | [time] | [notes] |

## Result

- **Final Status:** sent | failed | skipped
- **Fallback Used:** yes | no
- **Log Reference:** [path/id]
