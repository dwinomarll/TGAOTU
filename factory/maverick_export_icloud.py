#!/usr/bin/env python3
"""Copy the assembled Maverick workflow package to the local iCloud folder."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

from maverick_write_gates import assess_gate


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "factory" / "active" / "maverick-cockpit"
PACKAGE_DIR = APP_DIR / "global-repo" / "package"
ASSEMBLY_MANIFEST_PATH = APP_DIR / "global-repo" / "assembly-manifest.json"
LIVE_TARGETS_PATH = APP_DIR / "live-targets.json"
EXPORT_MANIFEST_PATH = APP_DIR / "exports" / "icloud-export-manifest.json"
DEFAULT_DESTINATION_ROOT = Path("/Users/edwinrosa/Library/Mobile Documents/com~apple~CloudDocs/Desktop/MAVERICK")
DESTINATION_PACKAGE_NAME = "Maverick-Cockpit"
WORKFLOW_HANDOFF_NAME = "MAVERICK_COCKPIT_WORKFLOW.md"
ICLOUD_EXPORT_ACTION_ID = "phase7-icloud-workflow-copy"
ICLOUD_EXPORT_OBSERVED_AT = "2026-06-14T17:06:42-04:00"
PRESERVED_TOP_LEVEL_ITEMS = [".codex", "DAILY_OPERATIONS_DECK.md", "MAVERICK_DOCTRINE.md", "TEMPLATES"]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _relative_to_root(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _target_by_id(targets_doc: dict[str, Any], target_id: str) -> dict[str, Any] | None:
    return next((target for target in targets_doc["targets"] if target["id"] == target_id), None)


def _copy_file(source: Path, target: Path) -> dict[str, Any]:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return {
        "source": _relative_to_root(source),
        "target": str(target),
        "relative_target": str(target.relative_to(target.parents[1])),
        "bytes": target.stat().st_size,
        "sha256": _sha256(target),
    }


def _copy_package(destination_package_dir: Path) -> list[dict[str, Any]]:
    copied = []
    for source in sorted(PACKAGE_DIR.rglob("*")):
        if source.is_file():
            target = destination_package_dir / source.relative_to(PACKAGE_DIR)
            copied.append(_copy_file(source, target))
    return copied


def _write_workflow_handoff(destination_root: Path) -> dict[str, Any]:
    source = PACKAGE_DIR / "docs" / "maverick-workflow.md"
    target = destination_root / WORKFLOW_HANDOFF_NAME
    return _copy_file(source, target)


def _require_ready_destination(destination_root: Path) -> None:
    if not destination_root.exists() or not destination_root.is_dir():
        raise FileNotFoundError(f"destination root is not an existing directory: {destination_root}")
    if not PACKAGE_DIR.exists() or not PACKAGE_DIR.is_dir():
        raise FileNotFoundError(f"assembled package is missing: {PACKAGE_DIR}")
    if not ASSEMBLY_MANIFEST_PATH.exists():
        raise FileNotFoundError(f"assembly manifest is missing: {ASSEMBLY_MANIFEST_PATH}")


def _require_confirmed_target(destination_root: Path) -> dict[str, Any]:
    targets_doc = _load_json(LIVE_TARGETS_PATH)
    target = _target_by_id(targets_doc, "icloud_destination")
    if target is None:
        raise ValueError("live-targets.json is missing icloud_destination")
    if target.get("confirmation_status") != "confirmed":
        raise PermissionError("icloud_destination must be confirmed before export")
    known_target = target.get("known_target") or ""
    if not str(destination_root) in known_target:
        raise PermissionError("confirmed iCloud target does not match the requested destination")
    return target


def export_to_icloud(
    confirm_token: str,
    destination_root: Path = DEFAULT_DESTINATION_ROOT,
    action_id: str = ICLOUD_EXPORT_ACTION_ID,
    observed_at: str = ICLOUD_EXPORT_OBSERVED_AT,
) -> dict[str, Any]:
    _require_ready_destination(destination_root)
    target = _require_confirmed_target(destination_root)
    gate = assess_gate("icloud_artifact_export", action_id, confirm_token)
    if not gate.get("allowed"):
        raise PermissionError(f"iCloud export gate denied: {gate.get('reason')}")

    destination_package_dir = destination_root / DESTINATION_PACKAGE_NAME
    destination_package_dir.mkdir(parents=True, exist_ok=True)

    copied = _copy_package(destination_package_dir)
    workflow_handoff = _write_workflow_handoff(destination_root)
    assembly_manifest = _load_json(ASSEMBLY_MANIFEST_PATH)

    manifest = {
        "generated_at": observed_at,
        "action_id": action_id,
        "source_package_dir": str(PACKAGE_DIR.relative_to(ROOT)),
        "destination_root": str(destination_root),
        "destination_package_dir": str(destination_package_dir),
        "workflow_handoff": workflow_handoff,
        "confirmed_target_id": "icloud_destination",
        "confirmed_target": {
            "known_target": target.get("known_target"),
            "owner_boundary": target.get("owner_boundary"),
            "access_method": target.get("access_method"),
            "write_gate": target.get("write_gate"),
        },
        "gate": {
            "id": gate["gate_id"],
            "allowed": gate["allowed"],
            "reason": gate["reason"],
            "required_token": gate["required_token"],
            "token_matches": gate["token_matches"],
        },
        "preserved_top_level_items": [
            {"path": str(destination_root / item), "exists": (destination_root / item).exists()}
            for item in PRESERVED_TOP_LEVEL_ITEMS
        ],
        "source_assembly_file_count": assembly_manifest.get("file_count"),
        "copied_file_count": len(copied),
        "copied_files": copied,
        "local_icloud_filesystem_write_performed": True,
        "external_mutation_scope": "local mounted iCloud Drive folder explicitly provided by the user",
        "slack_write_attempted": False,
    }
    EXPORT_MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    EXPORT_MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Maverick Cockpit package to the local iCloud destination")
    parser.add_argument("--confirm-token", required=True)
    parser.add_argument("--action-id", default=ICLOUD_EXPORT_ACTION_ID)
    parser.add_argument("--destination-root", default=str(DEFAULT_DESTINATION_ROOT))
    args = parser.parse_args()

    manifest = export_to_icloud(
        confirm_token=args.confirm_token,
        destination_root=Path(args.destination_root),
        action_id=args.action_id,
    )
    print(json.dumps({
        "export_manifest": str(EXPORT_MANIFEST_PATH.relative_to(ROOT)),
        "destination_package_dir": manifest["destination_package_dir"],
        "workflow_handoff": manifest["workflow_handoff"]["target"],
        "copied_file_count": manifest["copied_file_count"],
        "local_icloud_filesystem_write_performed": True,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
