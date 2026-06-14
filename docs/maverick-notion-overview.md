# Maverick Notion Overview

Maverick now has a read-only Notion overview layer for the Shift4 Dine field.
It uses fetched Notion page and database evidence because the SQL row-query
surface still returns `notion-query-data-sources not found`.

## Sources

- SHIFT-4 page: portfolio snapshot and references.
- Launch Team database: schema, views, and button/canvas structure.
- Argo Shift4 Dine Environment: bot dispatch, priority engine, 14-day rule.
- Portfolio Reconciliation: 172-account burndown.
- Burndown Sheet Operations Board: bucketed account lists.
- Buddy Mainframe: Launch Team board grouped by task status.

## What Maverick Uses

- 120 active cases.
- 37 callbacks pending.
- 22 overdue follow-ups.
- 12 resolved-but-still-open tasks.
- 172 reconciled accounts: 50 good, 15 close, 103 move to active, 4 hold.
- Canvases/views: Mainframe, Follow-ups, Callback, Launch Pad, QA Breakdown,
  Map Coverage, Observation Bin, Archive Ready.
- Bot dispatch quick replies: Acknowledge, Reply Gmail, Search Similar,
  Escalate, Nudge Merchant, Create RMA, Mark Waiting, QA, Resolve, Park.

## Guardrails

The overview is local-only and read-only. It does not update Notion rows, send
Gmail, mutate Calendar, publish GitHub, or write to Slack. Direct personal
contact fields are excluded from dashboard output.

## Command

```bash
python3 factory/maverick_notion_overview.py
```

## Validation

```bash
python3 factory/validate_maverick.py --phase notion-overview
```
