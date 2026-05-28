# Blueprint V — The Worker Reference Schema

**Status:** Canonical · seeded 2026-05-27
**Source:** [Blueprint I — The Hierarchy of Engagement](./hierarchy.md) (the Worker tier, drawn out)
**Commission:** Edwin, 2026-05-27 — *"encode the Worker Reference Schema."* (Commissioned as "Blueprint II" from a stale Mac view; renumbered to V on integration — II was already taken by [The Management Protocol](./management.md), its Manager-tier counterpart.)

---

## What this blueprint draws

Blueprint I named the tiers but left the **Worker** as a single line: *"single-file focused agents, glued to the end goal by reference `.md`."* That line is the most load-bearing in the whole hierarchy — the Worker is where intention becomes change. Blueprint V draws the Worker at full scale: its anatomy, its contract, and the exact shape of the reference `.md` that glues it.

A Worker is the **atomic unit of focus**. Everything above it (Manager, Workspace) exists to commission Workers cleanly. Everything below it (Files, Folder) is what a Worker touches. Get the Worker right and the hierarchy holds; get it wrong and the system drifts no matter how clean the tiers above.

It is the Worker-tier companion to [Blueprint II — The Management Protocol](./management.md): the Management Protocol's TASK MANIFEST has a `Worker(s)` field "assigned by Manager" — this schema defines what those assigned Workers *are*. Manager commissions; Worker executes.

## The Geometry

```
                 MANAGER
                    │   commissions — hands down the reference .md
                    ▼
   ┌───────────────────────────────────────────┐
   │                  WORKER                     │
   │                                             │
   │   ① END GOAL        the one outcome (lock)  │
   │   ② THE FILE        exactly one, owned      │
   │   ③ REFERENCE .md   the glue (this schema)  │
   │   ④ LINEAR PATH     straight, no branching  │
   │   ⑤ READS WIDE      context in, never edited│
   │                                             │
   └───────────────────────────────────────────┘
                    │   emits — the changed file + a report
                    ▼
                 MANAGER  (reconciles, never the Worker's peers)
```

A Worker reads widely and writes narrowly: it may consult any context, but it changes **one file** and reports the result **upward**. It never coordinates sideways with other Workers — the Manager is the only tier that sees the whole.

## What a Worker IS (the five invariants)

These descend directly from Blueprint I's Five Operating Laws, narrowed to the Worker scale:

1. **One Worker owns exactly one file.** Atomicity. The moment a Worker edits a second file, it has become polymathic and will drift. If the goal needs two files changed, that is two Workers (or one Worker run twice), reconciled by the Manager.
2. **The reference `.md` is the only source of the end goal.** The Worker does not infer scope from chat history, ambient context, or its own cleverness. Everything it is allowed to do is written in the reference `.md`. No reference, no Worker.
3. **The path is linear.** No branching, no "while I'm here" detours, no scope accretion. A straight walk from current state to Definition of Done.
4. **Reads are wide, writes are narrow.** A Worker may read any number of files for context — but those are *references*, not *targets*. It writes only to its one owned file.
5. **A Worker reports up, never sideways.** Completion, blockage, or surprise goes to the Manager. Workers do not call other Workers. Peer coordination is the Manager's job; smuggling it into a Worker collapses two tiers into one.

## The Reference `.md` — required anatomy

The reference `.md` is the glue. It is the contract the Manager writes and the Worker obeys. A valid reference `.md` has these sections — present, in order, none optional:

| § | Section | Purpose | Failure if missing |
|---|---|---|---|
| 1 | **End Goal** | The one outcome, stated in a single sentence. The lock. | Worker optimizes for the wrong thing |
| 2 | **The File** | The exact path of the single file this Worker owns. | Scope leaks across files (polymathic drift) |
| 3 | **Definition of Done** | Observable, checkable completion criteria. | Worker can't tell when to stop |
| 4 | **Out of Scope** | What the Worker must NOT touch or do. | Detours, "while I'm here" accretion |
| 5 | **Inputs** | What the Worker receives — args, upstream state, prior file contents. | Worker invents its own starting assumptions |
| 6 | **Context References** | Files/docs to READ for grounding (never to edit). | Worker edits a reference, or works blind |
| 7 | **Report Format** | What the Worker emits back to the Manager on done/block. | Manager can't reconcile the result |

The discipline of §4 (Out of Scope) is what keeps Law 3 (linear path) true. The discipline of §6 (Context References vs. The File) is what keeps Law 4 (read wide, write narrow) true. The schema enforces the invariants structurally — a Worker following a complete reference `.md` cannot easily drift.

## The Worker Template (the replication unit)

Blueprint I, Law 3: *"Templates are the unit of replication. You don't build the workplace per project — you instantiate it."* This is that template. The Manager fills the brackets and a Worker is born — no per-Worker engineering, just commission.

```markdown
# Worker: <short-name>

## 1. End Goal
<one sentence — the single outcome that means this Worker succeeded>

## 2. The File
<absolute or repo-relative path to the ONE file this Worker owns>

## 3. Definition of Done
- [ ] <observable criterion 1>
- [ ] <observable criterion 2>
- [ ] <the file type-checks / tests pass / renders / lints clean>

## 4. Out of Scope
- Do NOT touch any file other than the one in §2.
- Do NOT <known tempting detour 1>.
- Do NOT refactor, rename, or "improve" beyond the End Goal.

## 5. Inputs
- <arg / upstream value / current contents of the file, if any>

## 6. Context References (READ ONLY — never edit these)
- <path-or-url> — <why it matters to the goal>
- <path-or-url> — <why it matters to the goal>

## 7. Report Format
On done: report the diff summary + which Definition-of-Done boxes are checked.
On block: report the exact blocker + what input/decision is needed from the Manager.
Report UP to the Manager. Do not call other Workers.
```

## As Above, So Below

The same Worker schema instantiates in every kingdom of the stack:

- **MAAT** — MAAT Manager commissions a Worker to own `Sources/Terminal/VibeTunnelClient.swift`; reference `.md` = the task spec; linear path = implement reconnect-with-backoff; reports the diff up. One file, one Worker.
- **Eva** — a dispatched Claude Code subagent IS a Worker; its launch prompt + the doc paths it's handed ARE the reference `.md`; the one file it edits is §2. The Explore agent is the read-wide-write-nothing degenerate case (reads everything, owns no file — a scout, not a builder).
- **Sofia** — a single skill (honcho, deep-thinker) is a Worker; SOUL.md §V is the reference layer that keeps the skill glued to its job.
- **Notion Workers** — the atomic unit is **one capability**, not the whole `index.ts`. A worker file bundling 12 capabilities is 12 Workers sharing a substrate, not one polymathic Worker — the reference `.md` per capability keeps each linear. (Where this collapses into one sprawling handler, the schema is being violated; that's the diagnosis.)

The Architect drafted one Worker. Every agent that obeys its shape compounds; every agent that accretes scope drifts.

## Application notes — auditing a Worker

When designing or auditing any Worker in the stack, check it against the invariants:

- Does it own **exactly one** file? (Law 1)
- Is there a reference `.md` with all seven sections? (Law 2 / the anatomy)
- Is §4 (Out of Scope) explicit enough to stop the obvious detour? (Law 3)
- Are §6 context references clearly *read-only*, distinct from §2 the file? (Law 4)
- Does §7 send the report **up** to the Manager, with no sideways Worker calls? (Law 5)

A "no" at any line is the diagnosis — that is where the Worker will drift. A "yes" at every line is a Worker that walks straight.

---

*The atomic stone, cut to the same square every time. From identical stones, any building.*
