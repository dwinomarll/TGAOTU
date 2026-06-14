# Maverick Cockpit

> Domain blueprint for the Shift4 Dine workplace layer.

## Purpose

Maverick Cockpit is the operating dashboard for Edwin's Shift4 work. It is not
a folder tracker. It is a workplace layer that reads trusted surfaces, preserves
case memory, surfaces the next right action, and keeps accountability visible
without making Edwin operate the machinery.

The cockpit sits under Ptah's architecture rules:

- Ptah defines how autonomous work is governed.
- Maverick defines how Shift4 Dine work is understood, prioritized, and
  reinforced.
- The dashboard is the command surface where live state becomes legible.

## Source And Destination Surfaces

| Surface | Role | Current Evidence |
|---|---|---|
| Shift4 Notion page | Executive reference, dashboards, hot cases, related databases | `https://app.notion.com/p/1996ae29a07c801ba98ec12c0415ba21` |
| Launch Team data source | Core case database and workflow properties | `collection://2106ae29-a07c-81cb-9c6e-000ba25c1f45` |
| Legacy Shift4 Dine workspace | Existing modules, SOPs, Slack watch, property maps, interfaces | `/Users/edwinrosa/.codex/worktrees/slack-signal-maverick/Maverick Project/Shift4 Dine` |
| iCloud Drive destination | External shared destination folder for Maverick artifacts | `https://www.icloud.com/iclouddrive/09dTCQP4Zljf2MEc0fPTBGyGA` |
| Slack watch | Read-only signal detection for active cases | `Workflow/slack_signal_watch_runbook.md` |
| Gmail | Email memory and draft-reply lane | Connector requested; mailbox policy and access method still need confirmation |
| Google Calendar | Follow-up and appointment awareness | Connector requested; integration contract still needs a source map |
| GitHub | Global canonical repo for implementation history and reusable build surface | This repo |

Notion page/database fetch is available for the Shift4 workspace. The SQL
row-query tool still returns `notion-query-data-sources not found`, so the
cockpit uses a read-only overview layer with fetched page, database schema,
canvas/view, bot-dispatch, and reconciliation evidence.

## Cockpit Doctrine

Maverick must keep Edwin in shape by reducing cognitive drag:

1. Show what matters today.
2. Explain why it matters.
3. Preserve every case's memory.
4. Push accountability through a clear yes/no loop.
5. Stay read-only by default on external systems.
6. Require explicit confirmation before outbound writes, sends, or status
   mutations.
7. Learn from prior cases, emails, calls, Slack signals, and outcomes.

The hidden leverage is not more automation. It is case orientation: the system
must know where each account is, what changed, what is risky, and what Edwin
should do next.

## Primary Dashboard Zones

| Zone | Job | Inputs |
|---|---|---|
| Mission Control | Today summary: active cases, follow-ups, callbacks, QA same-day, overdue risk | Launch Team, Calendar |
| Case Radar | Active 0-14 day cases, observation bin, archive-ready cases, risk tags | Launch Team |
| Action Queue | Calls, emails, escalations, waiting states, yes/no accountability prompts | Launch Team, Gmail, Slack |
| Signal Watch | Read-only Slack matches against active accounts | Slack watch config, Launch Team active window |
| Merchant Memory | Per-case ledger, first seen, last seen, status deltas, decisions, prior outreach | Local Maverick state, Notion |
| Email Intelligence | Shift4 email summaries, draft replies, standing rules extracted from email | Gmail or pasted email, local reference |
| Calendar Guard | Appointments, follow-ups, timezone gaps, 24-48 hour and same-day QA deadlines | Calendar, Launch Team |
| Learning Loop | What worked, missed, repeated friction, next SOP improvement | Case ledger, QA outcomes, feedback |
| Canvas Map | Mainframe, Follow-ups, Callback, Launch Pad, QA Breakdown, Map Coverage, Observation Bin, Archive Ready | Launch Team database views |
| Bot Dispatch | Argo/Buddy quick replies, priority engine, and guarded action prompts | Argo Shift4 Dine Environment |
| Launch Gates | Repo package readiness, iCloud/GitHub candidates, and pending live-target confirmations | Local package manifests, live-target ledger |

## Data Contract

Maverick normalizes case records into these groups:

| Group | Fields |
|---|---|
| Identity | page_id, account, business_name, dba, mid, location_id, salesforce_case |
| Workflow | task_status, next_action, outcome_status, action_items, case_notes, feedback |
| Timing | created_at, case_age_days, case_phase, next_follow_up, last_contact, timezone |
| Reachability | contact_name, contact_number, contact_email, language |
| Risk | qa_score, open_loop, no_answer, callback, escalation_signals, risk_keywords |
| Memory | first_seen, last_seen, last_change, ledger_events, confidence_notes |

The canonical schema is `factory/schemas/maverick-workplace.schema.json`.

## Migration Map

| Existing Asset | Maverick Cockpit Role |
|---|---|
| `MAVERICK_V2_REQUIREMENTS.md` | Requirements seed for case memory, escalation, accountability, timing, email, Omi |
| `MAVERICK_V2_GAP_ANALYSIS.md` | Backlog and risk register |
| `Database/Notion/launch_team_property_map.json` | Property map seed |
| `Workflow/modules/_base.py` | Read-only case access pattern and fallback when Notion query is unavailable |
| `Workflow/slack_signal_watch_runbook.md` | Read-only Slack signal contract |
| `config/slack_signal_watch.json` | Slack watch configuration |
| `reference/shift4_email_reference.md` | Email memory destination |
| `Interface/*.html` | Prior UI references, not final cockpit architecture |

## Integration Rules

- The legacy Slack signal watch remains read-only. The cockpit may display and
  route signals, but it must not post, reply, react, edit, or create Slack
  content through that watch path.
- The Maverick Slack app `A0BALRB6CNQ` is a separate communication lane.
  Outbound messages through that app require a confirmed channel or DM target,
  secret-store token handling, and an exact `slack_write` confirmation.
- Notion reads are allowed. Notion writes require a separate confirmation gate.
- Gmail reads and drafts are allowed only after the mailbox and access method
  are confirmed. Sending requires explicit human confirmation per message.
- Calendar reads may inform deadline and appointment cards. Calendar writes
  require explicit confirmation.
- GitHub is the global versioned source for the cockpit implementation.
- iCloud Drive is a destination surface. Direct sync requires either a local
  mounted folder path or authenticated access to the shared folder.

## Build Phases

1. Establish the cockpit source map and schema.
2. Import the proven Shift4 Dine protocols as reference assets.
3. Build the normalized case ledger and active-case adapter.
4. Build the static cockpit UI shell with local demo data.
5. Connect read-only Notion, Slack, Gmail, and Calendar adapters.
6. Add confirmation-gated write paths.
7. Add learning memory and recurring quality reviews.

## Current Blockers

- Notion row query is unavailable in this session, but fetched Notion overview
  evidence is now wired into the dashboard.
- Gmail mailbox and access method are not confirmed.
- Calendar source-of-truth rules are not mapped.
- Write-back semantics for escalation/accountability remain confirmation-gated
  and should not be guessed.
