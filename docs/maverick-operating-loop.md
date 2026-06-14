# Maverick Operating Loop

Maverick needs a daily command rhythm, not only a dashboard. The operating loop
is the local contract that turns the Shift4 Notion overview, Launch Team
canvases, Argo/Buddy bot dispatch, and confirmation gates into a repeatable
work pattern.

## Source

Generated file:

```text
factory/active/maverick-cockpit/operating-loop.json
```

Generator:

```text
factory/maverick_operating_loop.py
```

The loop uses the read-only Notion overview. It does not query rows through the
unavailable `notion-query-data-sources` surface, and it does not mutate Notion,
Slack, Gmail, Google Calendar, GitHub, or iCloud.

## Daily Command

The dashboard panel named `Daily Command` exposes:

- active case pressure against the 50-case target
- the 14-day handling window
- the top objectives for overdue follow-ups, callbacks, resolved-but-open work,
  and reactivation candidates
- cadence count and gated lane count

This makes the work visible before any action is taken.

## Operating Rules

1. Read the field from Mission Control before opening new work.
2. Route work through explicit canvases such as Mainframe, Follow-ups, Callback,
   Launch Pad, QA Breakdown, Map Coverage, Observation Bin, and Archive Ready.
3. Use Bot Dispatch for classification, drafting, search, and local planning
   only. External effects remain gated.
4. Capture learning only when it changes routing, priority, or the next useful
   action.

## Guardrails

The legacy Slack signal watch remains read-only. Slack app messages through
`A0BALRB6CNQ`, Gmail sends, Calendar mutations, Notion updates, GitHub publish
actions, and iCloud exports require their matching confirmation gate. Secrets
and bot tokens must stay out of Notion, transcripts, dashboard JSON, and local
docs.

## Validation

```bash
python3 factory/maverick_operating_loop.py
python3 factory/validate_maverick.py --phase operating-loop
```
