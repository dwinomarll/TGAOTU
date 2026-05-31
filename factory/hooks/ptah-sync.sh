#!/usr/bin/env bash
# ptah-sync.sh — Distributed MJP-01 : boot/session-start GitHub reconciliation
# for the 4-device Ptah mesh.
#
# Doctrine (MJP-01): origin/main is the single source of truth; every device is a
# CONVERGENT REPLICA. The boot ritual is fetch -> rebase local work ONTO cloud -> push,
# so history stays LINEAR and branches always "connect" instead of forking. This script
# is the READ/RECONCILE counterpart to factory/hooks/pre-push (the WRITE enforcement).
#
# Contract:
#   * Idempotent and safe to run on every boot / Claude SessionStart.
#   * ONE network round-trip per repo in the common path (fetch); everything else local.
#   * NEVER force-pushes, NEVER `git reset --hard` a dirty tree, NEVER `checkout -- .`,
#     NEVER auto-resolves a true conflict. On conflict -> abort + alert + leave usable.
#   * NEVER strands work: detached-HEAD commits and feature-branch commits are backed up
#     to a named remote branch BEFORE anything else; uncommitted work is stashed, never lost.
#   * ALWAYS exits 0 (trap) so a failure never blocks startup.
#   * Loops over BOTH repos: TGAOTU and the independently-cloned eva-discord.
#
# Role gating reuses factory/hooks/federation-lib.sh (fed_is_manager). Manager of record
# (or a SOLO repo) fast-forward-pushes main; contributing instances offload local commits
# to a sync/<host>/<ts> branch + PR, then return main to origin/main (never write main direct).
#
# Env escapes (mirror the existing hooks):
#   FEDERATION_OVERRIDE=1   skip role gating, treat as manager (Edwin / emergency)
#   FEDERATION_MANAGER=1    force manager role on this node
#   PTAH_SYNC_DRYRUN=1      classify + log only; perform NO ref-moving / push / PR / stash
#   PTAH_SYNC_REPOS="a b"   override the repo list (space-separated abs paths)
#   PTAH_SYNC_SOLO_REPOS="eva-discord ..."  basenames treated as solo (direct ff-push); default: eva-discord
#   PTAH_SYNC_LOG=/path     override the log file
#
set -u

# ---------------------------------------------------------------------------
# Exit/lock safety. trap guarantees the "always exit 0" contract even if a
# `set -u` unbound var or any unexpected error fires mid-run (the bash-3.2
# empty-array trap the original tripped on). Also releases any repo locks.
# ---------------------------------------------------------------------------
LOCKS=""
_cleanup() { local d; for d in $LOCKS; do rm -rf "$d" 2>/dev/null || true; done; }
trap '_cleanup; exit 0' EXIT

DRY="${PTAH_SYNC_DRYRUN:-0}"

# ---------------------------------------------------------------------------
# Resolve self + federation lib (works whether run from cron, launchd, or hook).
# ---------------------------------------------------------------------------
SELF="$(cd "$(dirname "$0")" && pwd)/$(basename "$0")"
HOOKS_DIR="$(dirname "$SELF")"
# shellcheck source=/dev/null
if [ -f "$HOOKS_DIR/federation-lib.sh" ]; then
  . "$HOOKS_DIR/federation-lib.sh"
else
  # Degrade gracefully if run outside the repo tree: assume contributing instance.
  fed_is_manager() { [ "${FEDERATION_MANAGER:-0}" = "1" ] || [ "${FEDERATION_OVERRIDE:-0}" = "1" ]; }
  fed_hostname() { hostname 2>/dev/null | tr '[:upper:]' '[:lower:]'; }
  fed_red()    { printf '%s\n' "$1" >&2; }
fi
command -v fed_red >/dev/null 2>&1 || fed_red() { printf '%s\n' "$1" >&2; }

HOST="$(fed_hostname)"
NOW_ISO="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
TS_SAFE="$(date -u +%Y%m%dT%H%M%SZ)"
UNIQ="${TS_SAFE}-$$"          # PID suffix kills same-second branch-name collisions
BRANCH="${FEDERATION_PROTECTED_BRANCH:-main}"

