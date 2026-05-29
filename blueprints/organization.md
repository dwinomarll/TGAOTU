# Blueprint IV - Autonomous Organization

> Ptah is an organization first and a toolchain second.
> The system exists to convert vision into delivered work without requiring a
> human to operate the middle.

---

## Core Thesis

An organization is a structured system of roles, processes, and authority lanes
designed to achieve specific goals. Ptah applies that shape to an
autonomous software factory:

1. Edwin supplies intent.
2. The organization decomposes the intent.
3. Specialized agents execute atomic work.
4. Supervisors resolve blockers.
5. Delivery returns to Edwin as a notification unless there is a credential
   need, budget decision, taste decision, vision gap, or invited collaboration
   moment that truly requires action.

The user is the origin of vision, not the operator of the workflow.

---

## Human Policy

Default state:

- No human is required in the loop.
- Notification is required unless the user chooses silent mode.
- Edwin is the User / Founder / Vision Source.
- Eva is the COO / Chief of Staff / Org Manager.
- Other humans may be invited only as collaborators on a workplace, canvas, or
  review surface.

Invited collaborators provide additional input, critique, approval, domain
knowledge, or co-creation. They do not become required operators unless Edwin
explicitly assigns them that authority.

## Notification Policy

The organization distinguishes notification from escalation:

- Notification means the system informs the user through their preferred
  channel and continues operating.
- Escalation means the system needs a user decision before it can responsibly
  proceed.

Default channels are Telegram and email, with future support for workplace,
canvas, dashboard, webhook, or any user-selected delivery surface.

Routine progress, internal blockers, self-recovery, and quality failures do not
make the user part of the loop. They are handled inside the organization and
reported according to the user's cadence preference.

See `org/NOTIFICATION_SOP.md`.

---

## Foundational Departments

### 1. Executive and Leadership

| Role | Ptah mapping | Function |
|---|---|---|
| CEO | Edwin | Owns the vision, mission, final taste, and strategic direction. |
| COO | Eva | Runs daily operations, routing, delivery, sync, and enforcement. |
| CFO | Finance Agent | Handles budget limits, cost forecasts, billing risk, and spend reports. |

### 2. Core Operations and Service Delivery

| Role | Ptah mapping | Function |
|---|---|---|
| Product Manager | PM-1 | Turns vision into requirements. |
| Operations Manager | OPS-1 | Owns process flow, queues, handoffs, and capacity. |
| Customer Success Manager | CS-1 | Confirms delivered value, adoption, feedback, and retention of useful systems. |

### 3. Growth, Intake, and Demand

| Role | Ptah mapping | Function |
|---|---|---|
| Marketing Manager | MKT-1 | Turns shipped work into positioning, docs, examples, and outward signal. |
| Sales Manager | SALES-1 | Converts opportunities into commissions, scopes, and proposals when needed. |

### 4. Support and Infrastructure

| Role | Ptah mapping | Function |
|---|---|---|
| HR Manager | HR-1 | Agent lifecycle: hiring, onboarding, performance, retirement, culture. |
| IT/Systems Administrator | IT-1 | Tooling, credentials, infrastructure health, security posture, access. |

---

## Org Operating Model

```text
Edwin / invited collaborators
        |
        v
Eva COO intake and routing
        |
        v
Department leads
        |
        v
Atomic workers
        |
        v
QA + supervisor loop
        |
        v
Delivery report + substrate sync
        |
        v
User notification through preferred channel
```

Human collaboration enters only through the workplace/canvas layer:

- comment on a vision
- add domain constraints
- approve a design direction
- review a delivery candidate
- contribute assets or source material

The build loop itself remains autonomous unless a manifest explicitly marks a
human collaborator as required.

---

## Authority Rules

1. Edwin can change mission, budget, credentials, and taste direction.
2. Eva can change routing, staffing, process, and internal execution plans.
3. Department leads can change tactics inside their domain.
4. Workers can change implementation details inside their manifest.
5. Invited collaborators can advise or approve only within the canvas scope they
   were invited into.

---

## Required Org Properties

Every department, agent, active build, and invited collaborator must be
represented in the property model. The organization is not real until its roles
and state are inspectable.

See `org/PROPERTIES.md`.
