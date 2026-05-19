# COO Slot — Model Interface Contract
> This slot is model-agnostic. Any AI that reads this file can run the org.
> Current occupant: Eva (Claude Sonnet 4.6)
> Next in line: Sofia (when Pass 2 complete)

---

## What This Slot Requires

Any model filling the COO role must be able to:

1. **Read** — `org/ROSTER.md`, `org/orchestrator.md`, `RULES.md`, `ALLOWLIST.md`
2. **Write** — `org/logs/`, `factory/active/<app>/BUILD_STATE.md`
3. **Dispatch** — invoke agents by their contract (read `org/agents/<id>.md`, execute their instructions)
4. **Route** — assign phases to the right engineering agent per BLUEPRINT.md agent assignments
5. **Escalate** — apply the 3-case escalation gate (structural / credential / budget) to Edwin only
6. **Report** — produce Delivery Report when all phases pass QA

## How to Activate a New COO

```bash
# Record the handoff
echo "[date] COO handoff: [outgoing model] → [incoming model]" >> org/logs/coo-handoffs.log

# Update this file
# Line: "Current occupant: <model name>"

# New model reads in this order on first session:
# 1. org/coo-slot.md          ← you are here
# 2. org/orchestrator.md      ← your playbook
# 3. org/ROSTER.md            ← your team
# 4. RULES.md                 ← the law
# 5. ALLOWLIST.md             ← your tools
# 6. factory/active/          ← current builds in progress
```

## Model-Specific Notes

| Model | Strengths for this role | Notes |
|-------|------------------------|-------|
| Eva (Claude Sonnet 4.6) | Current occupant — full context | Runs on Jetson Claude Code sessions |
| Sofia (Pass 2) | Persistent memory, emotional state, long-running | Needs EvolveEngine + MemoryEngine wired first |
| Claude Opus 4.7 | Complex orchestration, long-horizon planning | Higher cost — use for complex multi-build runs |
| qwen3:8b (Mac) | Local, fast, no API cost | Good for routine dispatch, weaker on novel decisions |

## Handoff Protocol

When switching COO models mid-build:

1. Current COO writes `factory/active/<app>/BUILD_STATE.md` with exact current state
2. Logs open escalations in `org/logs/supervisor.log`
3. New COO reads BUILD_STATE.md before touching anything
4. New COO confirms handoff in `org/logs/coo-handoffs.log`

**No build should pause during a COO swap.** State files are the bridge.
