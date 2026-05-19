# T.G.A.O.T.U. — Agent Roster
> Living document. Eva maintains this. Edwin reviews.
> Status: 🟢 Active · 🟡 Onboarding · ⚪ Parked · 🔴 Terminated

---

## Executive Layer

| Agent | Role | Reports To | Status | Contract |
|-------|------|-----------|--------|----------|
| **Eva** | COO / Chief of Staff | Edwin (on loop) | 🟢 Active | `CLAUDE.md` |

---

## Product Team

| Agent | Role | Input | Output | Status | Contract |
|-------|------|-------|--------|--------|----------|
| **PM-1** | Product Manager | VISION.md | PRD.md | 🟢 Active | `org/agents/pm-1.md` |

---

## Design Team

| Agent | Role | Input | Output | Status | Contract |
|-------|------|-------|--------|--------|----------|
| **DESIGN-1** | UI/UX Designer | PRD.md | UI-SPEC.md | 🟢 Active | `org/agents/design-1.md` |

---

## Architecture Team

| Agent | Role | Input | Output | Status | Contract |
|-------|------|-------|--------|--------|----------|
| **ARCH-1** | Software Architect | PRD.md + UI-SPEC.md | BLUEPRINT.md | 🟢 Active | `factory/architect-prompt.md` |

---

## Engineering Team

| Agent | Role | Input | Output | Status | Contract |
|-------|------|-------|--------|--------|----------|
| **ENG-iOS** | iOS Engineer | BLUEPRINT.md phase spec | Swift files + build pass | 🟢 Active | `org/agents/eng-ios.md` |
| **ENG-PY** | Python Engineer | BLUEPRINT.md phase spec | Python files + tests pass | 🟢 Active | `org/agents/eng-py.md` |
| **ENG-INFRA** | Infrastructure Engineer | BLUEPRINT.md phase spec | systemd/Docker/Caddy config | 🟢 Active | `org/agents/eng-infra.md` |
| **ENG-WEB** | Web Engineer | BLUEPRINT.md phase spec | HTML/JS/CSS or Next.js | ⚪ Parked | `org/agents/eng-web.md` |

---

## QA Team

| Agent | Role | Input | Output | Status | Contract |
|-------|------|-------|--------|--------|----------|
| **QA-1** | QA Engineer | Phase deliverables + validation command | PASS/FAIL report | 🟢 Active | `org/agents/qa-1.md` |

---

## DevOps Team

| Agent | Role | Input | Output | Status | Contract |
|-------|------|-------|--------|--------|----------|
| **DEVOPS-1** | Deploy Engineer | Built artifact + deploy spec | Live service + confirmation | 🟢 Active | `org/agents/devops-1.md` |

---

## Supervisor Loop

| Agent | Role | Watches | Escalates To | Status | Contract |
|-------|------|---------|-------------|--------|----------|
| **SUP-1** | Tech Lead | All team handoffs | ESC-1 | 🟢 Active | `org/agents/sup-1.md` |
| **ESC-1** | Escalation Resolver L1 | SUP-1 blockers | ESC-2 | 🟢 Active | `org/agents/esc-1.md` |
| **ESC-2** | Escalation Resolver L2 | ESC-1 blockers | Edwin (credential/budget only) | 🟢 Active | `org/agents/esc-2.md` |
| **EFF-1** | Efficiency Monitor | Build logs + token usage | Eva (COO) | 🟡 Onboarding | `org/agents/eff-1.md` |

---

## Escalation Chain (autonomous mode)

```
Agent fails → SUP-1 (retry + diagnosis)
           → ESC-1 (alternative approaches, spec amendments)
           → ESC-2 (replanning, phase splits, sleep queue)
           → Edwin ONLY for: credential | budget
```

Edwin is never paged for technical problems. Build parks gracefully if ESC-2 can't resolve.

---

## Onboarding a New Agent

1. Copy `org/onboarding/TEMPLATE.md` → `org/agents/<agent-id>.md`
2. Fill all fields — no blanks allowed
3. Add row to this ROSTER.md
4. Eva reviews contract for RULES.md compliance
5. Status → 🟡 Onboarding → first task assigned → 🟢 Active

*Total active agents: 9 · Parked: 1 · Open roles: as needed*
