# Maverick Notion Live Bridge

The Notion Live Bridge is the local activation contract for the Shift4 Dine
Launch Team source. It records the preferred collection, the read-only fallback,
the dashboard read model, and the blocked update envelopes for future Notion
status updates.

Machine output:
`factory/active/maverick-cockpit/notion-live-bridge.json`

Runner:
`python3 factory/maverick_notion_bridge.py`

Validator:
`python3 factory/validate_maverick.py --phase notion-bridge`

## Source Hierarchy

Preferred source:
`collection://2106ae29-a07c-81cb-9c6e-000ba25c1f45`

Current row-query status:
`notion-query-data-sources not found`

Fallback:
`Workflow/modules/_base.py` using the local read-only cache path from the
Maverick Slack signal workflow.

## Required Before Update

- Confirm the live row query method for Launch Team rows.
- Confirm the Notion update method and allowed properties.
- Confirm property mapping for status, next action, follow-up, QA, MID, and
  Salesforce case.
- Provide `MAVERICK-CONFIRM notion_status_update notion-status-batch-plan`.

Until those are true, `update_allowed` remains false. The bridge does not query
private rows live, mutate Notion, store secrets, or invent row facts.
