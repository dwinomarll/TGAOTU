# BLUEPRINT - Maverick Cockpit

## Product Intent

Maverick Cockpit turns Shift4 Dine work into an inspectable operating system.
It does not replace Notion, Slack, Gmail, Calendar, iCloud Drive, or GitHub. It
reads them, normalizes their signals, and presents Edwin with a cockpit that
knows case state, risk, timing, accountability, and learning history.

Primary Launch Team data source:
`collection://2106ae29-a07c-81cb-9c6e-000ba25c1f45`

## File Tree

```text
docs/maverick-cockpit.md
docs/maverick-adapters.md
docs/maverick-write-gates.md
docs/maverick-live-targets.md
docs/maverick-global-repo.md
docs/maverick-target-discovery.md
docs/maverick-confirmation-applier.md
docs/maverick-repo-assembly.md
docs/maverick-operating-loop.md
docs/maverick-communication-outbox.md
docs/maverick-activation-checklist.md
docs/maverick-learning-ledger.md
docs/maverick-slack-bridge.md
docs/maverick-github-bridge.md
docs/maverick-notion-bridge.md
factory/active/maverick-cockpit/VISION.md
factory/active/maverick-cockpit/BLUEPRINT.md
factory/active/maverick-cockpit/BUILD_STATE.json
factory/active/maverick-cockpit/operating-loop.json
factory/active/maverick-cockpit/communication-outbox.json
factory/active/maverick-cockpit/activation-checklist.json
factory/active/maverick-cockpit/learning-ledger.json
factory/active/maverick-cockpit/slack-app-bridge.json
factory/active/maverick-cockpit/github-publish-bridge.json
factory/active/maverick-cockpit/notion-live-bridge.json
factory/active/maverick-cockpit/live-targets.json
factory/active/maverick-cockpit/target-discovery.json
factory/active/maverick-cockpit/confirmation-request.md
factory/active/maverick-cockpit/global-repo/repo-contract.json
factory/active/maverick-cockpit/global-repo/package-manifest.json
factory/active/maverick-cockpit/global-repo/assembly-manifest.json
factory/active/maverick-cockpit/adapters/adapter-contract.json
factory/active/maverick-cockpit/adapters/adapter-snapshot.json
factory/active/maverick-cockpit/write-gates/write-gate-contract.json
factory/active/maverick-cockpit/write-gates/export-manifest.json
factory/maverick_adapters.py
factory/maverick_assemble_repo.py
factory/maverick_activation_checklist.py
factory/maverick_confirm_target.py
factory/maverick_comms_outbox.py
factory/maverick_global_repo.py
factory/maverick_github_bridge.py
factory/maverick_learning_ledger.py
factory/maverick_live_targets.py
factory/maverick_notion_bridge.py
factory/maverick_slack_bridge.py
factory/maverick_write_gates.py
factory/schemas/maverick-workplace.schema.json
factory/validate_maverick.py
```

## Architecture

```text
Notion Launch Team
Slack read-only watch
Gmail read/draft lane
Google Calendar read lane
iCloud Drive destination
GitHub global repo
Legacy Shift4 Dine workspace
        |
        v
Maverick source adapters
        |
        v
Normalized case contract
        |
        v
Case ledger + signal ledger + accountability queue
        |
        v
Maverick Cockpit dashboard
        |
        v
Confirmation gates for any external mutation
```

## Domain Modules

| Module | Purpose | Write Policy |
|---|---|---|
| `source_map` | Knows all trusted inputs and connector boundaries | Local only |
| `case_adapter` | Converts Notion properties into Maverick case records | Read-only |
| `case_ledger` | Stores first_seen, last_seen, deltas, and learning notes | Local only |
| `signal_watch` | Matches Slack/Gmail/Omi signals against active cases | Read-only by default |
| `timing_guard` | Computes 24-48h, QA same-day, timezone gaps, callbacks | Local only |
| `accountability` | Creates yes/no prompts and tracks completion | Confirmation-gated |
| `operating_loop` | Converts case pressure, canvases, bot replies, and gates into the daily command rhythm | Local only |
| `communication_outbox` | Prepares Slack app, Gmail, Calendar, and Notion drafts without sending | Local only |
| `activation_checklist` | Shows missing evidence and example confirmation tokens for live target activation | Local only |
| `learning_ledger` | Promotes evidence-backed lessons and rejects unsafe memory | Local only |
| `slack_bridge` | Builds dry-run envelopes for Maverick Slack app messages | Local only |
| `github_bridge` | Builds dry-run publish envelopes for the global Maverick repo | Local only |
| `notion_bridge` | Builds dry-run row/update envelopes for Launch Team | Local only |
| `cockpit_ui` | Shows mission control, radar, queue, memory, and learning loop | Local/dashboard |
| `artifact_export` | Publishes selected deliverables to iCloud Drive or global repo release surface | Confirmation-gated |

