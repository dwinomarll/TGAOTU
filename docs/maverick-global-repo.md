# Maverick Global Repo Package

This package prepares Maverick Cockpit for a standalone or global GitHub repo.
It is not a GitHub publish. It is the local, reviewable shape that can be pushed
after the `github_publish` gate is confirmed.

Machine contract:
`factory/active/maverick-cockpit/global-repo/repo-contract.json`

Runner:
`python3 factory/maverick_global_repo.py`

Output:
`factory/active/maverick-cockpit/global-repo/package-manifest.json`

Related confirmation request:
`factory/active/maverick-cockpit/confirmation-request.md`

Local package preview:
`factory/active/maverick-cockpit/global-repo/package/`

Dashboard surface:
The Maverick Cockpit dashboard renders Launch Gates from the local package and
live-target data so publish/export readiness is visible without opening an
external write gate.

GitHub bridge:
`factory/active/maverick-cockpit/github-publish-bridge.json` records the
candidate repo, candidate branch, package evidence, and blocked
`github_publish` dry run. It does not push or open a pull request.

## Package Intent

The package is designed so Maverick can move as one system:

- cockpit dashboard
- normalized case schema
- source map
- adapter snapshot
- write-gate policy
- live-target checklist
- validation scripts

## Publish Boundary

The package may be inspected locally. It may not be pushed, uploaded, or copied
to external systems until the live target is confirmed and the matching token is
provided:

`MAVERICK-CONFIRM github_publish <action_id>`

The iCloud destination uses a separate gate:

`MAVERICK-CONFIRM icloud_artifact_export <action_id>`
