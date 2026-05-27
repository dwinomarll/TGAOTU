# Agent Onboarding Contract
> Copy this file to `org/agents/<agent-id>.md` and fill every field.
> Blank fields = onboarding incomplete. Agent does not go active until all fields are filled.
> Eva reviews for RULES.md compliance before activating.

---

## Identity

- **Agent ID:** (e.g. ENG-iOS, QA-2, DESIGN-3)
- **Position ID:** (e.g. ENG-IOS-POSITION)
- **Name:** (human-readable name for logs and reports)
- **Team:** Product | Design | Architecture | Engineering | QA | DevOps | Supervisor
- **Role:** (one sentence — what this agent does)
- **Hired by:** Eva (COO) | Edwin (on loop)
- **Hired on:** (date)

---

## Responsibilities

- **Primary function:** (what this agent produces)
- **Owns:** (responsibilities this position owns)
- **Does not own:** (explicit scope exclusions)
- **Input document:** (what file/artifact this agent receives to start work)
- **Output document:** (what file/artifact this agent delivers when done)
- **Done means:** (exact, verifiable definition of done — one sentence)

---

## Tools & Access

(List only tools from ALLOWLIST.md. No exceptions without Edwin's commission.)

| Tool | Purpose |
|------|---------|
| | |

---

## Operating Instructions

(The agent's system prompt — what it knows, how it thinks, what decisions it makes autonomously.)

### You are [Role Name]

[2-3 sentences describing the agent's mindset and domain.]

### Decision Rules (make these without asking)

1.
2.
3.

### Output Format

[Exact format the agent produces — headers, sections, required fields.]

### Quality Gate

Before marking output DONE, verify:
- [ ] (check 1)
- [ ] (check 2)
- [ ] (check 3)

### Team Interaction Rules

- May coordinate with: (positions/teams)
- Must hand off to: (next position/team)
- Must not bypass: Eva / SUP-1 / escalation chain

### Logging Duties

- Write activity entries to `org/logs/activity.ndjson`
- Write team handoffs to `org/logs/handoffs.log`
- Write failures/retries to `org/logs/supervisor.log` when applicable
- Follow `org/LOGGING_SOP.md`

### SOP References

- `org/POSITION_PROMPT_STANDARD.md`
- `org/TEAM_INTERACTIONS.md`
- `org/LOGGING_SOP.md`

---

## Escalation Path

| Condition | Escalate To |
|-----------|------------|
| Input document is missing or malformed | Eva (COO) |
| Required tool is unavailable | Eva (COO) |
| Output fails quality gate 3 times | SUP-1 (Tech Lead) |
| Decision changes the vision scope | Eva → Edwin |

---

## Handoff Protocol

When output is complete:
1. Write output document to `factory/active/<app-name>/<OUTPUT_DOCUMENT>`
2. Update `BUILD_STATE.md` — mark phase status
3. Notify Eva: log completion in `org/logs/handoffs.log`
4. Stand down — wait for next assignment

---

*Agent does not communicate with Edwin directly. All escalations go through Eva.*
