# Maverick Live Target Confirmation Request

Generated: 2026-06-14T16:37:38-04:00

Maverick has prepared local artifacts and discovered candidate targets. Nothing
has been pushed, uploaded, sent, scheduled, posted, or updated externally.

## Candidate Targets

| Target | Candidate | Required gate |
|---|---|---|
| GitHub repo | `dwinomarll/maverick-cockpit` from origin `https://github.com/dwinomarll/TGAOTU.git` | `github_publish` |
| GitHub branch | `codex/maverick-cockpit` | `github_publish` |
| Publish mode | `pull_request_or_new_private_repo` | `github_publish` |
| iCloud local path | `/Users/edwinrosa/Library/Mobile Documents/com~apple~CloudDocs` | `icloud_artifact_export` |
| iCloud web destination | `https://www.icloud.com/iclouddrive/09dTCQP4Zljf2MEc0fPTBGyGA` | `icloud_artifact_export` |
| Notion collection | `collection://2106ae29-a07c-81cb-9c6e-000ba25c1f45` | `notion_status_update` |
| Gmail mailbox | pending | `gmail_send` |
| Slack Maverick app | `A0BALRB6CNQ` | `slack_write` |
| Google Calendar | pending | `google_calendar_update` |

## Confirmation Tokens

To publish Maverick to GitHub, confirm an action id and use:

`MAVERICK-CONFIRM github_publish <action_id>`

To export Maverick artifacts to iCloud, confirm an action id and use:

`MAVERICK-CONFIRM icloud_artifact_export <action_id>`

To enable Notion writes, Gmail sends, Slack app messages, or Calendar updates,
confirm each target and action separately. The legacy Slack signal watch remains
read-only.

## Still Pending

- `github_global_repo`
- `notion_live_launch_team`
- `gmail_mailbox_lane`
- `slack_maverick_app`
- `google_calendar_lane`
