#!/usr/bin/env python3
"""Build Maverick's local communication outbox.

The outbox prepares Slack, Gmail, Calendar, and Notion communication intents as
local drafts only. It never sends, schedules, posts, updates, or stores secrets.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from maverick_operating_loop import OPERATING_LOOP_PATH, build_operating_loop
from maverick_write_gates import confirmation_token


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "factory" / "active" / "maverick-cockpit"
OUTBOX_PATH = APP_DIR / "communication-outbox.json"
LIVE_TARGETS_PATH = APP_DIR / "live-targets.json"
COMMS_OUTBOX_OBSERVED_AT = "2026-06-14T18:44:12-04:00"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_operating_loop() -> dict[str, Any]:
    if OPERATING_LOOP_PATH.exists():
        return _load_json(OPERATING_LOOP_PATH)
    return build_operating_loop()


def _load_live_targets() -> dict[str, Any]:
    if LIVE_TARGETS_PATH.exists():
        return _load_json(LIVE_TARGETS_PATH)
    return {"targets": []}


def _target(targets: dict[str, Any], target_id: str) -> dict[str, Any]:
    return next((target for target in targets.get("targets", []) if target.get("id") == target_id), {})


def _delivery_status(target: dict[str, Any]) -> str:
    if target.get("confirmation_status") != "confirmed":
        return "blocked_pending_target"
    return "draft_ready_confirmation_required"


def _draft(
    *,
    draft_id: str,
    lane: str,
    target_id: str,
    gate_id: str,
    action_id: str,
    title: str,
    body: str,
    target: dict[str, Any],
) -> dict[str, Any]:
    return {
        "id": draft_id,
        "lane": lane,
        "target_id": target_id,
        "known_target": target.get("known_target"),
        "gate": gate_id,
        "action_id": action_id,
        "required_token": confirmation_token(gate_id, action_id),
        "status": _delivery_status(target),
        "title": title,
        "body": body,
        "external_mutation_attempted": False,
    }


def build_outbox(
    operating_loop: dict[str, Any] | None = None,
    live_targets: dict[str, Any] | None = None,
    observed_at: str = COMMS_OUTBOX_OBSERVED_AT,
) -> dict[str, Any]:
    loop = operating_loop or _load_operating_loop()
    targets = live_targets or _load_live_targets()
    mission = loop.get("mission") or {}
    objectives = loop.get("today_objectives") or []
    top_objective = objectives[0] if objectives else {}

    slack_target = _target(targets, "slack_maverick_app")
    gmail_target = _target(targets, "gmail_mailbox_lane")
    calendar_target = _target(targets, "google_calendar_lane")
    notion_target = _target(targets, "notion_live_launch_team")

    active_cases = mission.get("active_cases", 0)
    desired_cases = mission.get("desired_active_cases", 50)
    window_days = mission.get("window_days", 14)
    top_metric = top_objective.get("metric", "No objective selected")
    top_action = top_objective.get("action", "Review Daily Command")

    drafts = [
        _draft(
            draft_id="slack_daily_command_brief",
            lane="slack",
            target_id="slack_maverick_app",
            gate_id="slack_write",
            action_id="slack-daily-command-brief",
            title="Send Maverick daily command brief to Edwin",
            body=(
                f"Maverick daily command: {active_cases} active cases against the "
                f"{desired_cases}-case target. Protect the {window_days}-day window. "
                f"Top objective: {top_metric}. Next move: {top_action}."
            ),
            target=slack_target,
        ),
        _draft(
            draft_id="gmail_followup_batch_plan",
            lane="gmail",
            target_id="gmail_mailbox_lane",
            gate_id="gmail_send",
            action_id="gmail-followup-batch-plan",
            title="Prepare follow-up batch draft",
            body="Draft merchant follow-up messages only after mailbox identity and send boundary are confirmed.",
            target=gmail_target,
        ),
        _draft(
            draft_id="calendar_focus_block_plan",
            lane="google_calendar",
            target_id="google_calendar_lane",
            gate_id="google_calendar_update",
            action_id="calendar-focus-block-plan",
            title="Prepare protected callback/follow-up focus block",
            body="Plan a calendar focus block for callbacks and overdue follow-ups after calendar ownership is confirmed.",
            target=calendar_target,
        ),
        _draft(
            draft_id="notion_status_batch_plan",
            lane="notion",
            target_id="notion_live_launch_team",
            gate_id="notion_status_update",
            action_id="notion-status-batch-plan",
            title="Prepare Notion status update batch",
            body="Prepare status updates only after live row query, property mapping, and write method are confirmed.",
            target=notion_target,
        ),
    ]

    return {
        "generated_at": observed_at,
        "source_policy": {
            "mode": "local_draft_outbox",
            "external_mutation_attempted": False,
            "secret_storage_required": True,
            "personal_contact_fields_excluded": True,
        },
        "slack_app": {
            "app_id": slack_target.get("known_target") or "A0BALRB6CNQ",
            "target_status": slack_target.get("confirmation_status", "pending"),
            "communication_target": None,
            "secret_policy": "Bot token must live in a secret store, never in Notion, dashboard JSON, docs, or transcripts.",
        },
        "delivery_rules": [
            "No draft may leave local disk until its live target is confirmed.",
            "Every external action needs an exact MAVERICK-CONFIRM token for its gate and action id.",
            "Slack signal watch remains read-only; Slack app messages use the separate slack_write gate.",
            "Do not include secrets, bot tokens, direct personal contact details, or unverified case facts.",
        ],
        "drafts": drafts,
        "external_mutation_attempted": False,
    }


def write_outputs(observed_at: str = COMMS_OUTBOX_OBSERVED_AT) -> dict[str, Any]:
    outbox = build_outbox(observed_at=observed_at)
    OUTBOX_PATH.write_text(json.dumps(outbox, indent=2), encoding="utf-8")
    return outbox


def main() -> int:
    outbox = write_outputs()
    print(json.dumps({
        "communication_outbox": str(OUTBOX_PATH.relative_to(ROOT)),
        "drafts": len(outbox["drafts"]),
        "slack_app": outbox["slack_app"]["app_id"],
        "slack_status": outbox["slack_app"]["target_status"],
        "external_mutation_attempted": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
