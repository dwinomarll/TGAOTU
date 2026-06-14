# Maverick Repo Assembly

Repo assembly builds a local preview of the standalone Maverick repository. It
copies the prepared cockpit artifacts into a generated package directory without
creating a GitHub repo, pushing a branch, or copying anything to iCloud Drive.

Runner:
`python3 factory/maverick_assemble_repo.py`

Generated output:

- `factory/active/maverick-cockpit/global-repo/assembly-manifest.json`
- `factory/active/maverick-cockpit/global-repo/package/`

The `package/` directory is generated and ignored by Git. The manifest is the
tracked proof of what was assembled.

Assembly uses a local lock directory at
`factory/active/maverick-cockpit/global-repo/.assembly.lock` so concurrent
validators or export runners do not rebuild `package/` at the same time.

The package intentionally excludes generated proof files that would make the
package self-referential, such as its own assembly manifest. Those remain beside
the package in `global-repo/`.

Validation:
`python3 factory/validate_maverick.py --phase repo-assembly`
