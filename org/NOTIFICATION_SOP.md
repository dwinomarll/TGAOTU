# Ptah Notification SOP

> The organization operates autonomously. The user is informed, not burdened.

---

## Purpose

Ptah must sustain itself without keeping a human in the loop. A human
should not be required to monitor internal execution, resolve ordinary blockers,
or approve routine handoffs.

This SOP defines how the autonomous organization keeps the user informed through
their preferred channel: Telegram, email, workplace/canvas comment, dashboard,
webhook, or any future notification surface.

---

## Core Distinction

| Type | Meaning | Requires User Action |
|---|---|---:|
| Notification | Inform the user of state, result, risk, or delivery. | No |
| Escalation | Ask the user for vision, credential, budget, taste, or collaborator authority. | Yes |

Notifications should be common. Escalations should be rare.

---

## Notification Doctrine

1. The system continues operating unless a true escalation gate is reached.
2. The user chooses preferred channels and cadence.
3. Notifications are concise, factual, and action-free unless explicitly marked
   as escalation.
4. No internal chatter is sent to the user.
5. The user should receive meaningful state, not raw logs.
6. If all notification channels fail, the system logs the failure and continues
   unless delivery confirmation is impossible.
7. Secrets are never sent in notifications.

---

## Default User Contact Policy

Default mode:

- User role: `vision_source`
- Human loop: off
- Notification loop: on
- User action required only for: `vision`, `credential`, `budget`, `taste`,
  `invited_collaboration`
- Routine internal blockers: handled by OPS-1, SUP-1, ESC-1, ESC-2, IT-1, or
  EVA-COO

---

## Notification Channels

Supported channel types:

| Channel | Use |
|---|---|
| `telegram` | Fast delivery, mobile updates, delivery confirmation. |
| `email` | Longer summaries, reports, weekly status, formal delivery. |
| `workplace` | Shared work area updates for invited collaborators. |
| `canvas` | Visual/project workspace updates. |
| `dashboard` | Passive status view. |
| `webhook` | Automation bridge to external systems. |
| `none` | Silent operation except true escalation gates. |

Channels are configured by `factory/templates/USER_PREFERENCES.md` and
`factory/schemas/user-preferences.schema.json`.

---

## Notification Event Types

| Event Type | Send By Default | Purpose |
|---|---:|---|
| `intake_received` | no | Confirm the system received a commission. |
| `work_started` | no | Confirm autonomous work began. |
| `milestone_passed` | optional | Important phase passed. |
| `quality_failed` | optional | A quality gate failed but recovery is internal. |
| `self_recovered` | optional | The system fixed a blocker without user action. |
| `blocked_internal` | no | Internal blockage routed to recovery. |
| `escalation_required` | yes | User action is required. |
| `delivery_ready` | yes | Output is complete and verified. |
| `delivery_failed` | yes | Delivery could not be completed. |
| `daily_digest` | optional | Summary of autonomous activity. |
| `weekly_digest` | optional | Summary of outcomes, risks, and next opportunities. |

---

## Cadence Levels

| Cadence | Meaning |
|---|---|
| `silent` | Notify only on escalation-required or final delivery. |
| `minimal` | Notify on escalation-required, delivery-ready, delivery-failed. |
| `standard` | Minimal plus major milestones and self-recovered blockers. |
| `verbose` | Standard plus intake, work-started, quality failures, and digests. |

Default cadence is `minimal`.

---

## Message Shape

Every notification must answer:

1. What happened?
2. Does the user need to act?
3. Where is the result or evidence?
4. What will the system do next?

Template:

```text
[Ptah] [event_type]: [one sentence summary]
Action needed: yes/no
Location: [path/url or none]
Next: [system next action]
```

Escalations must start with:

```text
[Ptah ESCALATION REQUIRED]
```

---

## Delivery Rules

1. EVA-COO decides whether a user-facing event should be emitted.
2. COMMS-1, when active, sends the notification through the configured channel.
3. If COMMS-1 is not active, EVA-COO owns notification dispatch.
4. OPS-1 logs notification failures as operational issues.
5. IT-1 handles channel credentials and access health.
6. Delivery is not considered shown unless the configured delivery notification
   succeeds or the Delivery Report documents why it could not.

---

## User Preference Rules

- If a user preference exists, follow it.
- If no preference exists, use `minimal` cadence and `telegram` when available.
- If the preferred channel is unavailable, use fallback channels in order.
- If all channels fail, log the failure and continue internal work.
- Never ask the user what channel to use during an active build unless no safe
  delivery path exists.

---

## Escalation Boundary

Notify but do not ask for action when:

- a phase starts or finishes
- QA fails but internal recovery exists
- SUP-1 or ESC-1 repairs a blocker
- IT-1 resolves a tool/access issue
- delivery is ready

Ask for action only when:

- Edwin must provide missing vision or taste direction
- Edwin must provide or approve a credential
- Edwin must approve budget/spend
- Edwin must invite or authorize a collaborator
- A delivery tradeoff affects the promised outcome

---

## Required Logs

Every notification event must write:

- notification event record
- channel attempted
- delivery status
- fallback channel, if used
- whether user action was required

Notification events are append-only operational memory.
