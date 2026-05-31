# Ptah Boot-Sync ("ptah-sync") — Design · **Distributed MJP-01**

> GitHub `origin/main` is the always-current canon; every device is a **convergent replica**.
> On boot/session-start each device reconciles **to** the canon: fetch -> rebase local work
> ONTO cloud -> push. History stays **linear** so branches always "connect" instead of forking.
> No divergent branch ever strands; no boot is ever blocked.

- **Status:** ✅ Hardened + verified. Adversarial stress-test found 5 HIGH-severity defects in
  the first draft (2 silent-data-loss, 1 bash-3.2 exit-0 contract violation, 1 detached-HEAD
  orphan, 1 feature-branch strand); all fixed. **37/37** assertions pass via
  `factory/hooks/test-ptah-sync.sh` on `/bin/bash` 3.2. Live dry-run against both real repos: clean.
- **Codename:** Distributed MJP-01.
- **Hardening applied beyond the first draft:** never double-stash (DIVERGED+dirty no longer
  orphans uncommitted work); contributor reset-to-canon failures are surfaced (no `|| true`
  mislog) and asserted via `HEAD == origin/main`; `trap 'exit 0' EXIT` + empty-array guard make
  the exit-0 contract hold on bash 3.2; detached-HEAD commits are **rescued** to a pushed
  `sync/<host>/<ts>-detached` branch before switching; non-`main` feature branches are **backed
  up** (never auto-merged, never silently stranded); per-repo `mkdir` lock + in-progress-op guard
  prevent concurrent collisions; solo repos (default: `eva-discord`) ff-push `main` directly
  instead of the PR dance; `gh`-absent offloads log a loud `PUSH-BRANCH-NO-PR`.
  **The script (`ptah-sync.sh`) is the source of truth where any step detail below differs.**
- **Script:** `factory/hooks/ptah-sync.sh` (bash-3.2-safe, idempotent, always `exit 0`).
- **Tests:** `factory/hooks/test-ptah-sync.sh` (bare-origin harness; run before any change).
- **Doctrine it enforces:** the READ/RECONCILE half of the Federation Protocol
  (`org/FEDERATION_SOP.md`, F1–F5). The WRITE half is already enforced by
  `factory/hooks/pre-push`. ptah-sync **reuses** `factory/hooks/federation-lib.sh`
  (`fed_is_manager`, `fed_*`) — it does not reinvent role logic.
- **Manager of record (Ptah):** Jetson (`FEDERATION_MANAGER_HOSTS="eva jetson"`). Every
  other device is a *contributing instance* and may never write `main` directly.

---

## 0. The two repos

There are **two independent GitHub repos**, each its own clone with its own `.git` and
remote:

| Repo | Remote | Mac path | Headless path |
|------|--------|----------|---------------|
| `TGAOTU` (Ptah) | `github.com/dwinomarll/TGAOTU.git` | `/Users/edwinrosa/TGAOTU` | `~/TGAOTU` |
| `eva-discord` | `github.com/dwinomarll/eva-discord.git` | `/Users/edwinrosa/TGAOTU/eva-discord` (nested, gitignored) | `~/eva-discord` (sibling) |

A single `git pull` in TGAOTU does **not** touch eva-discord. `ptah-sync.sh` **loops over
both** and auto-detects nested (Mac) vs sibling (Jetson/VPS) layout.

`.gitignore` deliberately ignores `.claude/`, `factory/active/`, `eva-discord/`. The sync
**never** `git add -A` outside the WIP-commit path, and even there `.gitignore` shields
those trees. It is fetch-and-reconcile, not a blind stage-everything.

---

## 1. The script — `factory/hooks/ptah-sync.sh`

The full body lives at `factory/hooks/ptah-sync.sh`. Algorithm per repo:

```
STEP 0  preconditions
        - is a git repo? has origin? else SKIP (logged).
        - detached HEAD  -> switch to main (I1 recovery), never boot detached.
        - not on main    -> SKIP, leave the branch untouched (don't clobber WIP).
        - ensure main tracks origin/main (I2).
STEP 1  snapshot HEAD (reflog-recoverable anchor, logged).
STEP 2  dirty tree -> `git stash push --include-untracked` (timestamped). NEVER reset --hard.
STEP 3  `git fetch --prune --tags origin`  <-- the ONLY network call.
        fetch fails (offline) -> pop stash, mark OFFLINE, exit. Never act on stale state.
STEP 4  classify, network-free:
            L=rev-parse main  R=rev-parse origin/main  B=merge-base main origin/main
            L==R        -> UP-TO-DATE
            L==B,L!=R   -> BEHIND
            R==B,L!=R   -> AHEAD
            else        -> DIVERGED
STEP 5  act:
            UP-TO-DATE  -> nothing
            BEHIND      -> `git merge --ff-only origin/main`   (can NEVER make a merge commit;
                           on a race it exits non-zero -> re-fetch + retry once)
            AHEAD       -> ahead_push()  [role-gated, below]
            DIVERGED    -> `git rebase --autostash origin/main`
                             success -> ahead_push()
                             conflict -> `git rebase --abort` + ALERT + BLOCKED, exit
STEP 6  pop the step-2 stash (if rebase path didn't already). pop conflict ->
        leave markers, KEEP named stash, ALERT, never drop.
STEP 8  assert still on main / tracking origin/main; emit one structured log line +
        a `=== PTAH SYNC ===` block to stdout (injected into Claude's context).
```

