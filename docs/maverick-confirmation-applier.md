# Maverick Confirmation Applier

The confirmation applier is the local-only step that can promote a pending live
target to confirmed after an exact gate token and payload are supplied.

Runner:
`python3 factory/maverick_confirm_target.py`

Default action id:
`phase7-live-target-confirmation`

## Required Payload

Each confirmation payload must include:

- `known_target`
- `owner_boundary`
- `access_method`
- `write_gate`
- `allowed_action`
- `evidence`

## Boundary

The applier may update `factory/active/maverick-cockpit/live-targets.json` and
append `factory/active/maverick-cockpit/confirmation-log.ndjson` when `--apply`
is present. It does not publish, upload, copy, send, schedule, post, or update
anything outside this repo.

Dry-run mode is the default. Validation uses dry-run mode so pending targets
remain pending until Edwin provides an explicit confirmation.