# ---------------------------------------------------------------------------
# Repo list. Per-device: headless boxes keep eva-discord as a SIBLING dir.
# ---------------------------------------------------------------------------
default_repos() {
  local tgaotu
  tgaotu="$(cd "$HOOKS_DIR/../.." && pwd)"     # factory/hooks -> repo root
  printf '%s\n' "$tgaotu"
  if [ -d "$tgaotu/eva-discord/.git" ]; then
    printf '%s\n' "$tgaotu/eva-discord"
  elif [ -d "$(dirname "$tgaotu")/eva-discord/.git" ]; then
    printf '%s\n' "$(dirname "$tgaotu")/eva-discord"
  fi
}

if [ -n "${PTAH_SYNC_REPOS:-}" ]; then
  # shellcheck disable=SC2206
  REPOS=( $PTAH_SYNC_REPOS )
else
  # shellcheck disable=SC2207
  REPOS=( $(default_repos) )
fi

# ---------------------------------------------------------------------------
# Logging + summary + alerting.
# ---------------------------------------------------------------------------
log_line() {  # repo state extra
  local repo="$1" state="$2" extra="${3:-}"
  local logfile
  if [ -n "${PTAH_SYNC_LOG:-}" ]; then
    logfile="$PTAH_SYNC_LOG"
  elif [ -d "$repo/.remember" ]; then
    mkdir -p "$repo/.remember/logs" 2>/dev/null || true
    logfile="$repo/.remember/logs/ptah-sync-$(date -u +%Y-%m-%d).log"
  else
    logfile="${TMPDIR:-/tmp}/ptah-sync-$(date -u +%Y-%m-%d).log"
  fi
  printf '%s\thost=%s\trepo=%s\tbranch=%s\tstate=%s\t%s\n' \
    "$NOW_ISO" "$HOST" "$(basename "$repo")" "$BRANCH" "$state" "$extra" >> "$logfile" 2>/dev/null || true
}

SUMMARY=""
BLOCKED_REPOS=""
CUR_REPO_BLOCKED=0
add_summary() { SUMMARY="${SUMMARY}\n  $1"; }

alert() {  # repo message
  local repo="$1" msg="$2"
  CUR_REPO_BLOCKED=1
  fed_red "PTAH-SYNC BLOCKED [$(basename "$repo")]: $msg"
  log_line "$repo" "BLOCKED-NEEDS-HUMAN" "msg=$msg"
  if command -v osascript >/dev/null 2>&1; then
    osascript -e "display notification \"$(basename "$repo"): $msg\" with title \"Ptah sync BLOCKED\"" >/dev/null 2>&1 || true
  fi
  command -v maat_notification_send >/dev/null 2>&1 && \
    maat_notification_send "Ptah sync BLOCKED [$(basename "$repo")]: $msg" >/dev/null 2>&1 || true
  BLOCKED_REPOS="${BLOCKED_REPOS} $(basename "$repo")"
}

# Derive owner/repo slug for gh from the origin URL (https or ssh).
gh_repo_slug() {
  local url; url="$(git -C "$1" remote get-url origin 2>/dev/null)"
  printf '%s' "$url" | sed -E 's#(git@github.com:|https://github.com/)##; s#\.git$##'
}

# Solo repos ff-push main directly (no PR dance) regardless of host role.
is_solo_repo() {  # repo
  local base; base="$(basename "$1")"
  case " ${PTAH_SYNC_SOLO_REPOS:-eva-discord} " in *" $base "*) return 0;; esac
  [ -f "$1/.git/ptah-solo" ] && return 0
  return 1
}

# Surface any leftover ptah-sync autostash entries so orphaned work can never hide.
warn_orphan_stashes() {  # repo
  local repo="$1" n
  n="$(git -C "$repo" stash list 2>/dev/null | grep -c 'ptah-sync autostash' || true)"
  if [ "${n:-0}" -gt 0 ]; then
    add_summary "$(basename "$repo"): NOTE — $n ptah-sync stash(es) present. Recover: git -C \"$repo\" stash pop"
    log_line "$repo" "STASH-PRESENT" "count=$n"
  fi
}

