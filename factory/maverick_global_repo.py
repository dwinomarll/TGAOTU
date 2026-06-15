#!/usr/bin/env python3
"""Prepare Maverick Cockpit for a standalone/global repository package."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "factory" / "active" / "maverick-cockpit"
CONTRACT_PATH = APP_DIR / "global-repo" / "repo-contract.json"
PACKAGE_MANIFEST_PATH = APP_DIR / "global-repo" / "package-manifest.json"
GLOBAL_REPO_OBSERVED_AT = "2026-06-14T16:35:13-04:00"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_package_manifest(observed_at: str = GLOBAL_REPO_OBSERVED_AT) -> dict[str, Any]:
    contract = _load_json(CONTRACT_PATH)
    export_manifest = _load_json(ROOT / contract["source_manifest"])
    artifact_paths = {artifact["path"] for artifact in export_manifest["artifacts"]}
    required_paths = {
        "docs/maverick-cockpit.md",
        "docs/maverick-source-map.md",
        "docs/maverick-ledger.md",
        "docs/maverick-adapters.md",
        "docs/maverick-write-gates.md",
        "docs/maverick-live-targets.md",
        "docs/maverick-global-repo.md",
        "docs/maverick-target-discovery.md",
        "docs/maverick-confirmation-applier.md",
        "docs/maverick-repo-assembly.md",
        "docs/maverick-operating-loop.md",
        "docs/maverick-communication-outbox.md",
        "docs/maverick-activation-checklist.md",
        "docs/maverick-learning-ledger.md",
        "docs/maverick-slack-bridge.md",
        "docs/maverick-github-bridge.md",
        "docs/maverick-notion-bridge.md",
        "docs/maverick-device-access.md",
        "factory/active/maverick-cockpit/device-access.json",
        "factory/active/maverick-cockpit/operating-loop.json",
        "factory/active/maverick-cockpit/communication-outbox.json",
        "factory/active/maverick-cockpit/activation-checklist.json",
        "factory/active/maverick-cockpit/learning-ledger.json",
        "factory/active/maverick-cockpit/slack-app-bridge.json",
        "factory/active/maverick-cockpit/github-publish-bridge.json",
        "factory/active/maverick-cockpit/notion-live-bridge.json",
        "factory/active/maverick-cockpit/confirmation-request.md",
        "factory/active/maverick-cockpit/target-discovery.json",
        "factory/active/maverick-cockpit/global-repo/README.md",
        "factory/active/maverick-cockpit/global-repo/repo-contract.json",
        "factory/active/maverick-cockpit/global-repo/netlify.toml",
        "factory/active/maverick-cockpit/live-targets.json",
        "factory/active/maverick-cockpit/dashboard/index.html",
        "factory/active/maverick-cockpit/dashboard/styles.css",
        "factory/active/maverick-cockpit/dashboard/app.js",
        "factory/active/maverick-cockpit/dashboard/icon.svg",
        "factory/active/maverick-cockpit/dashboard/manifest.webmanifest",
        "factory/active/maverick-cockpit/dashboard/service-worker.js",
        "factory/active/maverick-cockpit/dashboard/data/maverick-device-access.json",
        "factory/validate_maverick.py",
        "factory/maverick_assemble_repo.py",
        "factory/maverick_activation_checklist.py",
        "factory/maverick_confirm_target.py",
        "factory/maverick_comms_outbox.py",
        "factory/maverick_device_access.py",
        "factory/maverick_global_repo.py",
        "factory/maverick_github_bridge.py",
        "factory/maverick_learning_ledger.py",
        "factory/maverick_live_targets.py",
        "factory/maverick_notion_bridge.py",
        "factory/maverick_slack_bridge.py",
        "factory/maverick_operating_loop.py",
        "factory/maverick_serve_devices.py",
    }

    missing_required = sorted(required_paths - artifact_paths)
    return {
        "generated_at": observed_at,
        "contract": str(CONTRACT_PATH.relative_to(ROOT)),
        "suggested_repo_name": contract["suggested_repo_name"],
        "suggested_visibility": contract["suggested_visibility"],
        "publish_gate": contract["publish_gate"],
        "export_gate": contract["export_gate"],
        "publish_status": contract["publish_status"],
        "external_mutation_allowed": contract["external_mutation_allowed"],
        "source_manifest": contract["source_manifest"],
        "source_artifact_count": export_manifest["artifact_count"],
        "missing_required_artifacts": missing_required,
        "repo_layout": contract["repo_layout"],
        "required_confirmation_before_publish": contract["required_confirmation_before_publish"],
    }


def write_package_manifest(manifest: dict[str, Any]) -> None:
    PACKAGE_MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def main() -> int:
    manifest = build_package_manifest()
    write_package_manifest(manifest)
    print(json.dumps({
        "package_manifest": str(PACKAGE_MANIFEST_PATH.relative_to(ROOT)),
        "suggested_repo_name": manifest["suggested_repo_name"],
        "source_artifact_count": manifest["source_artifact_count"],
        "missing_required_artifacts": len(manifest["missing_required_artifacts"]),
        "external_mutation_allowed": manifest["external_mutation_allowed"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
