# T.G.A.O.T.U. Property Model

> Canonical shape layer for the factory. If a worker, script, Notion page, or
> build artifact needs to know "what fields exist," it starts here.

---

## Purpose

T.G.A.O.T.U. is an organization, not just a folder. The repo needs stable
properties so every substrate can mirror the same structure:

- Repo files hold the executable truth.
- Notion mirrors the archival and management truth.
- GitHub holds version history.
- Memory stores durable decisions and handoffs.

When a property is added here, it should be reflected in the relevant template,
schema, and downstream output format during the same session.

---

## Property Laws

1. **Required means required.** Blank required properties block progression.
2. **One source of truth per entity.** Templates describe human input; schemas
   validate machine shape; active build files store live state.
3. **Same names everywhere.** Do not rename a field in Notion, JSON, and Markdown
   unless the old name is explicitly superseded here.
4. **Dates are EDT unless a tool forces UTC.** If a tool emits UTC, convert before
   speaking or writing user-facing summaries.
5. **No silent inference.** Derived values must say what they were derived from.

---

## Entity Index

| Entity | Human file | Machine schema | Live location |
|---|---|---|---|
| Vision | `factory/templates/VISION.md` | `factory/schemas/vision.schema.json` | `factory/active/<app>/VISION.md` |
| Task Manifest | `factory/templates/TASK_MANIFEST.md` | `factory/schemas/task-manifest.schema.json` | `factory/active/<app>/manifests/*.json` |
| Build State | `factory/templates/BUILD_STATE.md` | `factory/schemas/build-state.schema.json` | `factory/active/<app>/BUILD_STATE.json` |
| Agent Contract | `org/onboarding/TEMPLATE.md` | `factory/schemas/agent-contract.schema.json` | `org/agents/<agent-id>.md` |
| Prompt Audit | `org/prompts/prompt-audit.ndjson` | `factory/schemas/prompt-audit.schema.json` | `org/prompts/prompt-audit.ndjson` |
| Delivery Report | `factory/templates/DELIVERY_REPORT.md` | `factory/schemas/delivery-report.schema.json` | `factory/delivered/<app>/DELIVERY_REPORT.md` |
| Department | `org/ROSTER.md` | `factory/schemas/department.schema.json` | `org/ROSTER.md` |
| Collaboration Gate | `factory/templates/TASK_MANIFEST.md` | `factory/schemas/collaboration-gate.schema.json` | `factory/active/<app>/collaboration/*.json` |
| AI Position | `org/AI_POSITIONS.md` | `factory/schemas/ai-position.schema.json` | `org/agents/<agent-id>.md` |
| Team Handoff | `org/TEAM_INTERACTIONS.md` | `factory/schemas/handoff.schema.json` | `org/logs/handoffs.log` |
| Activity Log | `org/LOGGING_SOP.md` | `factory/schemas/activity-log.schema.json` | `org/logs/activity.ndjson` |
| Quality Report | `factory/templates/QUALITY_REPORT.md` | `factory/schemas/quality-report.schema.json` | `factory/active/<app>/qa-reports/*.md` |
| User Preferences | `factory/templates/USER_PREFERENCES.md` | `factory/schemas/user-preferences.schema.json` | `org/users/<user-id>.json` |
| Notification Event | `factory/templates/NOTIFICATION_EVENT.md` | `factory/schemas/notification-event.schema.json` | `org/logs/notifications.ndjson` |

---

## Vision Properties

| Property | Required | Type | Owner | Notes |
|---|---:|---|---|---|
| `name` | yes | string | Edwin | App or system name. |
| `purpose` | yes | string | Edwin | One sentence problem statement. |
| `platform` | yes | enum/list | Edwin | One or more approved platforms. |
| `reference` | yes | string | Edwin | Existing model or `none`. |
| `must_haves` | yes | list | Edwin | Three to seven required features. |
| `must_nots` | yes | list | Edwin | Explicit exclusions. |
| `success_signal` | yes | string | Edwin | One verifiable action. |

---

## Department Properties