# ---------------------------------------------------------------------------
# DRYRUN: read-only classification. Mutates NOTHING (no stash/switch/push).
# ---------------------------------------------------------------------------
dryrun_report() {  # repo
  local repo="$1"; local g; g=(git -C "$repo")
  "${g[@]}" fetch --prune --tags origin >/dev/null 2>&1 || { add_summary "$(basename "$repo"): OFFLINE [DRYRUN]"; return 0; }
  local dirty=""; [ -n "$("${g[@]}" status --porcelain 2>/dev/null)" ] && dirty=" +dirty"
  if ! "${g[@]}" symbolic-ref --quiet HEAD >/dev/null 2>&1; then
    local n; n="$("${g[@]}" rev-list --count "origin/$BRANCH..HEAD" 2>/dev/null || echo '?')"
    add_summary "$(basename "$repo"): DETACHED, $n commit(s) ahead of canon — would rescue+switch [DRYRUN]$dirty"; return 0
  fi
  local cur; cur="$("${g[@]}" rev-parse --abbrev-ref HEAD 2>/dev/null)"
  if [ "$cur" != "$BRANCH" ]; then
    add_summary "$(basename "$repo"): on '$cur' (not $BRANCH) — would back up, not merge [DRYRUN]$dirty"; return 0
  fi
  local L R B state
  L="$("${g[@]}" rev-parse "$BRANCH" 2>/dev/null)"; R="$("${g[@]}" rev-parse "origin/$BRANCH" 2>/dev/null)"
  B="$("${g[@]}" merge-base "$BRANCH" "origin/$BRANCH" 2>/dev/null)"
  if   [ "$L" = "$R" ]; then state="UP-TO-DATE"
  elif [ "$L" = "$B" ]; then state="BEHIND"
  elif [ "$R" = "$B" ]; then state="AHEAD"
  else                       state="DIVERGED"; fi
  local counts; counts="$("${g[@]}" rev-list --left-right --count "${BRANCH}...origin/${BRANCH}" 2>/dev/null)"
  add_summary "$(basename "$repo"): $state ($counts ahead/behind) [DRYRUN]$dirty"
  log_line "$repo" "$state" "dryrun=1 counts=$counts"
}

