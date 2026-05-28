#!/usr/bin/env bash
# Federation Protocol enforcement — shared helpers.
# Sourced by pre-commit and pre-push. See org/FEDERATION_SOP.md (F1–F5).
#
# Config (all overridable by env, so the hook is a safety net, not a cage):
#   FEDERATION_MANAGER_HOSTS   space-separated hostname prefixes that ARE the Manager of record
#                              (default: "eva jetson")
#   FEDERATION_PROTECTED_BRANCH the branch only the Manager of record may write (default: "main")
#   FEDERATION_MANAGER=1        force this node to be treated as the Manager of record
#   FEDERATION_OVERRIDE=1       bypass ALL federation checks (Edwin / emergency)
#   FEDERATION_BRANCH_OVERRIDE  test seam: pretend the current branch is this value

: "${FEDERATION_MANAGER_HOSTS:=eva jetson}"
: "${FEDERATION_PROTECTED_BRANCH:=main}"
: "${FEDERATION_BRANCH_OVERRIDE:=}"

fed_hostname() { hostname 2>/dev/null | tr '[:upper:]' '[:lower:]'; }

# 0 = this node is the Manager of record; 1 = contributing instance.
fed_is_manager() {
  [ "${FEDERATION_MANAGER:-0}" = "1" ] && return 0
  local h p
  h="$(fed_hostname)"
  for p in $FEDERATION_MANAGER_HOSTS; do
    case "$h" in
      "$p" | "$p"*) return 0 ;;
    esac
  done
  return 1
}

fed_protected_branch() { printf '%s' "$FEDERATION_PROTECTED_BRANCH"; }

fed_current_branch() {
  [ -n "$FEDERATION_BRANCH_OVERRIDE" ] && { printf '%s' "$FEDERATION_BRANCH_OVERRIDE"; return 0; }
  git rev-parse --abbrev-ref HEAD 2>/dev/null
}

# Best-effort location of the shared work registry across nodes.
fed_registry_path() {
  local p
  for p in "$HOME/eva-workspace/memory/work_registry.json" \
           "/home/jetson/eva-workspace/memory/work_registry.json" \
           "/Users/edwinrosa/eva-workspace/memory/work_registry.json"; do
    [ -f "$p" ] && { printf '%s' "$p"; return 0; }
  done
  return 1
}

# 0 = at least one active claim exists; 1 = none active; 2 = registry unreadable.
fed_active_claim_state() {
  local reg
  reg="$(fed_registry_path)" || return 2
  python3 - "$reg" <<'PY' 2>/dev/null
import json, sys
try:
    d = json.load(open(sys.argv[1]))
    sys.exit(0 if d.get("active") else 1)
except Exception:
    sys.exit(2)
PY
}

fed_red()    { printf '\033[31m%s\033[0m\n' "$1" >&2; }
fed_yellow() { printf '\033[33m%s\033[0m\n' "$1" >&2; }
fed_green()  { printf '\033[32m%s\033[0m\n' "$1" >&2; }
