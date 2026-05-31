#!/bin/bash
# test-ptah-sync.sh — bare-origin verification harness for ptah-sync.sh (Distributed MJP-01).
# Runs every reconcile path on /bin/bash (3.2) against a throwaway bare origin.
# Exits non-zero if any assertion fails. Touches NO real repo (always sets PTAH_SYNC_REPOS).
set -u
SCRIPT="$(cd "$(dirname "$0")" && pwd)/ptah-sync.sh"
ROOT="$(mktemp -d)"; STUB="$ROOT/stub"; mkdir -p "$STUB"
# gh stub: present but always fails -> deterministic NO-PR path, no network.
printf '#!/bin/sh\nexit 1\n' > "$STUB/gh"; chmod +x "$STUB/gh"
PASS=0; FAIL=0
ok(){ printf '  \033[32mPASS\033[0m %s\n' "$1"; PASS=$((PASS+1)); }
bad(){ printf '  \033[31mFAIL\033[0m %s\n' "$1"; FAIL=$((FAIL+1)); }
ck(){ if eval "$2"; then ok "$1"; else bad "$1 [$2]"; fi; }

gc(){ git -C "$1" -c user.email=t@t -c user.name=t "${@:2}"; }
new_origin(){ # dir
  local d="$1"; git init -q --bare "$d/origin.git"
  git clone -q "$d/origin.git" "$d/seed" 2>/dev/null
  gc "$d/seed" checkout -q -b main 2>/dev/null
  echo base > "$d/seed/file.txt"; gc "$d/seed" add .; gc "$d/seed" commit -q -m base
  gc "$d/seed" push -q -u origin main 2>/dev/null
  git -C "$d/origin.git" symbolic-ref HEAD refs/heads/main
}
clone_work(){ git clone -q "$1/origin.git" "$2" 2>/dev/null; git -C "$2" config user.email t@t; git -C "$2" config user.name t; }
run(){ # work extra-env...   (default = contributor on a non-manager host)
  # Log OUTSIDE the repo (production writes to gitignored .remember/logs); a log
  # inside the worktree would itself dirty the tree and get stashed.
  local work="$1"; shift
  env FEDERATION_MANAGER_HOSTS=zzz PATH="$STUB:$PATH" PTAH_SYNC_LOG="${work}.synclog" "$@" \
      PTAH_SYNC_REPOS="$work" /bin/bash "$SCRIPT" 2>"${work}.err"
}
oref(){ git -C "$1/origin.git" rev-parse "$2" 2>/dev/null; }    # origin ref sha
href(){ git -C "$1" rev-parse HEAD 2>/dev/null; }
osync(){ git -C "$1/origin.git" for-each-ref --format='%(refname)' refs/heads/sync 2>/dev/null; }

T(){ printf '\033[1m%s\033[0m\n' "$1"; }

# ── T1 UP-TO-DATE ───────────────────────────────────────────────────────────
T "T1 UP-TO-DATE"; D="$ROOT/t1"; mkdir -p "$D"; new_origin "$D"; clone_work "$D" "$D/w"
out="$(run "$D/w")"
ck "stays at canon" "[ '$(href "$D/w")' = '$(oref "$D" main)' ]"
ck "reports OK"     "printf '%s' \"\$out\" | grep -q 'UP-TO-DATE OK'"

# ── T2 BEHIND -> fast-forward ───────────────────────────────────────────────
T "T2 BEHIND"; D="$ROOT/t2"; mkdir -p "$D"; new_origin "$D"; clone_work "$D" "$D/w"
gc "$D/seed" commit -q --allow-empty -m adv; gc "$D/seed" push -q
out="$(run "$D/w")"
ck "ff'd to canon"  "[ '$(href "$D/w")' = '$(oref "$D" main)' ]"
ck "logged FF"      "grep -q 'state=FF' "$D/w.synclog""

# ── T3 AHEAD as manager -> ff-push ──────────────────────────────────────────
T "T3 AHEAD (manager)"; D="$ROOT/t3"; mkdir -p "$D"; new_origin "$D"; clone_work "$D" "$D/w"
gc "$D/w" commit -q --allow-empty -m local-mgr; WH="$(href "$D/w")"
out="$(run "$D/w" FEDERATION_OVERRIDE=1)"
ck "origin advanced to local" "[ '$(oref "$D" main)' = '$WH' ]"
ck "HEAD == origin"           "[ '$(href "$D/w")' = '$(oref "$D" main)' ]"
ck "logged PUSH-FF"           "grep -q 'PUSH-FF' "$D/w.synclog""

