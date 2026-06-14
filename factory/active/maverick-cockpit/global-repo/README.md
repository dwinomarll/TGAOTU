# Maverick Cockpit

Maverick Cockpit is the Shift4 Dine workplace surface for case focus, signal
watching, merchant memory, and confirmation-gated action. It is built to read
from trusted sources, normalize work into one cockpit, and refuse unsafe
external writes unless the exact gate is confirmed.

## What This Package Contains

- `docs/maverick-cockpit.md` - workplace blueprint
- `docs/maverick-source-map.md` - Shift4 Dine migration map
- `docs/maverick-ledger.md` - normalized case ledger contract
- `docs/maverick-adapters.md` - read-only adapter contract
- `docs/maverick-write-gates.md` - external mutation safety rules
- `docs/maverick-live-targets.md` - GitHub, iCloud, Notion, Gmail, and Calendar confirmation checklist
- `factory/active/maverick-cockpit/dashboard/` - static cockpit dashboard
- `factory/maverick_*.py` - local adapter, gate, and package builders
- `factory/validate_maverick.py` - validation entrypoint

## Current Safety Boundary

Maverick can prepare local manifests and dashboard data. It does not push to
GitHub, upload to iCloud, send Gmail, create Calendar events, update Notion, or
write to Slack by default.

External publish requires the `github_publish` write gate:

`MAVERICK-CONFIRM github_publish <action_id>`

iCloud export requires the `icloud_artifact_export` write gate:

`MAVERICK-CONFIRM icloud_artifact_export <action_id>`

Slack signal watching remains read-only. Slack app messages through
`A0BALRB6CNQ` require the `slack_write` gate plus a confirmed channel or DM
target and secret-store token handling.

## Local Validation

```bash
python3 factory/maverick_adapters.py
python3 factory/maverick_write_gates.py
python3 factory/maverick_global_repo.py
python3 factory/validate_maverick.py --phase global-repo
```

The live target validation is expected to fail until the external targets are
confirmed:

```bash
python3 factory/validate_maverick.py --phase live-targets
```
