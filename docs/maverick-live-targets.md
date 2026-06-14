# Maverick Live Targets

Phase 7 is the bridge from local cockpit to live workplace. It does not assume
that a shared URL, connector name, or repo idea is writable. Each target needs a
specific confirmation record before Maverick may publish, export, read private
live data, or mutate an external system.

Machine checklist:
`factory/active/maverick-cockpit/live-targets.json`

Validation:
`python3 factory/validate_maverick.py --phase live-targets`

Discovery support:
`python3 factory/validate_maverick.py --phase target-discovery`

Confirmation-applier support:
`python3 factory/validate_maverick.py --phase confirmation-applier`

Repo assembly support:
`python3 factory/validate_maverick.py --phase repo-assembly`

## Pending Targets

| Target | System | Gate |
|---|---|---|
| `github_global_repo` | GitHub | `github_publish` |
| `icloud_destination` | iCloud Drive | `icloud_artifact_export` |
| `notion_live_launch_team` | Notion | `notion_status_update` |
| `gmail_mailbox_lane` | Gmail | `gmail_send` |
| `slack_maverick_app` | Slack | `slack_write` |
| `google_calendar_lane` | Google Calendar | `google_calendar_update` |

## Confirmation Standard

A target is confirmed only when it has:

- a concrete destination or source identity
- the owner or account boundary
- the read/write permission boundary
- the matching write gate
- the exact action Maverick is allowed to perform

Until that exists, Phase 7 should fail validation by design. A failed
live-target validation is not a code defect; it is the system refusing to guess.

Current local discovery has identified a GitHub origin and an iCloud Drive
candidate path, but neither has been promoted to confirmed live target status.
The Maverick Slack app id `A0BALRB6CNQ` is recorded, but a channel or DM target,
secret-store token path, and per-message confirmation wording are still needed
before any Slack app send can be attempted.