# ── T4 AHEAD as contributor -> offload branch + reset to canon ──────────────
T "T4 AHEAD (contributor)"; D="$ROOT/t4"; mkdir -p "$D"; new_origin "$D"; base="$(oref "$D" main)"
clone_work "$D" "$D/w"; gc "$D/w" commit -q --allow-empty -m local-contrib
out="$(run "$D/w")"
ck "origin main UNCHANGED"   "[ '$(oref "$D" main)' = '$base' ]"
ck "offload sync/ branch"    "[ -n '$(osync "$D")' ]"
ck "local reset to canon"    "[ '$(href "$D/w")' = '$base' ]"
ck "logged RESET-TO-CANON"   "grep -q 'RESET-TO-CANON' "$D/w.synclog""
ck "logged NO-PR (gh stub)"  "grep -q 'PUSH-BRANCH-NO-PR' "$D/w.synclog""

# ── T5 DIVERGED clean -> rebase (linear) then push ──────────────────────────
T "T5 DIVERGED clean (manager)"; D="$ROOT/t5"; mkdir -p "$D"; new_origin "$D"; clone_work "$D" "$D/w"
echo o > "$D/seed/o.txt"; gc "$D/seed" add .; gc "$D/seed" commit -q -m originA; gc "$D/seed" push -q
echo w > "$D/w/w.txt"; gc "$D/w" add .; gc "$D/w" commit -q -m localB
out="$(run "$D/w" FEDERATION_OVERRIDE=1)"
ck "HEAD == origin"          "[ '$(href "$D/w")' = '$(oref "$D" main)' ]"
ck "history is LINEAR"       "[ -z \"\$(git -C '$D/origin.git' log --merges --format=%H main)\" ]"
ck "both commits present"    "git -C '$D/w' log --format=%s | grep -q originA && git -C '$D/w' log --format=%s | grep -q localB"

# ── T6 DIVERGED + DIRTY (regression: orphaned step-2 stash) ─────────────────
T "T6 DIVERGED + dirty (orphan-stash regression)"; D="$ROOT/t6"; mkdir -p "$D"; new_origin "$D"; clone_work "$D" "$D/w"
echo o > "$D/seed/o.txt"; gc "$D/seed" add .; gc "$D/seed" commit -q -m originA; gc "$D/seed" push -q
echo w > "$D/w/w.txt"; gc "$D/w" add .; gc "$D/w" commit -q -m localB
echo UNCOMMITTED > "$D/w/dirty_untracked.txt"          # the work that must NOT vanish
out="$(run "$D/w" FEDERATION_OVERRIDE=1)"
ck "uncommitted work RESTORED" "[ -f '$D/w/dirty_untracked.txt' ]"
ck "NO orphaned ptah stash"    "[ \"\$(git -C '$D/w' stash list | grep -c ptah-sync)\" = '0' ]"
ck "HEAD == origin"            "[ '$(href "$D/w")' = '$(oref "$D" main)' ]"

# ── T7 DIVERGED conflict -> abort, preserve, BLOCK ──────────────────────────
T "T7 DIVERGED conflict"; D="$ROOT/t7"; mkdir -p "$D"; new_origin "$D"; clone_work "$D" "$D/w"
echo ORIGIN > "$D/seed/file.txt"; gc "$D/seed" add .; gc "$D/seed" commit -q -m originEdit; gc "$D/seed" push -q
echo WORK   > "$D/w/file.txt";    gc "$D/w" add .;    gc "$D/w" commit -q -m workEdit; WB="$(href "$D/w")"
out="$(run "$D/w" FEDERATION_OVERRIDE=1)"
ck "local commit PRESERVED"  "[ '$(href "$D/w")' = '$WB' ]"
ck "local content intact"    "[ \"\$(cat '$D/w/file.txt')\" = 'WORK' ]"
ck "origin NOT advanced"     "[ '$(oref "$D" main)' != '$WB' ]"
ck "reported BLOCKED"        "printf '%s' \"\$out\" | grep -q 'BLOCKED-NEEDS-HUMAN'"
ck "no rebase left dangling" "[ ! -d '$D/w/.git/rebase-merge' ] && [ ! -d '$D/w/.git/rebase-apply' ]"

