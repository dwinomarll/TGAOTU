#!/usr/bin/env python3
"""Confirm Maverick live targets locally after an explicit gate token.

This script only updates Maverick's local confirmation ledger when run with
`--apply`. It never publishes to GitHub, copies to iCloud, mutates Notion,
sends Gmail, updates Calendar, or writes to Slack.
"""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

from maverick_write_gates import confirmation_token


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "factory" / "active" / "maverick-cockpit"
LIVE_TARGETS_PATH = APP_DIR / "live-targets.json"
CONFIRMATION_LOG_PATH = APP_DIR / "confirmation-log.ndjson"
CONFIRMATION_ACTION_ID = "phase7-live-target-confirmation"
CONFIRMATION_OBSERVED_AT = "2026-06-14T16:40:22-04:00"
REQUIRED_PAYLOAD_FIELDS = {
    "known_target",
    "owner_boundary",
    "access_method",
    "write_gate",
    "allowed_action",
    "evidence",
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _target_by_id(targets_doc: dict[str, Any], target_id: str) -> dict[str, Any] | None:
    return next((target for target in targets_doc["targets"] if target["id"] == target_id), None)


def evaluate_confirmation(
    target_id: str,
    token: str,
    payload: dict[str, Any],
    action_id: str = CONFIRMATION_ACTION_ID,
) -> dict[str, Any]:
    targets_doc = _load_json(LIVE_TARGETS_PATH)
    target = _target_by_id(targets_doc, target_id)
    if target is None:
        return {
            "target_id": target_id,
            "allowed": False,
            "reason": "unknown_target",
            "external_mutation_attempted": False,
        }

    gate_id = target["write_gate"]
    required_token = confirmation_token(gate_id, action_id)
    missing_payload = sorted(field for field in REQUIRED_PAYLOAD_FIELDS if not payload.get(field))
    allowed = True
    reason = "confirmed_for_local_ledger_only"

    if token != required_token:
        allowed = False
        reason = "missing_or_invalid_confirmation_token"
    elif payload.get("write_gate") != gate_id:
        allowed = False
        reason = "payload_write_gate_mismatch"
    elif missing_payload:
        allowed = False
        reason = "missing_payload_fields"
    elif target.get("confirmation_status") == "confirmed":
        allowed = False
        reason = "target_already_confirmed"

    return {
        "target_id": target_id,
        "system": target["system"],
        "write_gate": gate_id,
        "action_id": action_id,
        "allowed": allowed,
        "reason": reason,
        "required_token": required_token,
        "missing_payload_fields": missing_payload,
        "external_mutation_attempted": False,
    }


def build_confirmed_targets(
    target_id: str,
    token: str,
    payload: dict[str, Any],
    observed_at: str = CONFIRMATION_OBSERVED_AT,
    action_id: str = CONFIRMATION_ACTION_ID,
) -> tuple[dict[str, Any], dict[str, Any]]:
    assessment = evaluate_confirmation(target_id, token, payload, action_id=action_id)
    targets_doc = _load_json(LIVE_TARGETS_PATH)
    if not assessment["allowed"]:
        return targets_doc, assessment

    updated = copy.deepcopy(targets_doc)
    target = _target_by_id(updated, target_id)
    if target is None:
        return updated, assessment

    target["confirmation_status"] = "confirmed"
    target["confirmed_at"] = observed_at
    target["known_target"] = payload["known_target"]
    target["owner_boundary"] = payload["owner_boundary"]
    target["access_method"] = payload["access_method"]
    target["allowed_action"] = payload["allowed_action"]
    target["confirmation_evidence"] = payload["evidence"]
    target["external_mutation_allowed"] = False
    target["notes"] = (
        f"Confirmed locally for {payload['allowed_action']}. "
        "External mutation still requires the action runner to pass its write gate."
    )
    return updated, assessment


def apply_confirmation(
    target_id: str,
    token: str,
    payload: dict[str, Any],
    observed_at: str = CONFIRMATION_OBSERVED_AT,
    action_id: str = CONFIRMATION_ACTION_ID,
) -> dict[str, Any]:
    updated, assessment = build_confirmed_targets(
        target_id,
        token,
        payload,
        observed_at=observed_at,
        action_id=action_id,
    )
    if not assessment["allowed"]:
        return assessment

    LIVE_TARGETS_PATH.write_text(json.dumps(updated, indent=2), encoding="utf-8")
    event = {
        "time": observed_at,
        "event_type": "live_target_confirmed",
        "target_id": target_id,
        "write_gate": assessment["write_gate"],
        "action_id": action_id,
        "external_mutation_attempted": False,
    }
    with CONFIRMATION_LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\n")
    return assessment


def main() -> int:
    parser = argparse.ArgumentParser(description="Confirm Maverick live targets locally")
    parser.add_argument("--target-id", required=True)
    parser.add_argument("--token", required=True)
    parser.add_argument("--payload-json", required=True)
    parser.add_argument("--action-id", default=CONFIRMATION_ACTION_ID)
    parser.add_argument("--apply", action="store_true", help="write the local confirmation ledger")
    args = parser.parse_args()

    payload = json.loads(args.payload_json)
    if args.apply:
        result = apply_confirmation(args.target_id, args.token, payload, action_id=args.action_id)
    else:
        result = evaluate_confirmation(args.target_id, args.token, payload, action_id=args.action_id)
        result["dry_run"] = True

    print(json.dumps(result, indent=2))
    return 0 if result["allowed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
