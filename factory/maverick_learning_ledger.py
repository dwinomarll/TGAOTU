#!/usr/bin/env python3
"""Build Maverick's local learning ledger."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from maverick_activation_checklist import ACTIVATION_CHECKLIST_PATH, build_activation_checklist
from maverick_comms_outbox import OUTBOX_PATH, build_outbox
from maverick_notion_overview import OVERVIEW_PATH, build_notion_overview
from maverick_operating_loop import OPERATING_LOOP_PATH, build_operating_loop


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "factory" / "active" / "maverick-cockpit"
LEARNING_LEDGER_PATH = APP_DIR / "learning-ledger.json"
LEARNING_LEDGER_OBSERVED_AT = "2026-06-14T19:12:26-04:00"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_or_build(path: Path, builder: Any) -> dict[str, Any]:
    if path.exists():
        return _load_json(path)
    return builder()


def _event(event_id: str, kind: str, signal: str, lesson: str, action: str) -> dict[str, Any]:
    return {
        "id": event_id,
        "kind": kind,
        "signal": signal,
        "lesson": lesson,
        "next_action": action,
        "promotion_status": "promoted_to_dashboard_memory",
        "confidence": "evidence_backed",
    }


def build_learning_ledger(observed_at: str = LEARNING_LEDGER_OBSERVED_AT) -> dict[str, Any]:
    overview = _load_or_build(OVERVIEW_PATH, build_notion_overview)
    operating_loop = _load_or_build(OPERATING_LOOP_PATH, build_operating_loop)
    outbox = _load_or_build(OUTBOX_PATH, build_outbox)
    activation = _load_or_build(ACTIVATION_CHECKLIST_PATH, build_activation_checklist)

    portfolio = overview.get("portfolio_snapshot") or {}
    reconciliation = overview.get("reconciliation") or {}
    mission = operating_loop.get("mission") or {}
    slack_app = outbox.get("slack_app") or {}
    activation_summary = activation.get("activation_summary") or {}

    events = [
        _event(
            "case_pressure_target_gap",
            "portfolio_pressure",
            f"{portfolio.get('total_active_cases', 0)} active cases vs {mission.get('desired_active_cases', 50)} target",
            "Maverick must prioritize reduction lanes before expanding new work.",
            "Keep Daily Command focused on overdue, callback, false-close, and reactivation objectives.",
        ),
        _event(
            "overdue_followup_bias",
            "timing_pressure",
            f"{portfolio.get('overdue_followups', 0)} overdue follow-ups",
            "Overdue work is the clearest signal that the 14-day rule is under pressure.",
            "Promote overdue follow-ups into the first daily work block.",
        ),
        _event(
            "callback_batching",
            "workflow_pattern",
            f"{portfolio.get('callbacks_pending', 0)} callbacks pending",
            "Callbacks should be batched through the Callback canvas instead of handled one by one.",
            "Use the Callback canvas as the default route for call-stack actions.",
        ),
        _event(
            "false_closure_qa",
            "quality_pattern",
            f"{portfolio.get('resolved_but_open_task', 0)} resolved-but-open tasks",
            "Resolved labels are not enough; QA must confirm the task is actually closed.",
            "Route resolved-but-open work through QA Breakdown before archive.",
        ),
        _event(
            "reactivation_burndown",
            "burndown_pattern",
            f"{reconciliation.get('move_to_active', 0)} accounts marked move to active",
            "Reactivation candidates should enter active review deliberately, not by copying stale rows wholesale.",
            "Use Portfolio Reconciliation as a candidate list, then verify each case before action.",
        ),
        _event(
            "slack_two_lane_model",
            "communication_boundary",
            f"Slack app {slack_app.get('app_id', 'A0BALRB6CNQ')} is {slack_app.get('target_status', 'pending')}",
            "Slack signal watching and Slack app messaging are different lanes with different gates.",
            "Keep the watch read-only and use Comms Outbox plus slack_write for future app messages.",
        ),
        _event(
            "activation_gate_pressure",
            "safety_pattern",
            f"{activation_summary.get('pending_targets', 0)} live targets pending",
            "Maverick should surface missing evidence instead of guessing live access.",
            "Use Activation Matrix before attempting publish, send, schedule, or update actions.",
        ),
    ]

    rejected = [
        {
            "id": "direct_contact_fields",
            "reason": "contact_number and contact_email are explicitly never-guess fields",
            "handling": "leave unknown until verified in the source system",
        },
        {
            "id": "bot_or_oauth_tokens",
            "reason": "secrets must live only in a secret store",
            "handling": "do not write tokens into Notion, docs, dashboard JSON, or transcripts",
        },
        {
            "id": "unmatched_slack_chatter",
            "reason": "Slack signal watch alerts only on active-account evidence",
            "handling": "ignore chatter unless it matches MID, DBA, account, contact, or Salesforce case",
        },
        {
            "id": "unverified_row_mutation",
            "reason": "Notion row query and update method are not confirmed",
            "handling": "prepare local plans only until live row method is proven",
        },
    ]

    return {
        "generated_at": observed_at,
        "source_policy": {
            "mode": "local_learning_ledger",
            "external_mutation_attempted": False,
            "personal_contact_fields_excluded": True,
            "secrets_recorded": False,
            "promotion_rule": "Promote a learning only when it changes routing, priority, safety, or next action.",
        },
        "summary": {
            "promoted_events": len(events),
            "rejected_memory": len(rejected),
            "confidence": "evidence_backed_local_snapshot",
            "review_cadence": "daily after case work and before export/publish decisions",
        },
        "learning_events": events,
        "rejected_memory": rejected,
        "dashboard_ready": True,
        "external_mutation_attempted": False,
    }


def write_outputs(observed_at: str = LEARNING_LEDGER_OBSERVED_AT) -> dict[str, Any]:
    ledger = build_learning_ledger(observed_at=observed_at)
    LEARNING_LEDGER_PATH.write_text(json.dumps(ledger, indent=2), encoding="utf-8")
    return ledger


def main() -> int:
    ledger = write_outputs()
    print(json.dumps({
        "learning_ledger": str(LEARNING_LEDGER_PATH.relative_to(ROOT)),
        "promoted_events": ledger["summary"]["promoted_events"],
        "rejected_memory": ledger["summary"]["rejected_memory"],
        "external_mutation_attempted": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
