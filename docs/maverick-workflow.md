# Maverick Cockpit Workflow

Maverick is the Shift4 Dine workplace cockpit for case clarity, signal intake,
memory, and disciplined execution. It starts from the dashboard, but it is not
only a dashboard. It is the operating loop that keeps the work visible,
prioritized, and guarded.

## Daily Loop

1. Open the cockpit package and review Mission Control.
2. Read Daily Command to choose the top lane before opening new work.
3. Scan Case Radar for blocked, aging, or at-risk merchant work.
4. Work Action Queue from highest risk to lowest risk.
5. Review Signal Watch for read-only Slack matches and supporting evidence.
6. Review Comms Outbox before any Slack, Gmail, Calendar, or Notion action.
7. Review Slack Bridge before any Maverick app message.
8. Review GitHub Bridge before any global repo publish action.
9. Review Notion Bridge before any Launch Team row update.
10. Review Activation Matrix before asking Maverick to publish, send, update, or schedule.
11. Check Merchant Memory before changing direction on any account.
12. Review Learning Ledger for promoted patterns and rejected unsafe memory.
13. Use Calendar Guard to protect follow-up windows and handoff timing.
14. Record learning notes only when they improve the next decision.

## Case Handling

Every case should resolve back to the Maverick ledger shape:

- `case`: merchant identity, MID, Salesforce case, DBA, and page id.
- `workflow`: current stage, owner, next action, and source lane.
- `timing`: age, due window, reminders, and stale-work flags.
- `risk`: escalation state, blockers, and customer impact.
- `memory`: history that changes the next useful move.
- `source`: Notion, Slack, Gmail, Calendar, iCloud, or local repo evidence.

Maverick should never invent case facts. If a field is missing, keep it
explicitly unknown and route the work to a confirmation step.

## Signal Rules

The legacy Slack signal watch remains read-only. Maverick can inspect and match
Slack evidence through that path, but it must not post, reply, react, edit, or
create Slack content there. The Maverick Slack app `A0BALRB6CNQ` is a separate
communication lane; sends require a confirmed destination, secret-store token
handling, and the `slack_write` gate.

Comms Outbox is local draft space. A draft can describe a Slack app message,
Gmail follow-up, Calendar block, or Notion status update, but it cannot leave
the repo until the matching live target and confirmation token exist.

Slack Bridge turns the local Slack draft into a dry-run envelope for app
`A0BALRB6CNQ`. It cannot send until a channel or DM target, secret-store token
reference, and exact `MAVERICK-CONFIRM slack_write` token are confirmed.

GitHub Bridge turns the local package into a dry-run publish envelope for the
global Maverick repository. It cannot push, create a repo, or open a pull
request until the repo/branch/publish mode and exact
`MAVERICK-CONFIRM github_publish` token are confirmed.

Notion Bridge turns the read-only overview and Notion draft into a dry-run row
update envelope for the Launch Team collection. It cannot query or mutate live
rows until the row query method, update method, property map, and exact
`MAVERICK-CONFIRM notion_status_update` token are confirmed.

Activation Matrix is the local readiness checklist. It shows each target, the
missing evidence, and example `MAVERICK-CONFIRM` token shape without opening
the gate.

Learning Ledger is local memory. It can promote evidence-backed lessons from
case pressure, follow-up pressure, callbacks, QA risk, reactivation work, the
Slack app `A0BALRB6CNQ`, and activation gates. It must reject secrets, direct
contact fields, unmatched Slack chatter, and unverified row mutations.

Gmail and Google Calendar are guarded lanes. Reading, drafting, and planning can
be modeled locally. Sending mail or changing events requires an explicit gate.

Notion is the case source of truth until a live write method is confirmed. Local
normalization and dashboard rendering are allowed; row mutation is gated.

## Export Rules

The iCloud folder is a working surface for the user, not a replacement for the
repo. Copy the current cockpit package there when the user asks for a usable
workflow bundle. Keep the export ledger in the repo so the copied files can be
verified later.

GitHub remains the durable global surface. Publish only after the repo, branch,
and action are explicitly confirmed.

## Recovery Rule

If Maverick becomes uncertain, it should fall back to the last verified local
artifact set:

1. `factory/active/maverick-cockpit/BUILD_STATE.json`
2. `factory/active/maverick-cockpit/source-map.json`
3. `factory/active/maverick-cockpit/ledger-contract.json`
4. `factory/active/maverick-cockpit/operating-loop.json`
5. `factory/active/maverick-cockpit/communication-outbox.json`
6. `factory/active/maverick-cockpit/activation-checklist.json`
7. `factory/active/maverick-cockpit/learning-ledger.json`
8. `factory/active/maverick-cockpit/slack-app-bridge.json`
9. `factory/active/maverick-cockpit/github-publish-bridge.json`
10. `factory/active/maverick-cockpit/notion-live-bridge.json`
11. `factory/active/maverick-cockpit/global-repo/assembly-manifest.json`
12. `factory/active/maverick-cockpit/exports/icloud-export-manifest.json`

The system should recover by reading evidence, not by guessing.
