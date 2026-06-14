# VISION - Maverick Cockpit

> Edwin fills this in once. The Factory reads it and builds. No further
> direction needed.

## Name
Maverick Cockpit

## Purpose
Create a resilient Shift4 Dine workplace dashboard that keeps Edwin oriented,
accountable, and learning across cases, communications, follow-ups, and signals.

## Platform
[ ] iOS  [ ] macOS  [x] Web  [x] API/backend  [ ] CLI  [x] Mixed: Notion, Slack, Gmail, Google Calendar, GitHub, iCloud Drive, local memory

## Reference
Shift4 Notion page `1996ae29-a07c-801b-a98e-c12c0415ba21`, Launch Team data
source `collection://2106ae29-a07c-81cb-9c6e-000ba25c1f45`, the existing
Shift4 Dine workspace under the Maverick Slack watch checkout, and the iCloud
Drive destination folder `https://www.icloud.com/iclouddrive/09dTCQP4Zljf2MEc0fPTBGyGA`.

## Must-Haves
1. Show a first-screen command center for active cases, follow-ups, callbacks,
   QA same-day risk, and escalation risk.
2. Normalize Launch Team case properties into a stable Maverick case contract.
3. Preserve per-case memory outside Notion so Maverick can learn across runs.
4. Keep Slack read-only and alert only when an active account match exists.
5. Expose a daily operating loop that routes cases through canvases, bot
   dispatch, confirmation gates, and learning capture.
6. Support Gmail email memory and draft replies after mailbox access is confirmed.
7. Use Google Calendar for appointment and follow-up awareness after source
   rules are mapped.
8. Treat GitHub as the global canonical repo and iCloud Drive as a destination
   surface for shared artifacts.
9. Require explicit confirmation before any external write, send, or status
   mutation.

## Must-Nots
1. Do not make a single folder or repo the workplace boundary.
2. Do not fabricate live row counts when Notion row-query tools are unavailable.
3. Do not write to Slack.
4. Do not send email or mutate Notion/Calendar without explicit confirmation.

## Success Signal
`python3 factory/validate_maverick.py` exits 0 and confirms the Maverick cockpit
blueprint, active build state, schema, and source map are present and consistent.
