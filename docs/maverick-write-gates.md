# Maverick Write Gates

Phase 6 gives Maverick a hard boundary for external actions. The cockpit may
prepare local artifacts, draft intent, and write local audit evidence. It may
not mutate Notion, Gmail, Google Calendar, iCloud Drive, GitHub, or Slack unless
the matching gate is explicitly confirmed.

Machine contract:
`factory/active/maverick-cockpit/write-gates/write-gate-contract.json`

Runner:
`python3 factory/maverick_write_gates.py`

Outputs:

- `factory/active/maverick-cockpit/write-gates/export-manifest.json`
- `factory/active/maverick-cockpit/write-gates/audit-log.ndjson`

## Gate Rule

Every external mutation must carry an exact token:

`MAVERICK-CONFIRM <gate_id> <action_id>`

The token is scoped to one gate and one action id. A token for Gmail cannot
authorize Calendar. A token for one email cannot authorize another. Slack app
messages use `slack_write` and remain disabled until the Maverick app target,
secret storage, and per-message confirmation wording are settled.

## Gate Status

| Gate | System | Status |
|---|---|---|
| `notion_status_update` | Notion | confirmation required, disabled until live update method is mapped |
| `gmail_send` | Gmail | confirmation required, disabled until mailbox access is confirmed |
| `google_calendar_update` | Google Calendar | confirmation required, disabled until source ownership is mapped |
| `icloud_artifact_export` | iCloud Drive | confirmation required, disabled until local path/auth is confirmed |
| `github_publish` | GitHub | confirmation required, disabled until repo/branch target is confirmed |
| `slack_write` | Slack | confirmation required, disabled until app target and secret handling are confirmed |

## Export Boundary

The export manifest hashes the local Maverick cockpit artifacts that would be
published to GitHub or copied to iCloud after confirmation. The manifest itself
is local proof only. It does not push, upload, copy, send, post, schedule, or
update anything outside the repo.
