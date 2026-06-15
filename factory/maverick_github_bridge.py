#!/usr/bin/env python3
"""Build Maverick's local GitHub publish bridge.

The bridge prepares a global-repo publish envelope from local package evidence.
It never pushes, creates a repository, opens a pull request, or records secrets.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from maverick_write_gates import WRITE_GATE_OBSERVED_AT, assess_gate, confirmation_token


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "factory" / "active" / "maverick-cockpit"
GITHUB_BRIDGE_PATH = APP_DIR / "github-publish-bridge.json"
LIVE_TARGETS_PATH = APP_DIR / "live-targets.json"
TARGET_DISCOVERY_PATH = APP_DIR / "target-discovery.json"
PACKAGE_MANIFEST_PATH = APP_DIR / "global-repo" / "package-manifest.json"
ASSEMBLY_MANIFEST_PATH = APP_DIR / "global-repo" / "assembly-manifest.json"
GITHUB_BRIDGE_OBSERVED_AT = "2026-06-14T19:38:44-04:00"
GITHUB_PUBLISH_ACTION_ID = "github-publish-maverick-cockpit"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)


def _git_value(command: list[str]) -> str | None:
    result = _run(command)
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def _target(targets: dict[str, Any], target_id: str) -> dict[str, Any]:
    return next((target for target in targets.get("targets", []) if target.get("id") == target_id), {})


def build_github_bridge(observed_at: str = GITHUB_BRIDGE_OBSERVED_AT) -> dict[str, Any]:
    live_targets = _load_json(LIVE_TARGETS_PATH)
    discovery = _load_json(TARGET_DISCOVERY_PATH)
    package = _load_json(PACKAGE_MANIFEST_PATH)
    assembly = _load_json(ASSEMBLY_MANIFEST_PATH)
    github_target = _target(live_targets, "github_global_repo")
    github = discovery.get("github") or {}
    gate_id = github_target.get("write_gate") or github.get("write_gate") or "github_publish"
    assessment = assess_gate(gate_id, GITHUB_PUBLISH_ACTION_ID, token=None)

    package_dir = assembly.get("package_dir")
    return {
        "generated_at": observed_at,
        "source_policy": {
            "mode": "local_github_publish_bridge",
            "external_mutation_attempted": False,
            "secrets_recorded": False,
            "gh_auth_output_recorded": False,
        },
        "repository": {
            "target_id": "github_global_repo",
            "candidate_repo": github.get("candidate_repo"),
            "candidate_branch": github.get("candidate_branch"),
            "candidate_publish_mode": github.get("candidate_publish_mode"),
            "current_origin": github.get("current_origin") or _git_value(["git", "config", "--get", "remote.origin.url"]),
            "current_branch": _git_value(["git", "branch", "--show-current"]),
            "current_commit": "tracked_by_git_history_not_embedded",
            "confirmation_status": github_target.get("confirmation_status", "pending"),
            "write_gate": gate_id,
        },
        "package_evidence": {
            "package_dir": package_dir,
            "assembled_file_count": assembly.get("file_count", 0),
            "source_artifact_count": package.get("source_artifact_count", 0),
            "missing_required_artifacts": package.get("missing_required_artifacts", []),
            "external_mutation_allowed": bool(package.get("external_mutation_allowed")),
            "publish_status": package.get("publish_status"),
        },
        "publish_envelope": {
            "action_id": GITHUB_PUBLISH_ACTION_ID,
            "required_token": confirmation_token(gate_id, GITHUB_PUBLISH_ACTION_ID),
            "gate_assessment_without_token": assessment,
            "publish_allowed": False,
            "commands_planned_not_run": [
                "create or select the target repository after confirmation",
                "create local publish branch from the assembled package after confirmation",
                "push the branch after confirmation",
                "open a pull request or release after confirmation",
            ],
        },
        "required_before_publish": [
            "Confirm repo owner/name or explicitly approve creating a new repo.",
            "Confirm branch name and publish mode.",
            "Confirm whether package/ should be copied into the current repo or published as a standalone repo root.",
            "Provide an exact MAVERICK-CONFIRM github_publish token for the action id.",
        ],
        "dry_run": {
            "publish_attempted": False,
            "publish_allowed": False,
            "reason": "missing confirmed GitHub target and confirmation token",
            "gate_timestamp": WRITE_GATE_OBSERVED_AT,
        },
        "external_mutation_attempted": False,
    }


def write_outputs(observed_at: str = GITHUB_BRIDGE_OBSERVED_AT) -> dict[str, Any]:
    bridge = build_github_bridge(observed_at=observed_at)
    GITHUB_BRIDGE_PATH.write_text(json.dumps(bridge, indent=2), encoding="utf-8")
    return bridge


def main() -> int:
    bridge = write_outputs()
    print(json.dumps({
        "github_bridge": str(GITHUB_BRIDGE_PATH.relative_to(ROOT)),
        "candidate_repo": bridge["repository"]["candidate_repo"],
        "assembled_file_count": bridge["package_evidence"]["assembled_file_count"],
        "publish_allowed": bridge["dry_run"]["publish_allowed"],
        "external_mutation_attempted": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
