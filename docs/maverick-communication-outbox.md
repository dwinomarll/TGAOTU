# Maverick Communication Outbox

Dashboard panel: `Comms Outbox`

The communication outbox is Maverick's local draft lane. It prepares what the
system could say through Slack, Gmail, Calendar, or Notion, but it does not send
or mutate anything.

## Source

Generated file:

```text
factory/active/maverick-cockpit/communication-outbox.json
```

Generator:

```text
factory/maverick_comms_outbox.py
```

## Slack App Lane

The Maverick Slack app id is `A0BALRB6CNQ`. The app is recorded as a pending
communication lane, not as an enabled sender.

Before Slack messages can leave local disk, Maverick still needs:

- the Slack channel or DM target where Edwin wants Maverick to communicate
- bot token storage in a secret store
- exact per-message confirmation wording
- the `slack_write` gate and action id

The legacy Slack signal watch remains read-only.

## Draft Rules

Every outbox draft carries:

- lane
- target id
- gate id
- action id
- required `MAVERICK-CONFIRM` token
- local-only message body
- blocked or ready status

No draft may include secrets, bot tokens, direct personal contact details, or
unverified case facts.

## Validation

```bash
python3 factory/maverick_comms_outbox.py
python3 factory/validate_maverick.py --phase comms-outbox
```
