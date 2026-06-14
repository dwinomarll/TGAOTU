# Maverick Slack App Bridge

The Slack App Bridge is the local activation contract for Maverick app
`A0BALRB6CNQ`. It turns Comms Outbox Slack drafts into safe message envelopes
without sending them.

Machine output:
`factory/active/maverick-cockpit/slack-app-bridge.json`

Runner:
`python3 factory/maverick_slack_bridge.py`

Validator:
`python3 factory/validate_maverick.py --phase slack-bridge`

## Boundary

The legacy Slack signal watch remains read-only. It may inspect and match
messages, but it must not post, reply, react, edit, or create Slack content.

The Maverick Slack app is a separate outbound lane. It remains blocked until all
of these are true:

- A Slack channel id or DM id is confirmed as Edwin's Maverick communication
  target.
- The bot token is stored only in a secret store outside repo artifacts.
- The exact message action id is confirmed with `MAVERICK-CONFIRM slack_write`.
- The message body is reviewed as a local draft before send.

## Current State

The bridge can prepare dry-run envelopes for the daily command brief, but
`send_allowed` is false. No Slack API call is made, no token is recorded, and no
channel is guessed.
