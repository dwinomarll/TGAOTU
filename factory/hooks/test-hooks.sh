#!/usr/bin/env bash
# Self-test for the Federation Protocol hooks.
# Simulates each scenario and asserts the exit code. No real commits/pushes happen.
# Run from anywhere inside the repo:  bash factory/hooks/test-hooks.sh
set -uo pipefail

REPO="$(git rev-parse --show-toplevel)"; cd "$REPO"
HOOKS="factory/hooks"
NOMATCH="__nomatch__"          # FEDERATION_MANAGER_HOSTS that never matches → forces "contributor"
LOCAL="$(git rev-parse HEAD)"
PARENT="$(git rev-parse HEAD~1)"
PROT="refs/heads/main"
pass=0; fail=0; RC=0

run()     { ( "$@" ) >/dev/null 2>&1; RC=$?; }
runpush() { local line="$1"; shift; ( printf '%s\n' "$line" | "$@" ) >/dev/null 2>&1; RC=$?; }
assert()  {
  if [ "$RC" = "$2" ]; then printf '  \033[32mPASS\033[0m %s (exit %s)\n' "$1" "$RC"; pass=$((pass+1))
  else printf '  \033[31mFAIL\033[0m %s (expected %s, got %s)\n' "$1" "$2" "$RC"; fail=$((fail+1)); fi
}

echo "── pre-commit (F3 block / F2 nudge) ──"
run env FEDERATION_MANAGER_HOSTS="$NOMATCH" FEDERATION_BRANCH_OVERRIDE=main    "$HOOKS/pre-commit"
assert "contributor commit → main is BLOCKED" 1
run env FEDERATION_MANAGER=1                 FEDERATION_BRANCH_OVERRIDE=main    "$HOOKS/pre-commit"
assert "manager   commit → main is ALLOWED" 0
run env FEDERATION_MANAGER_HOSTS="$NOMATCH" FEDERATION_BRANCH_OVERRIDE=feat/x  "$HOOKS/pre-commit"
assert "contributor commit → feature branch is ALLOWED" 0
run env FEDERATION_OVERRIDE=1 FEDERATION_MANAGER_HOSTS="$NOMATCH" FEDERATION_BRANCH_OVERRIDE=main "$HOOKS/pre-commit"
assert "override bypasses the block" 0

echo "── pre-push (F3 + F4) ──"
runpush "$PROT $LOCAL $PROT $PARENT"  env FEDERATION_MANAGER_HOSTS="$NOMATCH" "$HOOKS/pre-push"
assert "contributor push → main is BLOCKED" 1
runpush "$PROT $LOCAL $PROT $PARENT"  env FEDERATION_MANAGER=1 "$HOOKS/pre-push"
assert "manager fast-forward push → main is ALLOWED" 0
runpush "$PROT $PARENT $PROT $LOCAL"  env FEDERATION_MANAGER=1 "$HOOKS/pre-push"
assert "manager non-fast-forward (force) push → main is BLOCKED" 1
runpush "refs/heads/feat $LOCAL refs/heads/feat $PARENT" env FEDERATION_MANAGER_HOSTS="$NOMATCH" "$HOOKS/pre-push"
assert "contributor push → feature branch is ALLOWED" 0
runpush "$PROT $PARENT $PROT $LOCAL"  env FEDERATION_OVERRIDE=1 FEDERATION_MANAGER=1 "$HOOKS/pre-push"
assert "override bypasses the force-push block" 0

echo ""
printf 'RESULT: %s passed, %s failed\n' "$pass" "$fail"
[ "$fail" -eq 0 ]