| Property | Required | Type | Owner | Notes |
|---|---:|---|---|---|
| `department_id` | yes | string | Eva | Stable id: `executive`, `product`, `engineering`, etc. |
| `name` | yes | string | Eva | Human-readable department name. |
| `lead_agent` | yes | string | Eva | Agent or human responsible for the department. |
| `mission` | yes | string | Eva | One sentence purpose. |
| `status` | yes | enum | Eva | `active`, `planned`, `parked`, `retired`. |
| `roles` | yes | list | Eva | Roles inside the department. |
| `inputs` | yes | list | Eva | What the department receives. |
| `outputs` | yes | list | Eva | What the department produces. |

---

## Task Manifest Properties

| Property | Required | Type | Owner | Notes |
|---|---:|---|---|---|
| `manifest_id` | yes | string | Eva | Stable id: `<app>-phase-<n>-<agent>`. |
| `app_name` | yes | string | Eva | Matches active workspace folder. |
| `phase` | yes | integer | Eva | Phase number from BLUEPRINT.md. |
| `task_type` | yes | enum | Eva | Product, Design, Architecture, Engineering, QA, DevOps, Supervisor. |
| `assigned_agent` | yes | string | Eva | Must exist in `org/ROSTER.md`. |
| `input_artifacts` | yes | list | Eva | Files the worker may read. |
| `output_artifacts` | yes | list | Eva | Files the worker must produce or update. |
| `allowed_paths` | yes | list | Eva | Write boundary for this task. |
| `validation_command` | yes | string | Architect/Eva | Runnable command. |
| `pass_condition` | yes | string | Architect/Eva | Exact success condition. |
| `priority` | yes | enum | Eva | `P0`, `P1`, or `P2`. |
| `status` | yes | enum | Worker/Eva | `queued`, `in_progress`, `blocked`, `passed`, `failed`. |
| `escalation_policy` | yes | object | Eva | Target and allowed reasons. |
| `human_role` | yes | enum | Eva | `vision_source`, `invited_collaborator`, `reviewer`, or `none`. |
| `collaboration_gate` | yes | enum | Eva | `none`, `workplace`, `canvas`, or `review`. |

---

## Collaboration Gate Properties

| Property | Required | Type | Owner | Notes |
|---|---:|---|---|---|
| `gate_id` | yes | string | Eva | Stable gate id. |
| `app_name` | yes | string | Eva | Active workspace name. |
| `surface` | yes | enum | Eva | `workplace`, `canvas`, or `review`. |
| `participants` | yes | list | Eva | Edwin plus any invited humans. |
| `authority` | yes | enum | Eva | `input`, `review`, `approval`, or `co_creation`. |
| `opens_when` | yes | string | Eva | Condition that opens the gate. |
| `closes_when` | yes | string | Eva | Condition that closes the gate. |
| `required_for_delivery` | yes | boolean | Eva | False unless Edwin explicitly requires it. |

---

## User Preference Properties

| Property | Required | Type | Owner | Notes |
|---|---:|---|---|---|
| `user_id` | yes | string | Eva/User | Stable user or collaborator id. |
| `display_name` | yes | string | Eva/User | Human-readable name. |
| `role` | yes | enum | Eva | `vision_source`, `invited_collaborator`, or `reviewer`. |
| `human_loop` | yes | boolean | User/Eva | False by default for autonomous operation. |
| `notification_loop` | yes | boolean | User/Eva | True by default. |
| `cadence` | yes | enum | User/Eva | `silent`, `minimal`, `standard`, or `verbose`. |
| `timezone` | yes | string | User/Eva | Defaults to `America/New_York`. |
| `preferred_channels` | yes | list | User/Eva | Ordered channel targets and enabled flags. |
| `event_preferences` | yes | list | User/Eva | Per-event notify setting and channel override. |
| `escalation_permissions` | yes | object | User/Eva | Which true escalation cases may ask for action. |
| `fallback_rule` | yes | string | Eva | What to do when preferred channels fail. |

---

## Notification Event Properties

