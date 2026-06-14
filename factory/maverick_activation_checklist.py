#!/usr/bin/env python3
"""Build Maverick's local activation checklist for live targets."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from maverick_comms_outbox import OUTBOX_PATH
from maverick_write_gates import confirmation_token


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "factory" / "active" / "maverick-cockpit"
LIVE_TARGETS_PATH = APP_DIR / "live-targets.json"
WRITE_GATE_CONTRACT_PATH = APP_DIR / "write-gates" / "write-gate-contract.json"
ACTIVATION_CHECKLIST_PATH = APP_DIR / "activation-checklist.json"
ACTIVATION_CHECKLIST_OBSERVED_AT = "2026-06-14T18:58:09-04:00"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_optional(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return _load_json(path)


def _gate_by_id(contract: dict[str, Any]) -> dict[str, Any]:
    return {gate.get("id"): gate for gate in contract.get("gates", [])}


def _draft_by_target(outbox: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for draft in outbox.get("drafts", []):
        grouped.setdefault(draft.get("target_id", "unknown"), []).append(draft)
    return grouped


def _status(target: dict[str, Any], gate: dict[str, Any]) -> str:
    if target.get("confirmation_status") == "confirmed" and gate.get("enabled"):
        return "ready_with_confirmation_token"
    if target.get("confirmation_status") == "confirmed":
        return "target_confirmed_gate_review_needed"
    return "needs_confirmation"


def build_activation_checklist(observed_at: str = ACTIVATION_CHECKLIST_OBSERVED_AT) -> dict[str, Any]:
    live_targets = _load_json(LIVE_TARGETS_PATH)
    gates = _gate_by_id(_load_json(WRITE_GATE_CONTRACT_PATH))
    drafts = _draft_by_target(_load_optional(OUTBOX_PATH))

    lanes = []
    for target in live_targets.get("targets", []):
        gate_id = target.get("write_gate", "unknown_gate")
        gate = gates.get(gate_id, {})
        action_id = f"activate-{target.get('id', 'unknown-target')}"
        target_drafts = drafts.get(target.get("id"), [])
        missing = []
        if target.get("confirmation_status") != "confirmed":
            missing.extend(target.get("evidence_required", []))
        if gate_id == "slack_write" and target.get("id") == "slack_maverick_app":
            missing.append("Slack channel or DM id must be stored as the communication target")
            missing.append("bot token must stay in the secret store, not in repo artifacts")

        lanes.append({
            "target_id": target.get("id"),
            "system": target.get("system"),
            "known_target": target.get("known_target"),
            "confirmation_status": target.get("confirmation_status"),
            "gate": gate_id,
            "gate_enabled": bool(gate.get("enabled")),
            "activation_status": _status(target, gate),
            "missing_evidence": missing,
            "draft_count": len(target_drafts),
            "draft_ids": [draft.get("id") for draft in target_drafts],
            "example_action_id": action_id,
            "example_confirmation_token": confirmation_token(gate_id, action_id),
            "external_mutation_attempted": False,
        })

    pending = [lane for lane in lanes if lane["activation_status"] != "ready_with_confirmation_token"]
    return {
        "generated_at": observed_at,
        "source_policy": {
            "mode": "local_activation_checklist",
            "external_mutation_attempted": False,
            "secrets_recorded": False,
            "confirmation_tokens_are_examples": True,
        },
        "activation_summary": {
            "total_targets": len(lanes),
            "ready_with_confirmation_token": sum(1 for lane in lanes if lane["activation_status"] == "ready_with_confirmation_token"),
            "pending_targets": len(pending),
            "pending_target_ids": [lane["target_id"] for lane in pending],
        },
        "lanes": lanes,
        "external_mutation_attempted": False,
    }


def write_outputs(observed_at: str = ACTIVATION_CHECKLIST_OBSERVED_AT) -> dict[str, Any]:
    checklist = build_activation_checklist(observed_at=observed_at)
    ACTIVATION_CHECKLIST_PATH.write_text(json.dumps(checklist, indent=2), encoding="utf-8")
    return checklist


def main() -> int:
    checklist = write_outputs()
    print(json.dumps({
        "activation_checklist": str(ACTIVATION_CHECKLIST_PATH.relative_to(ROOT)),
        "total_targets": checklist["activation_summary"]["total_targets"],
        "pending_targets": checklist["activation_summary"]["pending_targets"],
        "external_mutation_attempted": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
