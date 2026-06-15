# Ptah — Foundation Plan

> Status: Blueprint III shipped 2026-05-19. App Factory protocol defined.
> Manager: Eva (Claude Code, Jetson). Edwin drops VISION.md — Factory builds.
> Mission refined: autonomous software organization that builds apps like MAAT. No human in the loop.

---

## What Is Built (Foundation — this session)

| File | Status |
|---|---|
| `README.md` | DONE — identity, mission, three substrates |
| `blueprints/hierarchy.md` | DONE — Blueprint I: 12-tier hierarchy + 5 laws |
| `blueprints/management.md` | DONE — Blueprint II: intake form, router, delivery contract, build order |
| `INSTRUCTIONS.md` | DONE — agent operating contract |
| `RULES.md` | DONE — 10 hard rules (binding, Blueprint I-derived) |
| `ALLOWLIST.md` | DONE — approved places, tools, skills, MCPs, models |
| `PLAN.md` | DONE — this file |

---

## What Is Built This Session

| File | Status |
|---|---|
| `blueprints/blueprint-III-factory.md` | DONE — App Factory protocol: 6 stages, escalation gate, build loop |
| `factory/templates/VISION.md` | DONE — Edwin's one-time brief template |
| `org/PROPERTIES.md` | DONE - canonical entity/property map for repo, Notion, GitHub, and memory |
| `factory/templates/TASK_MANIFEST.md` | DONE - worker assignment shape |
| `factory/templates/BUILD_STATE.md` | DONE - human build-state shape |
| `factory/templates/DELIVERY_REPORT.md` | DONE - delivery close-out shape |
| `factory/schemas/*.schema.json` | DONE - machine-readable schemas for factory entities |
| `org/AI_POSITIONS.md` | DONE - professional AI department structure and role definitions |
| `org/agents/eva-coo.md` | DONE - executive operations contract |
| `org/agents/ops-1.md` | DONE - operations manager contract |
| `org/agents/it-1.md` | DONE - systems administrator contract |
| `org/QUALITY_SOP.md` | DONE - quality gates, defect severity, and acceptance rules |
| `factory/templates/QUALITY_REPORT.md` | DONE - human quality report shape |
| `factory/schemas/quality-report.schema.json` | DONE - machine-readable quality report schema |
| `org/agents/qa-1.md` | DONE - QA contract upgraded to enforce quality gates |
| `org/NOTIFICATION_SOP.md` | DONE - user notification protocol without human-in-loop dependency |
| `factory/templates/USER_PREFERENCES.md` | DONE - user channel and cadence preference shape |
| `factory/templates/NOTIFICATION_EVENT.md` | DONE - notification event shape |
| `factory/schemas/user-preferences.schema.json` | DONE - machine-readable user preference schema |
| `factory/schemas/notification-event.schema.json` | DONE - machine-readable notification event schema |
| `org/agents/comms-1.md` | DONE - user notification manager contract |
| `org/users/edwin.json` | DONE - repo-safe default notification preferences |
| `docs/maverick-cockpit.md` | DONE - prior Shift4 Dine dashboard blueprint; secondary to the folder-first rule |
| `docs/maverick-workplace-folder-rule.md` | DONE - binding rule that Maverick is the iCloud workplace folder first |
| `factory/active/maverick-cockpit/` | DONE - active factory workspace for Maverick Cockpit |
| `factory/schemas/maverick-workplace.schema.json` | DONE - machine-readable Maverick case/workplace contract |
| `factory/validate_maverick.py` | DONE - Phase 1 Maverick artifact validator |
| `factory/active/maverick-cockpit/source-map.json` | DONE - legacy Shift4 Dine migration source map |
| `docs/maverick-source-map.md` | DONE - human-readable migration role guide |
| `factory/maverick_case_adapter.py` | DONE - Launch Team row to Maverick case adapter seed |
| `factory/active/maverick-cockpit/ledger-contract.json` | DONE - local per-case memory contract |
| `docs/maverick-ledger.md` | DONE - human-readable case ledger guide |
| `factory/active/maverick-cockpit/dashboard/` | DONE - static Maverick Cockpit dashboard shell |
| `factory/maverick_adapters.py` | DONE - read-only adapter snapshot builder |
| `factory/active/maverick-cockpit/adapters/` | DONE - adapter contract and generated snapshot |
| `factory/active/maverick-cockpit/dashboard/data/` | DONE - dashboard data emitted by adapters |
| `docs/maverick-adapters.md` | DONE - human-readable adapter contract guide |
| `factory/maverick_write_gates.py` | DONE - confirmation-gate and export-manifest builder |
| `factory/active/maverick-cockpit/write-gates/` | DONE - gate contract, local export manifest, and audit log |
| `docs/maverick-write-gates.md` | DONE - human-readable write-gate policy |
| `factory/active/maverick-cockpit/live-targets.json` | DONE - Phase 7 external target confirmation checklist |
| `docs/maverick-live-targets.md` | DONE - human-readable live-target confirmation guide |
| `factory/maverick_global_repo.py` | DONE - local global-repo package manifest builder |
| `factory/active/maverick-cockpit/global-repo/` | DONE - standalone repo contract, README, and package manifest |
| `docs/maverick-global-repo.md` | DONE - human-readable global repo package guide |
| `factory/maverick_live_targets.py` | DONE - local live-target discovery without confirmation |
| `factory/active/maverick-cockpit/target-discovery.json` | DONE - discovered local GitHub/iCloud candidates |
| `factory/active/maverick-cockpit/confirmation-request.md` | DONE - exact pending confirmation request |
| `docs/maverick-target-discovery.md` | DONE - human-readable target discovery guide |
| `factory/maverick_confirm_target.py` | DONE - local-only live-target confirmation applier |
| `docs/maverick-confirmation-applier.md` | DONE - confirmation payload and safety guide |
| `factory/maverick_assemble_repo.py` | DONE - local standalone repo package assembler |
| `factory/active/maverick-cockpit/global-repo/assembly-manifest.json` | DONE - local package integrity manifest |
| `docs/maverick-repo-assembly.md` | DONE - human-readable repo assembly guide |

