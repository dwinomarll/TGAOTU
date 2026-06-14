# Maverick Source Map

Phase 2 promotes the old Shift4 Dine workspace into a governed source map. The
goal is not to copy every file. The goal is to preserve proven protocols, retire
runtime drift, and rebuild the cockpit from stable contracts.

Canonical machine map:
`factory/active/maverick-cockpit/source-map.json`

## Migration Roles

| Role | Meaning |
|---|---|
| `copy_now` | Safe enough to carry directly into the cockpit contract now. |
| `copy_later` | Valuable implementation, but inspect and normalize before importing. |
| `reference` | Use as design/behavior evidence; do not copy as active code yet. |
| `rebuild` | Use as inspiration only; rebuild in the cockpit architecture. |
| `retire` | Do not migrate as canon. Usually runtime state or stale output. |
| `blocked` | Registered need, but waiting on access, path, policy, or confirmation. |

## Keep

The cockpit keeps the doctrine and the Shift4 email reference immediately. They
define the tone and memory destination. Without these, Maverick becomes a case
admin panel instead of an earned-performance system.

## Reference

The SOP, v2 requirements, gap analysis, satellite contract, Slack runbook, and
merchant outreach guide remain reference evidence. They are strong, but they
contain decisions and operational assumptions that should be distilled before
becoming executable cockpit code.

The fetched Notion overview now adds four live reference surfaces:

- Argo Shift4 Dine Environment for bot dispatch, the priority engine, and the
  14-day case handling rule.
- Buddy Mainframe for the Launch Team board grouped by Task Status.
- Portfolio Reconciliation for the 172-account burndown.
- Burndown Sheet Operations Board for close/good/reactivate/hold examples.

## Copy Later

The Notion property maps and Python satellites should be lifted only after the
new Maverick schema is stable. This protects the cockpit from inheriting broken
fields or old runtime assumptions. Priority candidates:

- `Workflow/modules/_base.py`
- `Workflow/modules/casebook.py`
- `Workflow/modules/timing.py`
- `Workflow/modules/accountability.py`
- `Workflow/modules/escalation.py`
- `config/slack_signal_watch.json`

## Rebuild

The legacy HTML interfaces are references, not the final dashboard. The
Maverick Cockpit UI should be rebuilt as a single coherent command surface:
mission control, case radar, action queue, signal watch, merchant memory, email
intelligence, calendar guard, and learning loop.

## Retire

Runtime `state/` files and caches do not become source truth. They can inform
adapter tests later, but they should not be committed as the cockpit's canon.

## Blocked Surfaces

- iCloud Drive has a confirmed local Maverick folder for package export.
- Gmail integration is blocked on mailbox and access-method confirmation.
- Google Calendar integration is blocked on source-of-truth mapping.
