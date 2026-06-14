# Maverick Read-Only Adapters

Phase 5 starts the bridge between the cockpit and its source surfaces. The
adapter layer is intentionally conservative: it reads local seed data, fetched
Notion overview evidence, the local operating loop, the local communication
outbox, the local activation checklist, the local learning ledger, the local
Slack app bridge, the local GitHub publish bridge, the local Notion live bridge,
and the legacy Slack watch config, then emits dashboard-ready JSON.

Machine contract:
`factory/active/maverick-cockpit/adapters/adapter-contract.json`

Runner:
`python3 factory/maverick_adapters.py`

Outputs:

- `factory/active/maverick-cockpit/adapters/adapter-snapshot.json`
- `factory/active/maverick-cockpit/dashboard/data/maverick-dashboard-data.json`
- `factory/active/maverick-cockpit/notion-overview.json`
- `factory/active/maverick-cockpit/operating-loop.json`
- `factory/active/maverick-cockpit/communication-outbox.json`
- `factory/active/maverick-cockpit/activation-checklist.json`
- `factory/active/maverick-cockpit/learning-ledger.json`
- `factory/active/maverick-cockpit/slack-app-bridge.json`
- `factory/active/maverick-cockpit/github-publish-bridge.json`
- `factory/active/maverick-cockpit/notion-live-bridge.json`

## Adapter Status

| Adapter | Status | Policy |
|---|---|---|
| Notion Launch Team sample | ready | read allowed, writes confirmation-gated |
| Notion live overview | ready | read-only fetch snapshot, writes confirmation-gated |
| Maverick operating loop | ready | local-only daily command rhythm |
| Maverick communication outbox | ready | local-only drafts, no sends |
| Maverick activation checklist | ready | local-only target readiness matrix |
| Maverick learning ledger | ready | local-only promoted lessons and rejected unsafe memory |
| Maverick Slack bridge | ready | local-only dry-run envelopes, no sends |
| Maverick GitHub bridge | ready | local-only publish envelope, no push |
| Maverick Notion bridge | ready | local-only row/update envelope, no mutation |
| Slack signal config | ready | read allowed, writes blocked |
| Gmail lane | pending | mailbox/access method required |
| Google Calendar lane | pending | source-of-truth mapping required |
| iCloud Drive destination | registered | local path/auth required before export |

## Notion Overview

Maverick can now read the Shift4 Notion page, Launch Team schema, Argo
environment, Buddy Mainframe, and reconciliation pages. The SQL row-query tool
still returns `notion-query-data-sources not found`, so the cockpit uses a
read-only overview until row-level access is stable.

The overview feeds the dashboard with:

- 120 active cases.
- 37 callbacks pending.
- 22 overdue follow-ups.
- 172 reconciled accounts.
- 8 Notion canvases/views.
- Argo/Buddy bot quick replies and priority lanes.

## Operating Loop

The operating loop turns the overview into the Daily Command panel. It keeps the
50-case target, 14-day handling window, overdue follow-ups, callbacks,
resolved-but-open tasks, reactivation candidates, canvas routing, and gated
lanes visible before any external action is taken.

## Communication Outbox

The communication outbox feeds the Comms Outbox panel. It prepares draft intents
for the Maverick Slack app `A0BALRB6CNQ`, Gmail, Calendar, and Notion. Every
draft carries its gate id, action id, required `MAVERICK-CONFIRM` token, and
blocked/ready status. The outbox never sends.

## Activation Checklist

The activation checklist feeds the Activation Matrix panel. It combines
`live-targets.json`, write gates, and outbox drafts so each lane shows missing
evidence and an example confirmation token shape before any external action is
attempted.

## Learning Ledger

The learning ledger feeds the Learning Ledger panel. It promotes evidence-backed
lessons from case pressure, callbacks, QA risk, reactivation burndown, the
two-lane Slack model for `A0BALRB6CNQ`, and activation gates. It rejects direct
contact fields, tokens, unmatched chatter, and unverified row mutations.

## Slack Bridge

The Slack bridge feeds the Slack Bridge panel. It converts local Slack drafts
into dry-run envelopes for app `A0BALRB6CNQ`, then keeps `send_allowed` false
until a channel or DM target, secret-store token reference, and exact
`slack_write` confirmation token are present.

## GitHub Bridge

The GitHub bridge feeds the GitHub Bridge panel. It records the candidate repo,
branch, package file count, and `github_publish` gate state while keeping
`publish_allowed` false until repo/branch/publish mode and confirmation token
are present.

## Notion Bridge

The Notion bridge feeds the Notion Bridge panel. It records the preferred Launch
Team collection, read-only fallback, overview counts, and
`notion_status_update` gate state while keeping `update_allowed` false until the
live row query method, update method, property map, and confirmation token are
present.

## Boundary

This phase does not mutate Notion, Slack, Gmail, Google Calendar, or iCloud
Drive. It gives the dashboard a real adapter output shape and keeps unsafe lanes
visibly pending until their access and confirmation contracts are settled.
