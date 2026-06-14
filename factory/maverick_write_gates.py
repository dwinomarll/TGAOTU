#!/usr/bin/env python3
"""Build and enforce Maverick confirmation gates.

The runner prepares local export metadata and audit evidence. It does not
perform external writes to Notion, Gmail, Google Calendar, iCloud, GitHub, or
Slack.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "factory" / "active" / "maverick-cockpit"
CONTRACT_PATH = APP_DIR / "write-gates" / "write-gate-contract.json"
EXPORT_MANIFEST_PATH = APP_DIR / "write-gates" / "export-manifest.json"
AUDIT_LOG_PATH = APP_DIR / "write-gates" / "audit-log.ndjson"
WRITE_GATE_OBSERVED_AT = "2026-06-14T16:30:35-04:00"
TOKEN_PREFIX = "MAVERICK-CONFIRM"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def confirmation_token(gate_id: str, action_id: str) -> str:
    return f"{TOKEN_PREFIX} {gate_id} {action_id}"


def _gate(contract: dict[str, Any], gate_id: str) -> dict[str, Any] | None:
    return next((gate for gate in contract["gates"] if gate["id"] == gate_id), None)


def assess_gate(gate_id: str, action_id: str, token: str | None = None) -> dict[str, Any]:
    contract = _load_json(CONTRACT_PATH)
    gate = _gate(contract, gate_id)
    if gate is None:
        return {
            "gate_id": gate_id,
            "action_id": action_id,
            "allowed": False,
            "reason": "unknown_gate",
            "external_mutation_attempted": False,
        }

    required = confirmation_token(gate_id, action_id)
    token_matches = token == required
    if gate["policy"] == "blocked":
        allowed = False
        reason = "policy_blocked"
    elif not gate["enabled"]:
        allowed = False
        reason = "gate_not_enabled"
    elif not token_matches:
        allowed = False
        reason = "missing_or_invalid_confirmation_token"
    else:
        allowed = True
        reason = "confirmed"

    return {
        "gate_id": gate_id,
        "system": gate["system"],
        "action_id": action_id,
        "allowed": allowed,
        "reason": reason,
        "required_token": required,
        "token_matches": token_matches,
        "external_mutation_attempted": False,
    }


def build_export_manifest(observed_at: str = WRITE_GATE_OBSERVED_AT) -> dict[str, Any]:
    contract = _load_json(CONTRACT_PATH)
    artifacts = []
    missing = []
    for rel_path in contract["local_exports"]:
        path = ROOT / rel_path
        if not path.exists():
            missing.append(rel_path)
            continue
        artifacts.append({
            "path": rel_path,
            "bytes": path.stat().st_size,
            "sha256": _sha256(path),
        })

    gate_status = []
    for gate in contract["gates"]:
        action_id = contract["confirmation"]["default_action_id"]
        assessment = assess_gate(gate["id"], action_id)
        gate_status.append({
            "id": gate["id"],
            "system": gate["system"],
            "operation": gate["operation"],
            "policy": gate["policy"],
            "enabled": gate["enabled"],
            "allowed_without_token": assessment["allowed"],
            "denial_reason": assessment["reason"],
        })

    return {
        "generated_at": observed_at,
        "contract": str(CONTRACT_PATH.relative_to(ROOT)),
        "destination": {
            "github": "pending explicit repo/branch confirmation",
            "icloud_drive": "https://www.icloud.com/iclouddrive/09dTCQP4Zljf2MEc0fPTBGyGA",
            "icloud_local_path": null_if_empty(""),
            "status": "prepared_local_manifest_only",
        },
        "external_mutation_attempted": False,
        "gates": gate_status,
        "artifact_count": len(artifacts),
        "missing_artifacts": missing,
        "artifacts": artifacts,
    }


def null_if_empty(value: str) -> str | None:
    return value or None


def build_audit_event(observed_at: str = WRITE_GATE_OBSERVED_AT) -> dict[str, Any]:
    return {
        "time": observed_at,
        "event_type": "write_gate_dry_run",
        "actor": "ENG-INTEGRATION",
        "external_mutation_attempted": False,
        "summary": "Prepared local export manifest and verified every external gate denies unconfirmed writes.",
    }


def write_outputs(observed_at: str = WRITE_GATE_OBSERVED_AT) -> dict[str, Any]:
    manifest = build_export_manifest(observed_at=observed_at)
    event = build_audit_event(observed_at=observed_at)
    EXPORT_MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    AUDIT_LOG_PATH.write_text(json.dumps(event, sort_keys=True) + "\n", encoding="utf-8")
    return {"manifest": manifest, "audit_event": event}


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare Maverick write-gate outputs")
    parser.add_argument("--gate-id")
    parser.add_argument("--action-id", default="phase6-dry-run")
    parser.add_argument("--confirm-token")
    args = parser.parse_args()

    if args.gate_id:
        assessment = assess_gate(args.gate_id, args.action_id, args.confirm_token)
        print(json.dumps(assessment, indent=2))
        return 0 if assessment["allowed"] else 2

    outputs = write_outputs()
    print(json.dumps({
        "export_manifest": str(EXPORT_MANIFEST_PATH.relative_to(ROOT)),
        "audit_log": str(AUDIT_LOG_PATH.relative_to(ROOT)),
        "artifact_count": outputs["manifest"]["artifact_count"],
        "external_mutation_attempted": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