---

## Phase Map (updated — autonomous app factory focus)

| Phase | Goal | Status |
|---|---|---|
| **F1** | Blueprint III — App Factory Protocol | ✅ DONE |
| **F2** | Architect Agent — reads VISION.md, produces BLUEPRINT.md autonomously | in progress: BUILD_STATE shape aligned |
| **F3** | Build Loop Engine — phase execution + self-repair + validation | after F2; must emit Task Manifests |
| **F4** | Escalation Gate — 3-case only Edwin contact protocol | after F3 |
| **F5** | First live run — Edwin drops one VISION.md, Factory ships an app | after F4 |
| **P1** | Telegram intake receptor (eva-gateway) — Factory receives commissions from phone | parallel |
| **M1** | Maverick Workplace Folder — Shift4 Dine operating folder | reset: folder-first rule established; dashboard work is secondary/supporting only |

---

## Phase F2 — Architect Agent (next)

**Goal:** Eva reads `factory/active/<app-name>/VISION.md` and produces a complete `BLUEPRINT.md` — tech stack, file tree, phases, agent assignments, dependency graph — without asking Edwin anything.

**Architect decision rules (no questions for these):**
- Tech stack → pick based on platform field in VISION.md + existing project patterns
- Library selection → proven libraries already in Eva's ALLOWLIST.md
- File structure → follow patterns from eva-workspace conventions
- Phase count → 4 phases minimum, 8 maximum
- Validation tests → one per phase, must be automatable (build command / curl / test suite)

---

## Eva's Ongoing Duties as Manager

1. **Watch every new agent input added to Ptah**
   When Edwin commissions a new Worker, Eva adds it to `blueprints/management.md` Agent Roster
   and verifies it follows INSTRUCTIONS.md protocol before it handles real tasks.

2. **Maintain three-substrate sync.**
   After every structural change: local file → Notion → GitHub → memory file.

3. **Enforce RULES.md.**
   Any Worker violating R1–R10 is halted and re-routed.

4. **Keep the build order visible.**
   This PLAN.md is updated after each phase completes.

5. **Notify Edwin through preference-based channels.**
   Use COMMS-1 and `org/NOTIFICATION_SOP.md`; do not make Edwin part of the
   execution loop unless a true escalation gate is reached.

---

## Memory Anchors (cross-session recall)

| Key | Value |
|---|---|
| Notion Ptah page | `3656ae29-a07c-81a5-9d5c-c10927e1b5f0` |
| Blueprint I (Notion) | `3646ae29-a07c-81be-96e3-f2bf2b9b3f80` |
| Memory file | `~/.claude/projects/-home-jetson/memory/project_tgaotu.md` |
| GitHub repo | `github.com/dwinomarll/TGAOTU` (private) |
| Local repo | `~/TGAOTU/` |

---

*Last updated: 2026-05-19 by Eva (foundation session)*