# ── T8 detached HEAD with a commit -> rescue ────────────────────────────────
T "T8 detached HEAD rescue"; D="$ROOT/t8"; mkdir -p "$D"; new_origin "$D"; clone_work "$D" "$D/w"
git -C "$D/w" checkout -q --detach; gc "$D/w" commit -q --allow-empty -m detached-work; DW="$(href "$D/w")"
out="$(run "$D/w")"
ck "rescue branch on origin"  "git -C '$D/origin.git' for-each-ref refs/heads/sync | grep -q detached"
ck "rescued commit pushed"    "git -C '$D/origin.git' branch --contains '$DW' 2>/dev/null | grep -q sync || git -C '$D/origin.git' for-each-ref --format='%(objectname)' 'refs/heads/sync/*' | grep -q '$DW'"
ck "back on main"             "[ '$(git -C "$D/w" rev-parse --abbrev-ref HEAD)' = 'main' ]"

# ── T9 feature branch, unpushed, no upstream -> backup ──────────────────────
T "T9 feature branch backup"; D="$ROOT/t9"; mkdir -p "$D"; new_origin "$D"; clone_work "$D" "$D/w"
git -C "$D/w" checkout -q -b feature/x; gc "$D/w" commit -q --allow-empty -m feat
out="$(run "$D/w")"
ck "feature backed up to origin" "git -C '$D/origin.git' for-each-ref refs/heads/sync | grep -q 'feature/x'"
ck "still on feature branch"     "[ '$(git -C "$D/w" rev-parse --abbrev-ref HEAD)' = 'feature/x' ]"
ck "main NOT touched"            "printf '%s' \"\$out\" | grep -q 'not merged'"

# ── T10 empty REPOS (bash-3.2 contract) ─────────────────────────────────────
T "T10 empty REPOS / exit-0 contract";
env PTAH_SYNC_REPOS=" " PATH="$STUB:$PATH" /bin/bash "$SCRIPT" >"$ROOT/t10.out" 2>"$ROOT/t10.err"; rc=$?
ck "exit 0"                  "[ $rc -eq 0 ]"
ck "no unbound-var crash"    "! grep -q 'unbound variable' '$ROOT/t10.err'"
ck "reports no repos"        "grep -q 'no repos resolved' '$ROOT/t10.out'"

# ── T11 in-progress git op -> SKIP ──────────────────────────────────────────
T "T11 in-progress op guard"; D="$ROOT/t11"; mkdir -p "$D"; new_origin "$D"; clone_work "$D" "$D/w"
gc "$D/w" commit -q --allow-empty -m local; WH="$(href "$D/w")"
echo deadbeef > "$D/w/.git/MERGE_HEAD"
out="$(run "$D/w" FEDERATION_OVERRIDE=1)"
ck "skipped (op in progress)" "printf '%s' \"\$out\" | grep -q 'operation in progress'"
ck "did NOT push"             "[ '$(oref "$D" main)' != '$WH' ]"
rm -f "$D/w/.git/MERGE_HEAD"

# ── T12 solo repo (eva-discord) on a contributor host -> direct ff-push ─────
T "T12 solo repo direct push"; D="$ROOT/t12"; mkdir -p "$D"; new_origin "$D"; clone_work "$D" "$D/eva-discord"
gc "$D/eva-discord" commit -q --allow-empty -m solo-local; SH="$(href "$D/eva-discord")"
out="$(run "$D/eva-discord")"   # contributor host, but basename eva-discord => solo
ck "origin advanced (direct)" "[ '$(oref "$D" main)' = '$SH' ]"
ck "no sync/ offload branch"  "[ -z '$(osync "$D")' ]"
ck "logged PUSH-FF"           "grep -q 'PUSH-FF' "$D/eva-discord.synclog""

# ── summary ─────────────────────────────────────────────────────────────────
printf '\n\033[1m=== %d passed, %d failed ===\033[0m\n' "$PASS" "$FAIL"
rm -rf "$ROOT"
[ "$FAIL" -eq 0 ]
