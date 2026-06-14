# Maverick Activation Checklist

Dashboard panel: `Activation Matrix`

The activation checklist is Maverick's local readiness matrix for live targets.
It does not open any external connection. It reads the live-target ledger,
write-gate contract, and communication outbox, then shows what is missing before
each lane can become active.

## Source

Generated file:

```text
factory/active/maverick-cockpit/activation-checklist.json
```

Generator:

```text
factory/maverick_activation_checklist.py
```

## What It Tracks

- GitHub publish target and branch evidence
- Notion live row query, update method, and property map confirmation
- Gmail mailbox identity and read/draft/send boundary
- Slack Maverick app `A0BALRB6CNQ`, channel or DM target, secret-store token
  handling, and `slack_write` confirmation
- Google Calendar identity and event ownership rules
- iCloud export readiness

## Guardrail

The confirmation tokens in this file are examples. They are not proof that the
external action should run. A lane is only actionable when the concrete target,
owner boundary, access method, write gate, and action id are confirmed.

## Validation

```bash
python3 factory/maverick_activation_checklist.py
python3 factory/validate_maverick.py --phase activation-checklist
```