| Property | Required | Type | Owner | Notes |
|---|---:|---|---|---|
| `event_id` | yes | string | COMMS-1/Eva | Stable event id. |
| `event_type` | yes | enum | COMMS-1/Eva | Notification event type from `org/NOTIFICATION_SOP.md`. |
| `subject` | yes | string | COMMS-1/Eva | App, delivery, org task, or escalation subject. |
| `created_at` | yes | datetime | COMMS-1/Eva | EDT-facing event time. |
| `created_by` | yes | string | COMMS-1/Eva | Position that emitted the event. |
| `user_action_required` | yes | boolean | EVA-COO | True only for real escalation gates. |
| `message` | yes | string | COMMS-1/Eva | User-facing notification text. |
| `delivery_attempts` | yes | list | COMMS-1/Eva | Channel, target, status, sent time, notes. |
| `final_status` | yes | enum | COMMS-1/Eva | `sent`, `failed`, or `skipped`. |
| `fallback_used` | yes | boolean | COMMS-1/Eva | True if preferred channel failed. |
| `log_reference` | yes | string | COMMS-1/Eva | Activity or notification log reference. |

---

## Build State Properties

| Property | Required | Type | Owner | Notes |
|---|---:|---|---|---|
| `app_name` | yes | string | Eva | Active workspace name. |
| `created_at` | yes | datetime | Factory | User-facing summaries convert to EDT. |
| `last_updated` | yes | datetime | Factory | Updated after every phase. |
| `overall_status` | yes | enum | Factory | `ready`, `in_progress`, `blocked`, `complete`, `delivered`. |
| `current_phase` | yes | integer | Factory | Current phase pointer. |
| `phases` | yes | list | Factory | Phase state array. |
| `escalations` | yes | list | Eva/SUP | Blockers and resolutions. |
| `delivery` | no | object | DevOps/Eva | Filled when complete. |

Each `phases[]` item must include:

| Property | Required | Type | Notes |
|---|---:|---|---|
| `number` | yes | integer | Phase number. |
| `title` | yes | string | Mirrors BLUEPRINT.md. |
| `worker` | yes | string | Assigned agent. |
| `status` | yes | enum | `pending`, `ready`, `in_progress`, `blocked`, `complete`. |
| `validated` | yes | boolean | True only after validation passes. |
| `validation_command` | yes | string | Runnable command. |
| `validation_result` | no | object | Exit code, summary, artifact path. |
| `notes` | no | string | Short operational note. |

---

## Agent Contract Properties

| Property | Required | Type | Owner | Notes |
|---|---:|---|---|---|
| `agent_id` | yes | string | Eva | Stable uppercase id. |
| `name` | yes | string | Eva | Human-readable role name. |
| `team` | yes | enum | Eva | Executive Ops, Product, Design, Architecture, Engineering, QA, DevOps, Communications, Operations, IT / Systems, Finance, Customer Success, Growth, Human Resources, Supervisor. |
| `role` | yes | string | Eva | One sentence function. |
| `reports_to` | yes | string | Eva | Usually Eva or SUP-1. |
| `input_document` | yes | string | Eva | Required input artifact. |
| `output_document` | yes | string | Eva | Required output artifact. |
| `tools` | yes | list | Eva | Must be in ALLOWLIST.md. |
| `decision_rules` | yes | list | Agent owner | Autonomous decisions. |
| `quality_gate` | yes | list | Agent owner | Must pass before done. |
| `escalation_path` | yes | list | Eva | Blocker routing. |

---

## AI Position Properties

| Property | Required | Type | Owner | Notes |
|---|---:|---|---|---|
| `position_id` | yes | string | Eva | Stable position id. |
| `department` | yes | string | Eva | Functional department. |
| `title` | yes | string | Eva | Role title. |
| `reports_to` | yes | string | Eva | Manager or supervisor. |
| `coordinates_with` | yes | list | Eva | Teams/positions this AI may coordinate with. |
| `authority_level` | yes | enum | Eva | `decide`, `recommend`, `execute`, `validate`, or `escalate`. |
| `owns` | yes | list | Eva | Responsibilities this position owns. |
| `does_not_own` | yes | list | Eva | Explicit scope exclusions. |
| `input_artifacts` | yes | list | Eva | Files/artifacts the position consumes. |
| `output_artifacts` | yes | list | Eva | Files/artifacts the position produces. |
| `done_means` | yes | string | Eva | Verifiable done condition. |
| `instructions` | yes | text | Eva | Operating instructions. |
| `escalation_conditions` | yes | list | Eva | When this AI stops and escalates. |
| `logging_duties` | yes | list | Eva | Logs this AI must write. |
| `sop_references` | yes | list | Eva | SOPs this AI must follow. |
| `status` | yes | enum | Eva | `active`, `onboarding`, `planned`, `parked`, `retired`. |

