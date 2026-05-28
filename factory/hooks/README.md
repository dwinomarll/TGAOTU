# Federation Protocol — Enforcement Hooks

Git hooks that make `org/FEDERATION_SOP.md` real instead of honor-system. They turn the
2026-05-27 collision into something git itself refuses to repeat.

## What they enforce

| Hook | Rule | Behavior |
|---|---|---|
| `pre-commit` | **F3** | A *contributing instance* committing to the protected branch (`main`) is **blocked**. |
| `pre-commit` | **F2** | If nothing is claimed in the work registry, prints a **nudge** (does not block). |
| `pre-push` | **F3** | A *contributing instance* pushing to `main` is **blocked** (branch + PR instead). |
| `pre-push` | **F4** | A non-fast-forward (force) push over `main` is **blocked** — even for the Manager. |

"Manager of record" vs "contributing instance" is decided by hostname: nodes matching
`FEDERATION_MANAGER_HOSTS` (default `eva jetson`) are the Manager; everything else contributes.

## Install (once per clone, per node)

```bash
bash factory/hooks/install.sh        # sets core.hooksPath → factory/hooks
```

The hook *scripts* travel with the repo (version-controlled here); only the activation
(`core.hooksPath`) is per-clone, so each node arms them once.

## Override (it is a safety net, not a cage)

```bash
FEDERATION_OVERRIDE=1 git commit …   # or git push …
git commit --no-verify               # native git bypass
```

Edwin, or any node in a genuine emergency, can always override.

## Test

```bash
bash factory/hooks/test-hooks.sh     # 9 simulated scenarios, asserts every exit code
```

## Config (env, all optional)

| Var | Default | Meaning |
|---|---|---|
| `FEDERATION_MANAGER_HOSTS` | `eva jetson` | hostname prefixes that ARE the Manager of record |
| `FEDERATION_PROTECTED_BRANCH` | `main` | the branch only the Manager may write |
| `FEDERATION_MANAGER` | unset | `1` forces this node to be treated as the Manager |
| `FEDERATION_OVERRIDE` | unset | `1` bypasses all checks |
| `FEDERATION_BRANCH_OVERRIDE` | unset | test seam: pretend the current branch is this value |

## Known limits (v1)

- **F2 is a nudge, not a block.** A pre-commit hook can't reliably tie a commit to a specific
  registry claim (no session handle), so it warns when *nothing* is claimed rather than
  false-blocking. Session-accurate claim matching is a future enhancement.
- Installed here for the `TGAOTU` repo. Porting to `eva-workspace` (the other shared repo)
  is the natural next step, deliberately deferred to avoid touching the most collision-prone
  Manager-owned tree without review.
