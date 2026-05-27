# USER PREFERENCES - [user-id]

## Identity

- **User ID:** [stable id]
- **Display Name:** [name]
- **Role:** vision_source | invited_collaborator | reviewer

## Notification Mode

- **Human loop:** off | on
- **Notification loop:** on | off
- **Cadence:** silent | minimal | standard | verbose
- **Timezone:** America/New_York

## Preferred Channels

| Priority | Channel | Address / Handle | Enabled | Notes |
|---:|---|---|---:|---|
| 1 | telegram | [handle/chat id] | yes | [notes] |
| 2 | email | [email] | yes | [notes] |

## Event Preferences

| Event Type | Notify | Channel Override |
|---|---:|---|
| intake_received | no | none |
| work_started | no | none |
| milestone_passed | optional | none |
| quality_failed | optional | none |
| self_recovered | optional | none |
| escalation_required | yes | highest_available |
| delivery_ready | yes | highest_available |
| delivery_failed | yes | highest_available |
| daily_digest | optional | email |
| weekly_digest | optional | email |

## Escalation Permissions

- **Vision:** yes
- **Credential:** yes
- **Budget:** yes
- **Taste:** yes
- **Invited collaboration:** yes

## Fallback Rule

[Example: If Telegram fails, use email. If email fails, log and continue unless
delivery confirmation is impossible.]
