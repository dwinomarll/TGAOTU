# Maverick iCloud Export

The iCloud export copies the assembled Maverick Cockpit package into the local
iCloud Drive folder supplied by the user:

`/Users/edwinrosa/Library/Mobile Documents/com~apple~CloudDocs/Desktop/MAVERICK`

The export is intentionally scoped. It writes a `Maverick-Cockpit/` package and
a top-level `MAVERICK_COCKPIT_WORKFLOW.md` handoff file beside the existing
Maverick doctrine, daily deck, templates, and `.codex` folder.

## Command

```bash
python3 factory/maverick_export_icloud.py \
  --confirm-token "MAVERICK-CONFIRM icloud_artifact_export phase7-icloud-workflow-copy"
```

## Guardrails

- Existing top-level files in the iCloud `MAVERICK` folder are preserved.
- The source package comes from
  `factory/active/maverick-cockpit/global-repo/package`.
- The export manifest is written locally to
  `factory/active/maverick-cockpit/exports/icloud-export-manifest.json`.
- The manifest records source and destination hashes for every copied package
  file.
- Slack signal watching remains read-only. Slack app messages through
  `A0BALRB6CNQ` are not part of iCloud export and require `slack_write`
  confirmation before any send.

## Validation

```bash
python3 factory/validate_maverick.py --phase icloud-export
```

This verifies the destination package, workflow handoff, existing iCloud folder
items, copied file hashes, and confirmation evidence.
