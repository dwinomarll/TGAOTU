# T.G.A.O.T.U. — Foundation Plan

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

---

## Phase Map (updated — autonomous app factory focus)

| Phase | Goal | Status |
|---|---|---|
| **F1** | Blueprint III — App Factory Protocol | ✅ DONE |
| **F2** | Architect Agent — reads VISION.md, produces BLUEPRINT.md autonomously | next |
| **F3** | Build Loop Engine — phase execution + self-repair + validation | after F2 |
| **F4** | Escalation Gate — 3-case only Edwin contact protocol | after F3 |
| **F5** | First live run — Edwin drops one VISION.md, Factory ships an app | after F4 |
| **P1** | Telegram intake receptor (eva-gateway) — Factory receives commissions from phone | parallel |

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

1. **Watch every new agent input added to T.G.A.O.T.U.**
   When Edwin commissions a new Worker, Eva adds it to `blueprints/management.md` Agent Roster
   and verifies it follows INSTRUCTIONS.md protocol before it handles real tasks.

2. **Maintain three-substrate sync.**
   After every structural change: local file → Notion → GitHub → memory file.

3. **Enforce RULES.md.**
   Any Worker violating R1–R10 is halted and re-routed.

4. **Keep the build order visible.**
   This PLAN.md is updated after each phase completes.

5. **Report to Edwin in one sentence per completed phase.**
   No walls of text. One result, one confirmation, one next step.

---

## Memory Anchors (cross-session recall)

| Key | Value |
|---|---|
| Notion T.G.A.O.T.U. page | `3656ae29-a07c-81a5-9d5c-c10927e1b5f0` |
| Blueprint I (Notion) | `3646ae29-a07c-81be-96e3-f2bf2b9b3f80` |
| Memory file | `~/.claude/projects/-home-jetson/memory/project_tgaotu.md` |
| GitHub repo | `github.com/dwinomarll/TGAOTU` (private) |
| Local repo | `~/TGAOTU/` |

---

*Last updated: 2026-05-19 by Eva (foundation session)*
