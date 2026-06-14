# Maverick Learning Ledger

The Learning Ledger is Maverick's local memory promotion layer. It captures
evidence-backed patterns that change routing, priority, safety, or the next
action. It does not store secrets, direct contact fields, private tokens, or
unmatched chatter.

Machine output:
`factory/active/maverick-cockpit/learning-ledger.json`

Runner:
`python3 factory/maverick_learning_ledger.py`

Validator:
`python3 factory/validate_maverick.py --phase learning-ledger`

## What Gets Promoted

Maverick should promote only lessons that improve a future route, priority,
safety decision, or next action.

- Case pressure against the 50-case target.
- Overdue follow-up pressure against the 14-day handling rule.
- Callback batching signals.
- Resolved-but-open QA risk.
- Portfolio reactivation burndown work.
- The two-lane Slack model: legacy watch read-only, Maverick app
  `A0BALRB6CNQ` gated through `slack_write`.
- Activation gate pressure before any publish, send, schedule, or update.

## What Gets Rejected

- Direct contact fields such as contact phone or email unless verified in the
  source system.
- Bot or OAuth tokens.
- Unmatched Slack chatter.
- Unverified Notion row mutations.

## Dashboard Role

The Learning Ledger feeds the cockpit's Learning Ledger panel. It gives Maverick
a visible memory of what the current artifact set has learned, while keeping the
Learning Loop focused on performance metrics.

This is local memory. It may guide the next decision, but it cannot mutate
Notion, Slack, Gmail, Google Calendar, GitHub, or iCloud Drive.
