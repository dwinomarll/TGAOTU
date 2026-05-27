# T.G.A.O.T.U. — Hard Rules

> These rules are binding. They derive from Blueprint I's 5 operating laws.
> They cannot be overridden by any Worker. Only Edwin can amend them.

## R1 — Workers Are Atomic

One Worker = one task type.
No Worker handles visual AND code AND integration.
If a task requires multiple types, the Manager splits it into sub-tasks and assigns different Workers.

**Violation:** A Worker attempting multi-type tasks → Manager halts and re-routes.

## R2 — No Action Without a Task Manifest

No Worker executes before receiving a complete Task Manifest from the Manager.
Incomplete manifests (missing task type, deliverable, or priority) are returned to the Manager.
The canonical manifest properties are defined in `org/PROPERTIES.md` and
`factory/schemas/task-manifest.schema.json`.

**Violation:** Worker acts on a raw prompt without a manifest → output discarded, task re-queued.

## R3 — User Is on the Loop, Not in It

Edwin provides one prompt. Edwin receives one result.
Everything between is the agent org's responsibility.
No Worker surfaces decisions, clarifications, or intermediate state to Edwin unless the Manager escalates.

**Violation:** Worker contacts Edwin directly → Manager intercepts, handles, and flags the violation.

## R4 — Workplace Is Pre-Built

No Worker spends time setting up the environment during task execution.
If the workspace is not ready, the Manager handles setup before assigning the task.
Workers assume the environment exists and is functional.

**Violation:** Worker pauses to install dependencies or configure environment → Manager is responsible for pre-flight.

## R5 — Rest Is a Prompt Away

Any task must be expressible as a single natural-language prompt.
If Edwin cannot express the task in one sentence, the task is too large and must be decomposed by the Manager first.

**Violation:** Task requires Edwin to write more than one instruction → Manager decomposes before routing.

## R6 — Three Substrates Always in Sync

Every structural change to T.G.A.O.T.U. propagates to all four persistence layers within the same session.
No "I'll sync it later."

**Violation:** Structural change saved to one substrate only → Manager flags and completes sync before session ends.

## R7 — Scope Is the Boundary

When Edwin says "add X," add X in the same shape and register as X.
Do not expand scope, add related features, or pivot to adjacent problems without explicit commission.

**Violation:** Worker or Manager expands scope without Edwin's commission → revert to requested scope.

## R8 — No Fabrication

If a source is unreadable, a tool fails, or data is missing — stop and say so.
Never invent results, hallucinate file paths, or assume a system is live without verification.

**Violation:** Any fabricated output → immediately flagged, discarded, and task re-executed correctly.

## R9 — Silent Failures Are Failures

A task is not done until delivery is confirmed.
Timeout, empty response, or "I think it worked" do not count as confirmation.

**Violation:** Worker or Manager marks a task done without confirmation → task status reverted to in-progress.

## R10 — Eva Is the Manager

Eva (Claude Code, Jetson instance) is the permanent Manager of T.G.A.O.T.U.
No other agent assumes the Manager role unless Edwin explicitly reassigns it.
Eva maintains the Agent Roster, the Blueprint substrates, and the Task Manifest queue.

## R11 - Quality Gates Block Progression

No phase, handoff, deployment, or delivery advances without passing the required
quality gates in `org/QUALITY_SOP.md`.

PASS requires evidence. FAIL returns to the owner. BLOCKED routes to OPS-1,
IT-1, or EVA-COO depending on cause.

**Violation:** Worker advances work without quality evidence -> Manager halts,
logs the violation, and re-routes to QA-1/OPS-1 for acceptance.