---

## Team Handoff Properties

| Property | Required | Type | Owner | Notes |
|---|---:|---|---|---|
| `handoff_id` | yes | string | Sender | Stable id for transfer. |
| `from_position` | yes | string | Sender | Sending position. |
| `to_position` | yes | string | Sender | Receiving position. |
| `app_name` | yes | string | Sender | Active build or org task. |
| `phase` | yes | number/string | Sender | Phase number, `prebuild`, or `delivery`. |
| `input_artifacts` | yes | list | Sender | Files receiver should read. |
| `output_expected` | yes | string | Sender | Required receiver output. |
| `validation` | yes | string | Sender | How completion is proven. |
| `assumptions` | yes | list | Sender | Decisions the receiver must preserve. |
| `evidence` | yes | list | Sender | Proof, source, report, or commit references. |
| `next_action` | yes | string | Sender | Exact next expected action. |
| `open_questions` | yes | list | Sender | Questions for Eva/SUP, not Edwin. |
| `status` | yes | enum | Sender/Receiver | `queued`, `accepted`, `blocked`, `complete`. |

---

## Quality Report Properties

| Property | Required | Type | Owner | Notes |
|---|---:|---|---|---|
| `report_id` | yes | string | QA-1 | Stable id for the quality report. |
| `subject` | yes | string | QA-1 | Phase, org change, or delivery being judged. |
| `app_name` | no | string | QA-1 | Active app/build name when applicable. |
| `phase` | no | number/string | QA-1 | Phase number or org/delivery marker. |
| `verdict` | yes | enum | QA-1 | `pass`, `fail`, or `blocked`. |
| `scope_gate` | yes | object | QA-1 | Expected output, actual output, and scope drift flag. |
| `artifact_gate` | yes | list | QA-1 | Required artifacts and whether each exists. |
| `validation_gate` | yes | object | QA-1 | Command/checklist, result, and evidence. |
| `defects` | yes | list | QA-1 | Defects with severity, owner, status, and summary. |
| `handoff_gate` | yes | object | OPS-1/QA-1 | Handoff completeness checks. |
| `log_gate` | yes | object | OPS-1/QA-1 | Activity, handoff, and supervisor log references. |
| `security_gate` | yes | object | IT-1/QA-1 | `clear`, `issue`, or `not_applicable`. |
| `accepted_by` | yes | string | EVA-COO/QA-1 | Position accepting the report. |
| `accepted_at` | yes | datetime | QA-1 | EDT-facing acceptance time. |
| `next_action` | yes | string | QA-1 | Exact next action required. |

---

## Notion Mirror Properties

When mirrored to Notion, use these canonical database/page properties:

| Property | Type | Maps from |
|---|---|---|
| `Name` | title | app name, blueprint name, or agent id |
| `Entity Type` | select | Vision, Task Manifest, Build State, Agent, Delivery |
| `Status` | select | current status |
| `Owner` | text/select | Edwin, Eva, or agent id |
| `Phase` | number | phase number if applicable |
| `Priority` | select | P0/P1/P2 |
| `Source Path` | url/text | repo path or GitHub URL |
| `Last Synced At` | date | EDT-facing sync time |
| `Summary` | text | short human summary |
| `Key Beats` | text | important state changes |

---

## Change Protocol

1. Update this file first.
2. Update the matching Markdown template.
3. Update the matching JSON schema.
4. Update scripts that read or write the property.
5. Update `PLAN.md` if the change alters the phase map.
6. Sync Notion, GitHub, and memory before closing the session.