# ---------------------------------------------------------------------------
# Per-repo sync.
# ---------------------------------------------------------------------------
sync_repo() {
  local repo="$1"
  local g; g=(git -C "$repo")
  CUR_REPO_BLOCKED=0

  # STEP 0 — preconditions ---------------------------------------------------
  if [ ! -e "$repo/.git" ]; then
    add_summary "$(basename "$repo"): SKIP (not a git repo)"; log_line "$repo" "SKIP" "reason=not_a_repo"; return 0
  fi
  if ! "${g[@]}" remote get-url origin >/dev/null 2>&1; then
    add_summary "$(basename "$repo"): SKIP (no origin remote)"; log_line "$repo" "SKIP" "reason=no_origin"; return 0
  fi

  if [ "$DRY" = "1" ]; then dryrun_report "$repo"; return 0; fi

  # Concurrency lock (portable mkdir-atomic; steals a dead lock).
  local gitdir lockdir
  gitdir="$("${g[@]}" rev-parse --absolute-git-dir 2>/dev/null || echo "$repo/.git")"
  lockdir="$gitdir/ptah-sync.lock.d"
  if ! mkdir "$lockdir" 2>/dev/null; then
    local lpid; lpid="$(cat "$lockdir/pid" 2>/dev/null || echo '')"
    if [ -n "$lpid" ] && ! kill -0 "$lpid" 2>/dev/null; then
      rm -rf "$lockdir" 2>/dev/null || true; mkdir "$lockdir" 2>/dev/null || true
    fi
    if [ ! -d "$lockdir" ] || ! printf '%s' "$$" > "$lockdir/pid" 2>/dev/null; then
      add_summary "$(basename "$repo"): SKIP (another ptah-sync holds the lock)"; log_line "$repo" "SKIP" "reason=locked"; return 0
    fi
  fi
  printf '%s' "$$" > "$lockdir/pid" 2>/dev/null || true
  LOCKS="$LOCKS $lockdir"

  # In-progress git operation? Never stash/rebase under a live rebase/merge/cherry-pick.
  if [ -d "$gitdir/rebase-merge" ] || [ -d "$gitdir/rebase-apply" ] || \
     [ -f "$gitdir/MERGE_HEAD" ] || [ -f "$gitdir/CHERRY_PICK_HEAD" ] || [ -f "$gitdir/sequencer/todo" ]; then
    add_summary "$(basename "$repo"): SKIP (git operation in progress — left untouched)"
    log_line "$repo" "SKIP" "reason=op_in_progress"; return 0
  fi

  # STEP 0a — detached HEAD: RESCUE any unpushed commits before switching.
  if ! "${g[@]}" symbolic-ref --quiet HEAD >/dev/null 2>&1; then
    local dhead; dhead="$("${g[@]}" rev-parse HEAD 2>/dev/null)"
    "${g[@]}" fetch --prune origin >/dev/null 2>&1 || true
    local unreach; unreach="$("${g[@]}" rev-list --count "origin/$BRANCH..$dhead" 2>/dev/null || echo 0)"
    if [ "${unreach:-0}" != "0" ]; then
      local rb="sync/${HOST}/${UNIQ}-detached"
      if "${g[@]}" branch -f "$rb" "$dhead" >/dev/null 2>&1 && "${g[@]}" push -u origin "$rb" >/dev/null 2>&1; then
        add_summary "$(basename "$repo"): DETACHED had $unreach commit(s) — rescued to origin/$rb"
        log_line "$repo" "RESCUE-DETACHED" "branch=$rb commits=$unreach sha=$dhead"
      else
        alert "$repo" "detached HEAD with $unreach unpushed commit(s) at ${dhead:0:8} — rescue push failed; NOT switching"
        return 0
      fi
    fi
    if "${g[@]}" switch "$BRANCH" >/dev/null 2>&1 || "${g[@]}" checkout "$BRANCH" >/dev/null 2>&1; then
      log_line "$repo" "RECOVER" "from=detached to=$BRANCH"
    else
      alert "$repo" "detached HEAD and cannot switch to $BRANCH (dirty tree?)"; return 0
    fi
  fi

  # STEP 0b — on a non-main branch: NEVER auto-merge, but BACK UP unpushed commits.
  local cur; cur="$("${g[@]}" rev-parse --abbrev-ref HEAD 2>/dev/null)"
  if [ "$cur" != "$BRANCH" ]; then
    "${g[@]}" fetch --prune origin >/dev/null 2>&1 || true
    if "${g[@]}" rev-parse --abbrev-ref "${cur}@{u}" >/dev/null 2>&1; then
      local unpushed; unpushed="$("${g[@]}" rev-list --count "${cur}@{u}..${cur}" 2>/dev/null || echo 0)"
      if [ "${unpushed:-0}" != "0" ]; then
        if "${g[@]}" push >/dev/null 2>&1; then
          add_summary "$(basename "$repo"): on '$cur' — pushed $unpushed commit(s) to its upstream (not merged to $BRANCH)"
          log_line "$repo" "BRANCH-PUSH" "branch=$cur n=$unpushed"
        else
          alert "$repo" "on '$cur' with $unpushed unpushed commit(s); push to upstream failed"
        fi
      else
        add_summary "$(basename "$repo"): SKIP (on '$cur', up-to-date with upstream — left untouched)"
        log_line "$repo" "SKIP" "reason=not_on_${BRANCH} cur=$cur"
      fi
    else
      local mb="sync/${HOST}/${cur}"
      if "${g[@]}" push -u origin "${cur}:${mb}" >/dev/null 2>&1; then
        add_summary "$(basename "$repo"): on '$cur' (no upstream) — backed up to origin/$mb (not merged)"
        log_line "$repo" "BRANCH-BACKUP" "cur=$cur mirror=$mb"
      else
        add_summary "$(basename "$repo"): SKIP (on '$cur', no upstream, backup failed — left untouched)"
        log_line "$repo" "SKIP" "reason=not_on_${BRANCH} cur=$cur backup=failed"
      fi
    fi
    return 0
  fi

  # I2 — ensure main tracks origin/main.
  if ! "${g[@]}" rev-parse --abbrev-ref "${BRANCH}@{u}" >/dev/null 2>&1; then
    "${g[@]}" branch --set-upstream-to="origin/$BRANCH" "$BRANCH" >/dev/null 2>&1 || true
  fi

  # STEP 1 — snapshot (reversible by a human via reflog).
  local pre_head; pre_head="$("${g[@]}" rev-parse HEAD 2>/dev/null)"
  log_line "$repo" "SNAPSHOT" "head=$pre_head"

  # STEP 2 — dirty-tree handling. Stash (incl. untracked) before any ref move.
  local stashed=0
  if [ -n "$("${g[@]}" status --porcelain 2>/dev/null)" ]; then
    if "${g[@]}" stash push --include-untracked -m "ptah-sync autostash $NOW_ISO" >/dev/null 2>&1; then
      stashed=1; log_line "$repo" "STASH" "msg=ptah-sync autostash $NOW_ISO"
    else
      alert "$repo" "working tree dirty and stash failed — refusing to move refs"; return 0
    fi
  fi

  # STEP 3 — fetch (the ONLY network call in the common path). Offline => restore + skip.
  if ! "${g[@]}" fetch --prune --tags origin >/dev/null 2>&1; then
    [ "$stashed" = 1 ] && "${g[@]}" stash pop >/dev/null 2>&1 || true
    add_summary "$(basename "$repo"): OFFLINE (fetch failed — left as-is)"
    log_line "$repo" "OFFLINE" "reason=fetch_failed"; return 0
  fi

  # STEP 4 — classify (network-free triad).
  local L R B
  L="$("${g[@]}" rev-parse "$BRANCH" 2>/dev/null)"
  R="$("${g[@]}" rev-parse "origin/$BRANCH" 2>/dev/null)"
  B="$("${g[@]}" merge-base "$BRANCH" "origin/$BRANCH" 2>/dev/null)"
  local counts ahead behind
  counts="$("${g[@]}" rev-list --left-right --count "${BRANCH}...origin/${BRANCH}" 2>/dev/null)"
  ahead="$(printf '%s' "$counts" | awk '{print $1}')"
  behind="$(printf '%s' "$counts" | awk '{print $2}')"

  local state
  if   [ "$L" = "$R" ]; then state="UP-TO-DATE"
  elif [ "$L" = "$B" ]; then state="BEHIND"
  elif [ "$R" = "$B" ]; then state="AHEAD"
  else                       state="DIVERGED"; fi

  # STEP 5 — act per state. (Tree is already CLEAN here if it was dirty: STEP 2 stashed it.)
  case "$state" in
    UP-TO-DATE)
      : ;;
    BEHIND)
      if ! "${g[@]}" merge --ff-only "origin/$BRANCH" >/dev/null 2>&1; then
        "${g[@]}" fetch --prune origin >/dev/null 2>&1 || true
        "${g[@]}" merge --ff-only "origin/$BRANCH" >/dev/null 2>&1 || {
          [ "$stashed" = 1 ] && "${g[@]}" stash pop >/dev/null 2>&1 || true
          alert "$repo" "ff-only failed twice (concurrent push?) — left at ${pre_head:0:8}"; return 0
        }
      fi
      log_line "$repo" "FF" "from=$pre_head to=$R behind=$behind" ;;
    AHEAD)
      ahead_push "$repo" ;;
    DIVERGED)
      # MJP-01 core: rebase local commits ONTO canon (linear history, no fork).
      # Tree is clean (STEP 2 stashed), so no --autostash needed here.
      if "${g[@]}" rebase "origin/$BRANCH" >/dev/null 2>&1; then
        log_line "$repo" "REBASE" "onto=$R replayed=$ahead"
        ahead_push "$repo"
      else
        local conflicts
        conflicts="$("${g[@]}" diff --name-only --diff-filter=U 2>/dev/null | tr '\n' ',' )"
        "${g[@]}" rebase --abort >/dev/null 2>&1 || true
        alert "$repo" "rebase conflict on [$conflicts] local=${L:0:8} remote=${R:0:8} — aborted, no push"
        add_summary "$(basename "$repo"): DIVERGED-CONFLICT (BLOCKED, local commit + stash preserved)"
        warn_orphan_stashes "$repo"
        return 0
      fi ;;
  esac

  # STEP 6 — restore the step-2 stash on EVERY non-conflict path (incl. DIVERGED-success).
  if [ "$stashed" = 1 ]; then
    if ! "${g[@]}" stash pop >/dev/null 2>&1; then
      alert "$repo" "stash pop conflicted — tree has markers, named stash retained (git stash list)"
      add_summary "$(basename "$repo"): $state then STASH-CONFLICT (BLOCKED, stash kept)"
      return 0
    fi
  fi

  # If a sub-step (ahead_push) blocked this repo, do not claim OK.
  if [ "$CUR_REPO_BLOCKED" = "1" ]; then warn_orphan_stashes "$repo"; return 0; fi

  # STEP 7 — invariant assert: branch is main AND HEAD == origin/main (truth reached).
  if [ "$("${g[@]}" rev-parse --abbrev-ref HEAD)" != "$BRANCH" ]; then
    alert "$repo" "post-sync not on $BRANCH (invariant violated)"; return 0
  fi
  local post upstream; post="$("${g[@]}" rev-parse HEAD 2>/dev/null)"; upstream="$("${g[@]}" rev-parse "origin/$BRANCH" 2>/dev/null)"
  if [ "$post" != "$upstream" ]; then
    alert "$repo" "post-sync HEAD ${post:0:8} != origin/$BRANCH ${upstream:0:8} (NOT reconciled)"; return 0
  fi
  add_summary "$(basename "$repo"): $state OK (ahead=$ahead behind=$behind head=${post:0:8})"
  log_line "$repo" "OK" "final=$state head=$post"
}

