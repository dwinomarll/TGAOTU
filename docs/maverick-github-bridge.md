# Maverick GitHub Publish Bridge

The GitHub Publish Bridge is the local activation contract for making Maverick
usable as a global repository. It proves what package would be published and
what confirmation is missing. It does not push, create a repository, open a pull
request, or run any mutating GitHub command.

Machine output:
`factory/active/maverick-cockpit/github-publish-bridge.json`

Runner:
`python3 factory/maverick_github_bridge.py`

Validator:
`python3 factory/validate_maverick.py --phase github-bridge`

## Candidate Target

The current candidate is `dwinomarll/maverick-cockpit` on branch
`codex/maverick-cockpit`, using the `github_publish` gate. The bridge records
the current origin, current commit, package file count, source artifact count,
and missing required artifacts from the local package manifest.

## Required Before Publish

- Confirm repo owner/name or explicitly approve creating a new repo.
- Confirm branch name and publish mode.
- Confirm whether the assembled `package/` becomes the standalone repo root or
  is copied into the current repo.
- Provide `MAVERICK-CONFIRM github_publish github-publish-maverick-cockpit`.

Until those are true, `publish_allowed` remains false and no external mutation
is attempted.
