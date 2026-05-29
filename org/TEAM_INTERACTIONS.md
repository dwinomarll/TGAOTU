# Ptah Team Interaction Protocol

> How AI departments coordinate without turning the user into the coordinator.

---

## Default Rule

Teams do not interrupt Edwin. Teams coordinate through artifacts, manifests,
logs, and Eva's routing layer.

The only allowed human interruptions are:

- vision change
- credential need
- budget decision
- invited collaboration gate
- final delivery

---

## Handoff Packet

Every team-to-team handoff must include:

| Field | Meaning |
|---|---|
| `handoff_id` | Stable id for the transfer |
| `from_position` | Sending AI position |
| `to_position` | Receiving AI position |
| `app_name` | Active build |
| `phase` | Phase number or `prebuild` |
| `input_artifacts` | Files the receiver should read |
| `output_expected` | What the receiver must produce |
| `validation` | How the receiver proves completion |
| `assumptions` | Decisions or assumptions the receiver must preserve |
| `evidence` | Test output, source section, report path, or commit reference |
| `next_action` | The exact next action expected from the receiver |
| `open_questions` | Questions for Eva/SUP, not Edwin |
| `status` | queued, accepted, blocked, complete |

---

## Team Interfaces

### Product -> Design

Product hands off `PRD.md`.

Design may ask for clarification only if:

- a required feature contradicts another required feature
- the user persona is unclear
- a must-not blocks the requested interface

### Design -> Architecture

Design hands off `UI-SPEC.md`.

Architecture may adjust implementation details but must preserve:

- information hierarchy
- interaction model
- accessibility requirements
- explicit exclusions

### Architecture -> Engineering

Architecture hands off `BLUEPRINT.md` and phase manifests.

Engineering may choose implementation details inside the assigned phase, but may
not change:

- tech stack
- phase order
- validation command
- deliverable list

### Engineering -> QA

Engineering hands off changed files and validation evidence.

QA validates, reports, and classifies failures. QA does not repair unless a new
manifest assigns repair work.

### QA -> DevOps

QA hands off only passed artifacts.

DevOps deploys and confirms the runtime. Deployment failure routes to SUP-1.

### DevOps -> Eva

DevOps hands off the delivery location, runtime status, and verification
evidence. Eva writes the Delivery Report.

---

## Conflict Resolution

| Conflict | Resolver |
|---|---|
| Product vs Design | Eva |
| Design vs Architecture | Eva + ARCH-1 |
| Architecture vs Engineering | SUP-1 |
| Engineering vs QA | SUP-1 |
| Deployment vs Budget | Eva -> Edwin |
| Credential missing | Eva -> Edwin |
| Human collaborator disagreement | Eva; Edwin only if vision changes |

---

## Logs

Team interaction logs live in:

- `org/logs/handoffs.log`
- `org/logs/supervisor.log`
- `org/prompts/prompt-audit.ndjson`

Silent coordination is not coordination. If it changed state, it gets logged.

See also: `org/LOGGING_SOP.md`.
