# Maverick Case Ledger

The ledger is Maverick's memory. Notion is the working board, but the cockpit
needs its own record of what it observed, when it observed it, what changed, and
why a case was surfaced.

Canonical machine contract:
`factory/active/maverick-cockpit/ledger-contract.json`

## Key Decision

The canonical case key is `case.page_id`. MID is useful for merchant rollups,
but it is not safe as a primary key because it can be blank or shared by
multiple case rows.

## Memory Shape

Each normalized case carries:

- identity fields from the Launch Team row
- workflow fields used for the action queue
- timing fields used for 24-48h and QA same-day guards
- risk signals used for the cockpit radar
- memory events owned by Maverick
- source policy declaring what can be read or written

## Write Boundary

The ledger may write local state only. Notion, Gmail, Google Calendar, iCloud
Drive, and any other external mutation require a confirmation gate. Slack writes
remain blocked.

## Current Seed

Phase 3 currently includes:

- `factory/maverick_case_adapter.py`
- `factory/active/maverick-cockpit/ledger-contract.json`
- `factory/active/maverick-cockpit/samples/notion-case.json`
- `factory/active/maverick-cockpit/samples/normalized-case.json`

This is not the live adapter yet. It is the stable seed that proves how a
Launch Team row becomes a Maverick workplace case.
