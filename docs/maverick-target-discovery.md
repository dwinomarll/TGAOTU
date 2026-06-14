# Maverick Target Discovery

Target discovery records candidate external destinations without confirming or
using them. It is a Phase 7 support step between local package readiness and
live-target validation.

Runner:
`python3 factory/maverick_live_targets.py`

Outputs:

- `factory/active/maverick-cockpit/target-discovery.json`
- `factory/active/maverick-cockpit/confirmation-request.md`

## What It May Do

- read the current Git remote
- detect whether GitHub CLI is authenticated, without storing auth output
- detect local iCloud Drive candidate paths
- restate the Notion collection id already registered in Maverick
- keep Gmail and Google Calendar pending until a mailbox/calendar is confirmed
- record the Maverick Slack app id `A0BALRB6CNQ` as a pending communication
  lane

## What It May Not Do

- create a GitHub repo
- push a branch
- copy files to iCloud Drive
- query or mutate private Notion rows
- read or send Gmail
- read or update Google Calendar
- send Slack messages or configure bot tokens

Discovery improves the map. It does not open the gate.