# ahead_push — role-gated. Manager / SOLO repo ff-pushes main; contributor offloads to PR.
ahead_push() {
  local repo="$1"
  local g; g=(git -C "$repo")
  local L R B; L="$("${g[@]}" rev-parse "$BRANCH")"; R="$("${g[@]}" rev-parse "origin/$BRANCH")"
  B="$("${g[@]}" merge-base "$BRANCH" "origin/$BRANCH")"
  [ "$L" = "$R" ] && return 0                 # nothing to push
  [ "$R" != "$B" ] && return 0                # not strictly ahead -> caller re-handles

  if fed_is_manager || [ "${FEDERATION_OVERRIDE:-0}" = "1" ] || is_solo_repo "$repo"; then
    if "${g[@]}" push origin "$BRANCH" >/dev/null 2>&1; then
      log_line "$repo" "PUSH-FF" "to=origin/$BRANCH"
    else
      "${g[@]}" fetch --prune origin >/dev/null 2>&1 || true
      if "${g[@]}" rebase "origin/$BRANCH" >/dev/null 2>&1 && \
         "${g[@]}" push origin "$BRANCH" >/dev/null 2>&1; then
        log_line "$repo" "PUSH-FF" "to=origin/$BRANCH (after re-rebase)"
      else
        "${g[@]}" rebase --abort >/dev/null 2>&1 || true
        alert "$repo" "manager/solo ff-push rejected and re-rebase failed — local commits retained"
      fi
    fi
  else
    # Contributing instance: NEVER write main. Offload to a named branch + PR.
    local sb="sync/${HOST}/${UNIQ}"
    "${g[@]}" branch -f "$sb" "$BRANCH" >/dev/null 2>&1
    if "${g[@]}" push -u origin "$sb" >/dev/null 2>&1; then
      log_line "$repo" "PUSH-BRANCH" "branch=$sb"
      local pr_made=0
      if command -v gh >/dev/null 2>&1; then
        if gh -R "$(gh_repo_slug "$repo")" pr create --base "$BRANCH" --head "$sb" \
             --title "sync: ${HOST} local commits @ ${NOW_ISO}" \
             --body "Auto-offloaded by ptah-sync (Distributed MJP-01) from contributing instance \`${HOST}\`. Local commits that were ahead of origin/${BRANCH}. Review + squash-merge." \
             >/dev/null 2>&1; then pr_made=1; fi
      fi
      if [ "$pr_made" = "1" ]; then
        log_line "$repo" "PR-OPENED" "head=$sb"
      else
        # gh missing/unauth/PR-exists: work is SAFE on the branch but NOT visible as a PR.
        add_summary "$(basename "$repo"): offloaded to origin/$sb but NO PR opened (gh missing/unauth) — open it manually"
        log_line "$repo" "PUSH-BRANCH-NO-PR" "head=$sb"
      fi
      # Return local main to canon. Capture status — never swallow with `|| true`.
      if "${g[@]}" reset --keep "origin/$BRANCH" >/dev/null 2>&1 || \
         "${g[@]}" merge --ff-only "origin/$BRANCH" >/dev/null 2>&1; then
        log_line "$repo" "RESET-TO-CANON" "main=origin/$BRANCH offloaded=$sb"
      else
        alert "$repo" "offloaded to $sb (safe) but could NOT reset main to canon — main still ahead; resolve manually"
      fi
    else
      alert "$repo" "contributor could not push offload branch $sb — local commits retained"
    fi
  fi
}

# ---------------------------------------------------------------------------
# Drive all repos. The bash-3.2 empty-array guard + EXIT trap guarantee exit 0.
# ---------------------------------------------------------------------------
if [ "${#REPOS[@]}" -gt 0 ]; then
  for r in "${REPOS[@]}"; do
    sync_repo "$r"
  done
else
  add_summary "(no repos resolved — nothing to sync)"
fi

printf '=== PTAH SYNC === Distributed MJP-01 (%s @ %s)' "$HOST" "$NOW_ISO"
printf '%b\n' "$SUMMARY"
if [ -n "$BLOCKED_REPOS" ]; then
  printf '  !! BLOCKED-NEEDS-HUMAN:%s — resolve before relying on these repos.\n' "$BLOCKED_REPOS"
fi

exit 0