## Phases

### Phase 1 - Register Maverick as an active factory build
- Worker: ARCH-1
- Deliverables:
  - `docs/maverick-cockpit.md`
  - `factory/active/maverick-cockpit/VISION.md`
  - `factory/active/maverick-cockpit/BLUEPRINT.md`
  - `factory/active/maverick-cockpit/BUILD_STATE.json`
  - `factory/schemas/maverick-workplace.schema.json`
  - `factory/validate_maverick.py`
- Validation:
  - Command: `python3 factory/validate_maverick.py`
  - Pass condition: validator exits 0 and reports required artifacts present.

### Phase 2 - Promote legacy Shift4 Dine assets into source references
- Worker: OPS-1
- Deliverables:
  - source inventory for legacy SOPs, modules, interfaces, schemas, and workflows
  - migration decision list: copy, reference, retire, or rebuild
- Validation:
  - Command: `python3 factory/validate_maverick.py --phase source-map`
  - Pass condition: every required legacy source has an assigned migration role.

### Phase 3 - Build normalized case ledger
- Worker: ENG-PY
- Deliverables:
  - case identity adapter
  - local case ledger file contract
  - delta computation for first_seen, last_seen, status change, and risk change
- Validation:
  - Command: `python3 factory/validate_maverick.py --phase ledger`
  - Pass condition: sample case records validate against the Maverick schema.

### Phase 4 - Build cockpit UI shell
- Worker: DESIGN-1 + ENG-FRONTEND
- Deliverables:
  - first-screen command center
  - case radar
  - action queue
  - signal watch
  - memory and learning panels
- Validation:
  - Command: `python3 factory/validate_maverick.py --phase dashboard`
  - Pass condition: dashboard files exist, required cockpit zones are present, and core controls are wired.

### Phase 5 - Connect read-only adapters
- Worker: ENG-INTEGRATION
- Deliverables:
  - Notion read adapter
  - local operating loop adapter
  - local communication outbox adapter
  - local activation checklist adapter
  - local learning ledger adapter
  - local Slack app bridge adapter
  - local GitHub publish bridge adapter
  - local Notion live bridge adapter
  - Slack signal watch adapter
  - Gmail read/draft adapter after access confirmation
  - Google Calendar read adapter after source mapping
- Validation:
  - Command: `python3 factory/validate_maverick.py --phase adapters`
  - Pass condition: adapters run in read-only mode and redact secrets.

### Phase 6 - Add confirmation-gated external writes and exports
- Worker: ENG-INTEGRATION + QA-1
- Deliverables:
  - Notion status update gate
  - Gmail send-after-confirmation gate
  - Calendar create/update-after-confirmation gate
  - iCloud artifact export after local path/auth confirmation
  - audit log for every external mutation
- Validation:
  - Command: `python3 factory/validate_maverick.py --phase write-gates`
  - Pass condition: no external mutation can run without an explicit confirmation token.

### Phase 7 - Confirm live targets and publish/export
- Worker: ENG-INTEGRATION + DEVOPS-1
- Deliverables:
  - local global repo package manifest
  - local target discovery and confirmation request
  - local-only confirmation applier for live targets
  - generated local package preview for standalone/global repo shape
  - confirmed GitHub repo/branch target for the global Maverick surface
  - confirmed iCloud local path or authenticated upload route
  - confirmed Notion live row read/update method
  - confirmed Gmail mailbox lane and Calendar source ownership
  - release checklist proving what was published, copied, or intentionally left local
- Validation:
  - Command: `python3 factory/validate_maverick.py --phase live-targets`
  - Pass condition: every live target has an explicit confirmation record before any external mutation runs.

## Risks

- Notion row-query may be unavailable; the cockpit needs a local cache fallback.
- Email access may belong to a corporate mailbox and require a different
  connector than Gmail.
- Calendar actions need strict confirmation gates because missed or duplicated
  appointments can harm operations.
- iCloud web links are destinations, not guaranteed local writable paths.
- Migrating old files wholesale would import drift. Source roles must be
  assigned before copying implementation.

## Current Acceptance

Phase 6 is accepted when `python3 factory/validate_maverick.py --phase write-gates`
passes. The next acceptance gate is live-target confirmation for GitHub, iCloud,
Notion, Gmail, and Google Calendar.
