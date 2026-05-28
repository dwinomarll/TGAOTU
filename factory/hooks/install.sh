#!/usr/bin/env bash
# Arm the Federation Protocol git hooks for this clone.
# The hook scripts are version-controlled in factory/hooks/; this points git at them.
# Run once per clone, per node. See org/FEDERATION_SOP.md.
set -euo pipefail

REPO="$(git rev-parse --show-toplevel)"
cd "$REPO"

chmod +x factory/hooks/pre-commit factory/hooks/pre-push factory/hooks/install.sh factory/hooks/test-hooks.sh 2>/dev/null || true
git config core.hooksPath factory/hooks

# shellcheck source=/dev/null
. factory/hooks/federation-lib.sh

if fed_is_manager; then role="MANAGER of record"; else role="contributing instance"; fi

echo "✓ Federation hooks armed (core.hooksPath = factory/hooks)"
echo "  This node ($(fed_hostname)): $role"
echo "  Protected branch: $(fed_protected_branch)"
echo "  Override anytime:  FEDERATION_OVERRIDE=1 <git cmd>   or   --no-verify"
echo "  Uninstall:         git config --unset core.hooksPath"
