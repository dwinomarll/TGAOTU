#!/usr/bin/env python3
"""Build Maverick's local Slack app bridge contract.

The bridge prepares safe message envelopes for the Maverick Slack app. It never
sends messages, records bot tokens, or changes the legacy read-only watch.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from maverick_comms_outbox import OUTBOX_PATH, build_outbox
from maverick_write_gates import WRITE_GATE_OBSERVED_AT, assess_gate


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "factory" / "active" / "maverick-cockpit"
LIVE_TARGETS_PATH = APP_DIR / "live-targets.json"
SLACK_BRIDGE_PATH = APP_DIR / "slack-app-bridge.json"
SLACK_BRIDGE_OBSERVED_AT = "2026-06-14T19:27:18-04:00"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_outbox() -> dict[str, Any]:
    if OUTBOX_PATH.exists():
        return _load_json(OUTBOX_PATH)
    return build_outbox()


def _target(targets: dict[str, Any], target_id: str) -> dict[str, Any]:
    return next((target for target in targets.get("targets", []) if target.get("id") == target_id), {})


def _slack_drafts(outbox: dict[str, Any]) -> list[dict[str, Any]]:
    return [draft for draft in outbox.get("drafts", []) if draft.get("lane") == "slack"]


def build_slack_bridge(observed_at: str = SLACK_BRIDGE_OBSERVED_AT) -> dict[str, Any]:
    live_targets = _load_json(LIVE_TARGETS_PATH)
    outbox = _load_outbox()
    slack_target = _target(live_targets, "slack_maverick_app")
    slack_app = outbox.get("slack_app") or {}
    app_id = slack_target.get("known_target") or slack_app.get("app_id") or "A0BALRB6CNQ"

    envelopes = []
    for draft in _slack_drafts(outbox):
        assessment = assess_gate(
            draft.get("gate", "slack_write"),
            draft.get("action_id", "slack-action"),
            token=None,
        )
        envelopes.append({
            "id": draft.get("id"),
            "app_id": app_id,
            "channel_or_dm_id": None,
            "text": draft.get("body"),
            "source_draft": draft.get("id"),
            "required_gate": draft.get("gate"),
            "required_token": draft.get("required_token"),
            "gate_assessment_without_token": assessment,
            "send_allowed": False,
            "delivery_status": "blocked_pending_channel_or_dm_secret_and_confirmation",
            "external_mutation_attempted": False,
        })

    return {
        "generated_at": observed_at,
        "source_policy": {
            "mode": "local_slack_app_bridge",
            "legacy_watch_policy": "read_only",
            "external_mutation_attempted": False,
            "secrets_recorded": False,
            "personal_contact_fields_excluded": True,
        },
        "app": {
            "id": app_id,
            "target_id": "slack_maverick_app",
            "known_target": slack_target.get("known_target"),
            "confirmation_status": slack_target.get("confirmation_status", "pending"),
            "write_gate": slack_target.get("write_gate", "slack_write"),
            "communication_target": None,
            "secret_store_reference": None,
        },
        "required_before_send": [
            "Confirm the Slack channel id or DM id where Maverick should communicate with Edwin.",
            "Store the bot token only in a secret store outside repo artifacts.",
            "Confirm the exact message action id with a MAVERICK-CONFIRM slack_write token.",
            "Keep the legacy Slack signal watch read-only.",
        ],
        "message_envelopes": envelopes,
        "dry_run": {
            "send_attempted": False,
            "send_allowed": False,
            "reason": "missing channel_or_dm_id, secret_store_reference, and confirmation token",
            "gate_timestamp": WRITE_GATE_OBSERVED_AT,
        },
        "external_mutation_attempted": False,
    }


def write_outputs(observed_at: str = SLACK_BRIDGE_OBSERVED_AT) -> dict[str, Any]:
    bridge = build_slack_bridge(observed_at=observed_at)
    SLACK_BRIDGE_PATH.write_text(json.dumps(bridge, indent=2), encoding="utf-8")
    return bridge


def main() -> int:
    bridge = write_outputs()
    print(json.dumps({
        "slack_bridge": str(SLACK_BRIDGE_PATH.relative_to(ROOT)),
        "app_id": bridge["app"]["id"],
        "message_envelopes": len(bridge["message_envelopes"]),
        "send_allowed": bridge["dry_run"]["send_allowed"],
        "external_mutation_attempted": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
