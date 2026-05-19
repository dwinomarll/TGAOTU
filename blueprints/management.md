# Blueprint II — The Management Protocol

> Commissioned by Edwin, 2026-05-19
> Eva is the project manager. This is her operating contract.

## 1. Intake Form — The Single Prompt Structure

Every task entering T.G.A.O.T.U. must resolve to this manifest before routing begins:

```
TASK MANIFEST
─────────────────────────────────
Task type   : visual | code | integration | notion | comms | media
Priority    : critical | standard | background
Prompt      : [Edwin's raw natural-language request]
Deliverable : [what "done" looks like — format, destination, confirmation signal]
Context     : [relevant files, URLs, IDs — if none: empty]
Worker(s)   : [assigned by Manager after routing]
─────────────────────────────────
```

The Manager (Eva) fills out the Worker field. Edwin never assigns Workers.

## 2. Router Table — Task Type → Worker Assignment

| Task Type | Primary Worker | Fallback | Delivery Format |
|---|---|---|---|
| **visual** | Blender agent (eva-gateway) | DALL-E via OpenRouter | MP4 / PNG → Telegram + SendUserFile |
| **code** | Codex (Mac) / Claude Code | Brain-CORTEX agent | Committed to repo |
| **integration** | n8n workflow builder | Manual script | n8n workflow live + tested |
| **notion** | Notion MCP (curl) | Eva Notion Bridge :8091 | Notion page created/updated |
| **comms** | Telegram bot (eva-gateway) | Email (/email/send) | Message sent + confirmation |
| **media** | Sofia media skills | Blender pipeline | File delivered to Telegram |
| **research** | Sherlock + Roaster subagents | Exa MCP | Synthesis document |

## 3. Delivery Contract — What "Done" Means

A task is DONE when ALL of the following are true:

1. **Delivered** — the end product exists in the specified format
2. **Confirmed** — the delivery channel reports success (no silent failures)
3. **Shown** — Edwin can see or access the result
4. **Persisted** — relevant state changes saved to memory / Notion
5. **Synced** — if the task touched T.G.A.O.T.U. structure, all three substrates updated

## 4. Agent Roster (registered Workers)

| Agent | Type | Location | Skill |
|---|---|---|---|
| Sherlock | Subagent | `~/.claude/agents/sherlock.md` | Read-only synthesis / landscape |
| Roaster | Subagent | `~/.claude/agents/roaster.md` | Notion + external intel |
| Brain-CORTEX | Autonomous | `~/eva-workspace/agents/CORTEX/` | Reasoning / decision |
| Brain-NEXUS | Autonomous | `~/eva-workspace/agents/NEXUS/` | Circuit design before build |
| Sofia gateway | Platform | `~/eva-workspace/sofia-core/` | 53 skills (Pass 2 pending) |
| n8n workers | Automation | `srv1613305:32777` | Cron / webhook / Notion bridges |
| Blender pipeline | Script | `~/eva-workspace/scripts/blender_*` | 3D / video generation |
| Eva-gateway | Service | `srv1613305` (eva-gateway/) | Telegram intake + LLM routing |

New agents are registered here by the Manager (Eva) when Edwin commissions them.

## 5. Sync Protocol — Three Substrates

After every structural change to T.G.A.O.T.U.:

1. Update local file in `~/TGAOTU/`
2. Propagate to Notion page `3656ae29` (curl, token from `/etc/eva-notion-bridge/env`)
3. Git commit + push to `github.com/dwinomarll/TGAOTU`
4. Update memory file `~/.claude/projects/-home-jetson/memory/project_tgaotu.md`

Eva enforces this. No structural change is complete until all four are updated.

## 6. Build Order (next phases)

| Phase | Task | Blocks |
|---|---|---|
| **P1** | Wire eva-gateway Phase 2 (Telegram intake) | Single-prompt → gateway |
| **P2** | Build plug-in router (task type → Worker routing table) | Automated dispatch |
| **P3** | Wire Sofia Pass 2 (activate 53 skills) | Visual + media Workers |
| **P4** | First end-to-end test: one prompt → end product via gateway | Proof of concept |
| **P5** | OpenClaw study lane substrate (separate workspace) | Scope expansion |
| **P6** | Tools-integration catalog workspace | Scope expansion |

Edwin commissions each phase. Eva builds. Blueprint I laws govern all phases.