`ahead_push()` is the orphan-prevention core:

- **Manager of record** (Jetson, or `FEDERATION_OVERRIDE=1`): `git push origin main`
  (plain fast-forward; the pre-push hook permits ff). If rejected non-ff (someone pushed
  first) -> re-fetch, `rebase --autostash`, retry once; else abort + alert. **Never** `--force`.
- **Contributing instance** (Mac/VPS/Ally): create deterministic `sync/<host>/<ISO8601>`
  at HEAD, `git push -u origin <branch>`, `gh pr create --base main` (idempotent), then
  `git reset --keep origin/main` to return local main to canon. The device ends **clean,
  on main, tracking origin/main**, and its work has a **named, pushed, PR'd home** — the
  literal opposite of a stranded branch.

**Logging:** one tab-delimited line per event into
`<repo>/.remember/logs/ptah-sync-YYYY-MM-DD.log` (falls back to `$TMPDIR`). Plus the
human `=== PTAH SYNC ===` summary on stdout.

**Env escapes** (mirror the existing hooks): `FEDERATION_OVERRIDE=1`,
`FEDERATION_MANAGER=1`, `PTAH_SYNC_DRYRUN=1` (classify + log only, no writes),
`PTAH_SYNC_REPOS="…"`, `PTAH_SYNC_LOG=…`.

**Verified offline** (bare-origin harness, no network): BEHIND fast-forwards; AHEAD-as-
manager ff-pushes to main; AHEAD-as-contributor creates `sync/<host>/<ts>` + resets to
canon; DIVERGED-conflict aborts cleanly, preserves the local commit, flags BLOCKED, exits 0.

---

## 2. Boot wiring, per device

### Mac (`maxed-m4`) — contributing instance, the human work surface

**Primary: Claude Code SessionStart hook** (runs *in addition to* the remember plugin's
SessionStart hook; does not replace it). Create `/Users/edwinrosa/TGAOTU/.claude/settings.json`:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          { "type": "command",
            "command": "bash /Users/edwinrosa/TGAOTU/factory/hooks/ptah-sync.sh" }
        ]
      }
    ]
  }
}
```

> `.claude/` is gitignored, so this is local-only (correct — boot wiring is per-device).
> The **script** lives in the tracked `factory/hooks/`, so it ships to every clone; only
> the *invocation* is per-device. Hook stdout is injected into the session, so the
> `=== PTAH SYNC ===` summary appears in Claude's briefing exactly like `=== MEMORY ===`.

**Optional: LaunchAgent for non-Claude boots / periodic re-sync.** Matches the existing
`ai.eva.*` convention. `~/Library/LaunchAgents/ai.eva.ptah-sync.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>ai.eva.ptah-sync</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>/Users/edwinrosa/TGAOTU/factory/hooks/ptah-sync.sh</string>
  </array>
  <key>RunAtLoad</key><true/>
  <key>StartInterval</key><integer>1800</integer>   <!-- re-sync every 30 min -->
  <key>StandardOutPath</key><string>/Users/edwinrosa/TGAOTU/.remember/logs/ptah-sync.launchd.log</string>
  <key>StandardErrorPath</key><string>/Users/edwinrosa/TGAOTU/.remember/logs/ptah-sync.launchd.log</string>
