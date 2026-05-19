# Blueprint III — The App Factory Protocol

> The machinery that turns one vision into a shipped app. No human in the loop.
> Edwin inputs the WHAT. The Factory owns the HOW, WHEN, and WHO.
> Edwin re-enters only when the Factory hits a true structural blocker.

---

## The Factory Contract

```
Edwin drops:   VISION.md  (one document, one time)
Factory ships: working app  (git repo + deployed service + delivery confirmation)
Edwin sees:    nothing in between — only the result
```

---

## Stage 1 — Vision Intake

Edwin fills out one file: `factory/templates/VISION.md`

Fields (all required):
- **Name** — what the app is called
- **Purpose** — one sentence: what problem it solves for Edwin
- **Platform** — iOS / macOS / web / API / CLI / mixed
- **Reference** — existing app Edwin points to as model (e.g., "like MAAT but for X")
- **Must-haves** — 3–7 non-negotiable features
- **Must-nots** — explicit exclusions (Edwin's constraints)
- **Success signal** — how Edwin knows it worked (one verifiable test)

The Factory reads this file. Edwin does not explain further.

---

## Stage 2 — Architect Agent (Blueprint Generation)

The Architect reads VISION.md and produces `factory/active/<app-name>/BLUEPRINT.md`.

BLUEPRINT.md contains:
1. **Tech stack decision** — language, framework, DB, infra (with rationale)
2. **File tree** — complete directory structure before first file is written
3. **Phase breakdown** — 4–8 ordered phases, each with: goal, deliverables, validation test
4. **Agent assignments** — which Worker handles each phase
5. **Dependency graph** — which phases must complete before which
6. **Escalation triggers** — the 3 specific conditions that pause and ping Edwin

The Architect does NOT ask Edwin to review before building starts.
All tech decisions belong to the Architect. Edwin's constraints are in VISION.md — that is the full brief.

---

## Stage 3 — Build Loop (autonomous execution)

For each phase in BLUEPRINT.md:

```
LOOP:
  1. Worker reads phase spec from BLUEPRINT.md
  2. Worker checks BUILD_STATE.md — confirms previous phase passed
  3. Worker executes (writes code, deploys service, creates config)
  4. Worker runs validation test defined in BLUEPRINT.md
  5. If PASS → mark phase complete in BUILD_STATE.md → advance
  6. If FAIL → self-repair up to 3 attempts:
       - Analyze error
       - Apply fix
       - Re-run validation
     If FAIL after 3 attempts → log blocker → escalate to Manager
  7. Manager decides: retry with different approach OR escalate to Edwin
```

Workers never skip validation. A phase is not done until the test passes.
Workers never contact Edwin. They escalate to Manager only.

---

## Stage 4 — Build State Tracking

Every active build has `factory/active/<app-name>/BUILD_STATE.md`:

```markdown
# BUILD STATE — <app-name>

## Current Phase: <N>
## Overall Status: in_progress | blocked | complete

| Phase | Title | Status | Validated | Notes |
|-------|-------|--------|-----------|-------|
| 1 | Setup + scaffolding | ✅ complete | xcodebuild passes | |
| 2 | Data models | 🔄 in_progress | — | |
| 3 | Core UI | ⏳ pending | — | |
```

BUILD_STATE.md is the single source of truth. Updated after every phase result.

---

## Stage 5 — Escalation Gate (3 cases only)

The Factory pings Edwin ONLY for:

| Case | Trigger | What Edwin sees |
|------|---------|-----------------|
| **Structural** | A phase requires a decision that changes the vision itself | One-sentence question + recommended path |
| **Credential** | A service requires a key/account Edwin hasn't provided | "Need X credential for Y service" |
| **Budget** | A service would incur cost Edwin hasn't approved | "Deploying Z costs ~$X/mo. Proceed?" |

Everything else — library selection, UI details, file naming, architecture choices, error handling — the Factory decides. Edwin is not consulted.

---

## Stage 6 — Delivery Report

When all phases complete:

1. Factory sends Edwin a Delivery Report (Telegram + INBOX)
2. Report contains:
   - App name + what was built
   - Where to find it (repo URL, TestFlight link, endpoint URL)
   - How to verify (success signal from VISION.md, now confirmed)
   - What Edwin can commission next

---

## Factory Directory Layout

```
factory/
├── templates/
│   └── VISION.md          — Edwin fills this in for each new app
├── active/
│   └── <app-name>/
│       ├── VISION.md      — Edwin's brief (read-only after Stage 1)
│       ├── BLUEPRINT.md   — Architect's complete technical plan
│       └── BUILD_STATE.md — live phase tracker
├── delivered/
│   └── <app-name>/        — moved here after delivery confirmed
└── blocked/
    └── <app-name>/        — moved here when escalation fires
```

---

## Agent Assignments for App Builds

| Phase type | Worker | Method |
|------------|--------|--------|
| iOS / Swift | Codex (Mac) or Claude Code | `--print --permission-mode bypassPermissions` |
| Python API / FastAPI | Claude Code | direct execution |
| Infrastructure | Eva | systemd / Docker / Caddy |
| Testing | Same Worker that built the phase | XCTest / pytest / curl |
| Deployment | Eva | git push / xcrun devicectl / systemctl restart |
| Notion / memory | Eva | curl → Notion API |

---

## Governing Law

Derived from Blueprint I — Law 4:
> "User is on the loop, not in it. Edwin provides the prompt and reviews the result.
> Everything between is the agent org's responsibility."

**The Factory IS everything between.**
