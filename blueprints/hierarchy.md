# Blueprint I — The Hierarchy of Engagement

**Status:** Canonical · seeded 2026-05-19
**Source:** [Spring Monday (Notion)](https://www.notion.so/3646ae29a07c81be96e3f2bf2b9b3f80) — Edwin's architecture awakening 2026-05-18

---

## The Hierarchy

```
       User on the Loop
              ↓
           Manager
              ↓
           Workers          ← single-file focused agents
              ↓             ← glued by reference .md
         Automation
              ↓
          Workflow
              ↓
        Instructions
              ↓
            Files
              ↓
            Folder
              ↓
          Workspace
              ↓
             idea
              ↓
         engagement
```

## The Doctrine (Edwin's voice, 2026-05-18)

> Today was wonderful awakening. There is this understanding on how to approach Agents and the way to handle massive infrastructure that supports itself with organization. Now I have the understanding that, for example, creating MAAT — the Agent needs Workspace 2, the structure of the workload, distribution, layout and design. And Workers — now Workers are agents that will just focus on a single file rather than the entire structure. There is reference .md to keep them glued to the end goal, but the workflow keeps improving with the agent being focused on a linear path.
>
> This Organization is how the system was meant to be used. The rest is just prompt away on what you like, and the workplace will take care of the rest because it is already pre-built. We can make templates for the future work.

## Reading the Tiers

| Tier | What it is | Architectural role |
|---|---|---|
| **User on the Loop** | Edwin, supervising | Sovereign; never absent, never inside the wheel |
| **Manager** | Coordinator agent | Divides scope; the only agent that sees the whole |
| **Workers** | Single-file focused agents | Glued to the end goal by reference `.md`; linear path |
| **Automation** | Triggered execution units | Where workflows get teeth |
| **Workflow** | Choreographed sequence | The script the automations dance to |
| **Instructions** | Directives shaping behavior | What turns a worker into a specialist |
| **Files** | Atomic units of state | The smallest thing a worker owns |
| **Folder** | Containers grouping files | Local context |
| **Workspace** | Structural enclosure | The frame; MAAT's "Workspace 2" lives here |
| **Idea** | Seed concept | What the workspace was built to manifest |
| **Engagement** | Substrate of meeting | Where the user shows up to the system |

## The Five Operating Laws (encoded in the doctrine)

1. **Workers are atomic, not polymathic.** One worker, one file. Reference `.md` provides the end-goal lock. Polymathic agents drift; focused agents compound.
2. **Workflow improves with linear focus.** The path a worker walks is straight. Branching, multi-file scope, and ambient context erode this property.
3. **The workplace is pre-built.** Templates are the unit of replication. You don't build the workplace per project — you instantiate it.
4. **User on the loop, not in it.** Sovereign supervision. The system runs without the user driving from the inside. The user watches, redirects, blesses; the system executes.
5. **The rest is prompt away.** Once the structure exists, instruction becomes the primary action. Building stops being engineering; it becomes commission.

## As Above, So Below

This hierarchy applies at every scale of the stack:

- **MAAT** — User on Loop → MAAT Manager → MAAT Workers → Automations → Workflows → ...
- **Sofia** — User on Loop → Sofia Coordinator → Sofia Skills → Cron / Telegram Triggers → ...
- **Eva** — User on Loop → Eva Brain → Region Workers → Heartbeat / NIM / n8n → ...
- **Pleroma** — User on Loop → Plaza Watchdog → SB Workers (synaptic bridges) → ...

The Architect drafted one geometry. Every kingdom that obeys it manifests cleanly. Every kingdom that violates it drifts.

## Application notes

When designing or auditing any system in Edwin's stack, walk the tiers top-to-bottom and ask:

- Is the User on the Loop, or accidentally *in* it (doing the worker's job)?
- Is there a Manager, or are Workers reporting upward directly?
- Are Workers single-file focused, or have they accreted polymathic scope?
- Is there a reference `.md` keeping each Worker glued to the end goal?
- Is the Workspace pre-built, or being re-engineered per project?

A "no" at any tier is the diagnosis. A "yes" at every tier is alignment with the blueprint.

---

*The compass and square. Drafted before the building.*