</dict></plist>
```

Mac auth: `gh` keyring over HTTPS, credential helper `gh auth git-credential` — headless,
no prompt at boot.

### Jetson (`eva`, 100.88.180.54) — **Manager of record**, headless

Auth already works: SSH `~/.ssh/github_key` via an ssh-config `Host github.com` alias
(`ssh -T git@github.com` => `Hi dwinomarll!`). TGAOTU already cloned at `/home/jetson/TGAOTU`
(but **stale at #3 vs origin #18** — that staleness is the exact problem this fixes).

First-time steps:
```bash
cd /home/jetson/TGAOTU && git pull --ff-only          # closes the #3 -> HEAD gap immediately
git clone git@github.com:dwinomarll/eva-discord.git /home/jetson/eva-discord
git config core.hooksPath factory/hooks                # arms pre-commit/pre-push (and ships the script)
```
Boot hook — simplest is cron `@reboot` + a periodic interval:
```bash
crontab -e
# @reboot      /home/jetson/TGAOTU/factory/hooks/ptah-sync.sh >> /home/jetson/.ptah-sync.log 2>&1
# */30 * * * * /home/jetson/TGAOTU/factory/hooks/ptah-sync.sh >> /home/jetson/.ptah-sync.log 2>&1
```
Or a systemd `oneshot` unit with `After=network-online.target` if you prefer a real
dependency on the network being up. Because the hostname is `eva`, `fed_is_manager`
returns true here, so Jetson **ff-pushes** to main (no PR offload).

### VPS (Hostinger `srv1613305`) — contributing instance, headless, **needs auth bootstrap**

No `gh`, no GitHub key, no clones yet. Bootstrap (recommended: deploy key, mirrors Jetson):
```bash
ssh-keygen -t ed25519 -f ~/.ssh/github_key -N ""
cat ~/.ssh/github_key.pub      # add as a read+write Deploy Key on BOTH repos in GitHub
printf 'Host github.com\n  IdentityFile ~/.ssh/github_key\n  IdentitiesOnly yes\n' >> ~/.ssh/config
git clone git@github.com:dwinomarll/TGAOTU.git     /root/TGAOTU
git clone git@github.com:dwinomarll/eva-discord.git /root/eva-discord
cd /root/TGAOTU && git config core.hooksPath factory/hooks
crontab -e   # same @reboot + */30 lines as Jetson, pointing at /root/TGAOTU/...
```
> A GitHub **Deploy Key is per-repo**, so add the one VPS pubkey to *both* repos. (Alt:
> a fine-grained PAT scoped to these two repos + `credential.helper store`.) VPS is a
> contributor, so any local commits go out as a `sync/<host>/<ts>` PR, never onto main.

### Ally (`x-roger`, Windows) — optional tier-3

Not in the named Mac/Jetson/VPS set, intermittently offline. If wired later: install Git +
Git Bash, clone both repos, add a **Task Scheduler** "At log on" task running
`bash .../ptah-sync.sh`. Contributing instance. Skip until the three core nodes are proven.

### iPhone (`iphone182`) — **read-only, excluded**

Omi capture device: no shell, no git, no boot hook. It reaches the hub through the
Omi/API/Notion layer, not GitHub. **Not in the sync mesh.**

---

## 3. Conflict / divergence policy — RECOMMENDED safe default

| Situation | Action | Why |
|-----------|--------|-----|
| **BEHIND** | `merge --ff-only origin/main` | Can never create a merge commit; no merge-commit spam. |
| **AHEAD (manager)** | `push origin main` (ff only) | Pre-push hook permits ff; never `--force`. |
| **AHEAD (contributor)** | branch `sync/<host>/<ts>` + PR + `reset --keep origin/main` | Work reaches the hub as a PR; device returns to clean canon. |
| **DIVERGED (clean)** | `rebase --autostash origin/main` | Linear history, canon is trunk; then flows into the AHEAD path. |
| **DIVERGED (true conflict)** | `rebase --abort` -> preserve -> **ALERT** -> `BLOCKED-NEEDS-HUMAN` | Conflict resolution is a human/Manager act, never autonomous (Blueprint Law 4, user on the loop). |
| **Dirty tree** | `stash --include-untracked` (or rebase `--autostash`); pop after | Untracked agent files are real work; never `reset --hard` / `checkout -- .` (banned). |
| **stash pop conflict** | leave markers, **keep** named stash, alert | Never auto-`drop`; work stays recoverable. |
| **Offline at boot** | skip, stay on current main, log OFFLINE | Never act on stale remote state. |

**RECOMMENDED default for uncommitted work at an *agent/headless* boot:** *(this is the
one knob — see §6)*. The doctrine-safe default is **STASH-AND-LEAVE**: preserve, never
author commits in Edwin's name, surface in the summary. The alternative (auto-WIP-commit)
gets work to the hub faster but writes commits autonomously.

The unbreakable rule under every branch: **never destroy local work, never auto-resolve a
conflict, never force-push, always exit 0.**

---

## 4. How GitHub stays the canonical current main + orphan prevention

**Server-side (unbypassable — a `--no-verify` or fresh clone bypasses the local hook, but
not this):** enable a **branch-protection ruleset on `main`**:
- Require a PR before merge.
- Require the **`factory-tests`** status check (`.github/workflows/factory-tests.yml`) — wire it as **required**.
- Require branch **up-to-date before merge** (forces contributors to rebase onto latest canon — a stale diverge can't merge).
- **Block force-push** and **block deletion** on main (makes F4 a server guarantee).
- **Require linear history** (rebase/squash only — no merge-commit spam at the hub either).
- Restrict merge to the Manager-of-record identity / Edwin.

**Optional scheduled Action — "assert main is canon" (e.g. hourly):** check out main and
assert `factory-tests` is green on HEAD, no PR sits un-reconciled past a threshold, and
HEAD matches the last merged PR's merge SHA (detects any out-of-band push). Notify on
failure. This is the hub-side mirror of the device-side STEP-8 invariant.

**Why the orphan/divergent-branch problem cannot happen:**
1. STEP 0 recovers a detached HEAD back to main and refuses to boot detached (I1).
2. Local-only commits are *always* either ff'd to main (manager) or pushed as a
   **named** `sync/<host>/<ts>` branch + PR (contributor) **before STEP 8 completes** (I3).
   A contributor's divergent work gets a named, pushed, PR'd home on GitHub.
3. A device that sleeps with new commits cannot keep them hostage past its next boot — the
   next sync offloads them.
4. Concurrent manager pushes: the second is rejected non-ff by GitHub -> that node
   re-syncs, re-classifies AHEAD-after-fetch, rebases, retries (FM10).
5. Force-push to main is blocked at three layers: the local pre-push hook, server branch
   protection, and the algorithm never issuing `--force`.

---

## 5. Install plan (Mac first) + rollback

> Wire order: **Jetson 1st** (already cloned + SSH auth; just stale — fastest proof),
> **Mac 2nd** (clean, gh-auth, lowest risk), **VPS 3rd** (needs auth bootstrap). But install
> the *script* the same way everywhere; only the boot trigger differs.

**Step A — land the script (already done in this branch).**
`factory/hooks/ptah-sync.sh`, executable, verified offline.
*Rollback:* `git rm factory/hooks/ptah-sync.sh`.

**Step B — Mac SessionStart hook.**
Create `/Users/edwinrosa/TGAOTU/.claude/settings.json` with the §2 JSON.
Test: open a new Claude session, confirm a `=== PTAH SYNC ===` block appears.
*Rollback:* delete that `settings.json` (or remove the `hooks` key). The remember
plugin's own SessionStart hook is untouched.

**Step C — Mac LaunchAgent (optional).**
Write `~/Library/LaunchAgents/ai.eva.ptah-sync.plist`, then
`launchctl load ~/Library/LaunchAgents/ai.eva.ptah-sync.plist`.
*Rollback:* `launchctl unload …` then delete the plist.

**Step D — Jetson.** `git pull --ff-only`; clone eva-discord; `git config core.hooksPath
factory/hooks`; add the `@reboot` + `*/30` crontab lines. Test:
`FEDERATION_MANAGER=1 PTAH_SYNC_DRYRUN=1 factory/hooks/ptah-sync.sh`.
*Rollback:* `crontab -e` remove the two lines; `git config --unset core.hooksPath`.

**Step E — VPS.** Bootstrap deploy key; clone both; set hooksPath; add crontab.
*Rollback:* remove crontab lines; remove the Deploy Key in GitHub; `rm -rf` the clones.

**Step F — GitHub branch protection + (optional) scheduled assert Action.**
Enable the §4 ruleset; mark `factory-tests` required.
*Rollback:* disable the ruleset (no client change needed).

**Validate each node after wiring:** `git -C <repo> rev-parse HEAD` must equal
`git -C <repo> rev-parse origin/main` post-boot, both repos.

**Global kill switch:** set `FEDERATION_OVERRIDE=` unset + just remove the boot trigger;
or rename `ptah-sync.sh`. The script never runs unless a trigger calls it.

---

## 6. The ONE decision Edwin must approve before install

**When a *headless/agent* boot finds uncommitted local changes, should ptah-sync
auto-create a labeled WIP commit (so the work travels to the hub as a PR), or
stash-and-leave it (preserve locally, author nothing, surface in the summary)?**

- **RECOMMENDED: stash-and-leave** (the script's current default). It never authors
  commits in your name without consent, it never destroys work, and it surfaces the
  dirty state in the `=== PTAH SYNC ===` summary for you to decide. Trade-off: a stash is
  local-only, so genuinely-meaningful uncommitted work won't reach the hub until you act.
- **Alternative: auto-WIP-commit** on headless boots only — a commit travels via PR and is
  reflog-recoverable on every device, closing the "work stays local" gap faster, at the
  cost of the sync authoring commits autonomously.

Flip to auto-WIP only by your explicit say-so; the BEHIND/AHEAD/DIVERGED/conflict logic is
identical either way.
