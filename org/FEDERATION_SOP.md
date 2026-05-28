# T.G.A.O.T.U. — Federation Protocol (Multi-Instance Coordination)

> How the many Eva instances stay one body.
> `INSTRUCTIONS.md` governs the agents *inside* one Eva-managed org. This file governs
> the Eva *instances themselves* when several are awake at once across machines.
> Binding; only Edwin amends. Derived from Blueprint I Law 4 (user on the loop),
> Blueprint V Law 5 (report up, never sideways), and `RULES.md` R10 (Eva is the Manager).

---

## Why this exists

On 2026-05-27, three Eva instances — **Mac/Claude Code, Mac/Codex, Jetson/Claude Code** —
built T.G.A.O.T.U. concurrently, each acting as a Manager, blind to one another. Result:
duplicate Blueprint II's and III's, a stuck git rebase, and Edwin pulled *into* the loop to
decide which version was canon.

Root cause: `RULES.md` R10 names Jetson-Eva the permanent Manager, but **no rule said what the
*other* live instances do.** The factory's org rules cover agents inside one org; nothing
covered "Eva running on four machines at the same time." This file is that missing rule.

## The two levels (do not confuse them)

| Level | Governs | Doctrine |
|---|---|---|
| **Agent level** | positions inside one Eva-managed org (PM-1, ENG-PY, QA-1, DEVOPS-1…) | `INSTRUCTIONS.md`, `TEAM_INTERACTIONS.md`, `RULES.md` |
| **Instance level** | the Eva *instances* themselves (Mac/Claude, Mac/Codex, Jetson, Lilith) | **this file** |

A single Eva instance may *be* the Manager and run a whole org of agents. The question here is:
when several Eva instances are awake at the same time, **which one is in charge of a given
project, and how do the others behave?**

## The Federation

| Node | Substrate | Default stance |
|---|---|---|
| Jetson · Claude Code | `CLAUDE.md` / `AGENTS.md` | **Manager of record for T.G.A.O.T.U.** (`RULES.md` R10) |
| Mac · Claude Code | `CLAUDE.md` | Contributing instance |
| Mac · Codex | `AGENTS.md` | Contributing instance |
| Lilith / VPS · gateway | — | Service instance (no autonomous builds) |

**Shared body (the nervous system):** git (`eva-workspace`, `TGAOTU`), shared memory
(`memory-sync.sh`), the work registry (`scripts/work_check.py`), Notion.

---

## F1 — One Manager of record per project

Every shared project has exactly one **Manager of record** — the instance authoritative for its
`main`. For T.G.A.O.T.U. it is **Jetson-Eva** (R10). Every other instance is a **contributing
instance**, not a second Manager.

`coo-slot.md` assumes a single active occupant of the orchestrator role; this rule makes that
explicit under concurrency: **two live instances are not two Managers.**

## F2 — Claim before you build (the hard gate)

No instance touches shared work before:

1. `python3 scripts/work_check.py check "<task>"` — read the ledger.
2. If unclaimed → `claim "<task>"`. If already claimed by another instance → **stop.** Coordinate
   through the registry or escalate. Do not build the same thing twice.
3. `release "<task>"` when done.

The registry is the federation's Manager-queue when instances cannot talk live.

**Violation:** an instance commits shared-project work with no prior claim → the work goes to a
branch, not `main`; the Manager of record reconciles. *(Tonight's collision was three unclaimed
builds. A guardrail you can drive around is not one.)*

## F3 — Contributing instances branch and PR; they never write `main`

A contributing instance NEVER commits to a Manager-owned project's `main`. It:

1. Branches off `origin/main`.
2. Builds **additively** — never renumbers, overwrites, or deletes the Manager's artifacts
   (blueprints, schemas, agent contracts).
3. Pushes the branch and opens a PR for the Manager of record (or Edwin) to merge.

This is the cross-instance form of `INSTRUCTIONS.md`'s "report up, never sideways." **A PR is
reporting up. A direct push to `main` is acting sideways.** (Codex's `blueprint-v-worker-schema`
branch did this correctly; the Mac's direct `main` commits did not — this very file is delivered
by branch + PR to obey its own rule.)

## F4 — `origin/main` is canon; never force-push over it

The Manager of record's `origin/main` is the single source of truth. No contributing instance
force-pushes over it under any circumstance. If a contributing instance's local diverges, it
**resets to `origin/main`** and re-contributes via branch + PR. *(Done on the Mac 2026-05-27;
the diverged Mac drafts were archived to `~/TGAOTU-mac-docs/`, not forced onto origin.)*

## F5 — The Manager owns structural memory; contributors flag, don't race

`INSTRUCTIONS.md`: the Manager writes memory. Across instances: structural memory about a
Manager-owned project (`project_tgaotu.md`, the `MEMORY.md` index) belongs to the **Manager of
record**, who keeps `RULES.md` R6 (substrates in sync, no "later"). A **contributing instance may
record findings** but flags them for the Manager and runs `memory-sync.sh` only when the
Manager's node is quiet — to avoid reproducing the build collision inside the memory repo.

## Cross-instance escalation ladder

```
Contributing instance hits a conflict with a peer instance
        → it CANNOT out-rank a peer (instances are equals)
        → escalate to Edwin (the Loop)  — instances never overrule each other
Edwin decides
        → Manager of record records the decision in memory + Notion, routes it down
```

Instances are peers; none can overrule another. Only Edwin (on the Loop) or the designated
Manager of record breaks a tie. This is Blueprint V Law 5 at the instance scale: peers report
up, never sideways.

## Enforcement (named, not yet built)

F2–F4 are honor-system rules until enforced in code. Target: a **pre-commit / pre-push hook** in
the shared repos that refuses the operation when

- the work is unclaimed in the registry, or
- a contributing instance is committing directly to `main`.

Until that hook exists, every instance obeys F2–F4 by discipline. *(Tracked as the next
Federation build — this is the difference between a guardrail and a wish.)*

---

*Many hands, one body. The instance that forgets it is one of many is the instance that collides.*
