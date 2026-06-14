#!/usr/bin/env python3
"""Build Maverick's local Notion live-row bridge.

The bridge prepares row-query and update envelopes for the Launch Team source.
It never mutates Notion and does not invent row data when live row access is
unavailable.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from maverick_comms_outbox import OUTBOX_PATH, build_outbox
from maverick_notion_overview import NOTION_OVERVIEW_OBSERVED_AT, OVERVIEW_PATH, build_notion_overview
from maverick_write_gates import WRITE_GATE_OBSERVED_AT, assess_gate


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "factory" / "active" / "maverick-cockpit"
NOTION_BRIDGE_PATH = APP_DIR / "notion-live-bridge.json"
LIVE_TARGETS_PATH = APP_DIR / "live-targets.json"
NOTION_BRIDGE_OBSERVED_AT = "2026-06-14T19:49:33-04:00"
NOTION_UPDATE_ACTION_ID = "notion-status-batch-plan"
LAUNCH_TEAM_COLLECTION = "collection://2106ae29-a07c-81cb-9c6e-000ba25c1f45"
LOCAL_CACHE_FALLBACK = "/Users/edwinrosa/.codex/worktrees/slack-signal-maverick/Maverick Project/Shift4 Dine/Workflow/modules/_base.py"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_overview() -> dict[str, Any]:
    if OVERVIEW_PATH.exists():
        return _load_json(OVERVIEW_PATH)
    return build_notion_overview()


def _load_outbox() -> dict[str, Any]:
    if OUTBOX_PATH.exists():
        return _load_json(OUTBOX_PATH)
    return build_outbox()


def _target(targets: dict[str, Any], target_id: str) -> dict[str, Any]:
    return next((target for target in targets.get("targets", []) if target.get("id") == target_id), {})


def _notion_drafts(outbox: dict[str, Any]) -> list[dict[str, Any]]:
    return [draft for draft in outbox.get("drafts", []) if draft.get("lane") == "notion"]


def build_notion_bridge(observed_at: str = NOTION_BRIDGE_OBSERVED_AT) -> dict[str, Any]:
    live_targets = _load_json(LIVE_TARGETS_PATH)
    overview = _load_overview()
    outbox = _load_outbox()
    target = _target(live_targets, "notion_live_launch_team")
    gate_id = target.get("write_gate") or "notion_status_update"
    policy = overview.get("source_policy") or {}
    portfolio = overview.get("portfolio_snapshot") or {}
    canvases = overview.get("canvases") or []
    drafts = _notion_drafts(outbox)

    update_envelopes = []
    for draft in drafts:
        assessment = assess_gate(draft.get("gate", gate_id), draft.get("action_id", NOTION_UPDATE_ACTION_ID), token=None)
        update_envelopes.append({
            "id": draft.get("id"),
            "target_id": "notion_live_launch_team",
            "collection": LAUNCH_TEAM_COLLECTION,
            "source_draft": draft.get("id"),
            "required_gate": draft.get("gate", gate_id),
            "required_token": draft.get("required_token"),
            "proposed_operation": "batch_status_update_after_row_method_confirmation",
            "row_filter": {
                "active_window_days": 14,
                "requires_live_row_query": True,
                "fallback_is_read_only_cache": True,
            },
            "property_map_required": [
                "Task Status",
                "Next Action",
                "Next Follow-up",
                "QA Score",
                "MID",
                "Salesforce Case",
            ],
            "gate_assessment_without_token": assessment,
            "update_allowed": False,
            "external_mutation_attempted": False,
        })

    return {
        "generated_at": observed_at,
        "source_policy": {
            "mode": "local_notion_live_bridge",
            "preferred_source": LAUNCH_TEAM_COLLECTION,
            "row_query_status": policy.get("notion_query_data_sources", "unavailable"),
            "local_cache_fallback": LOCAL_CACHE_FALLBACK,
            "external_mutation_attempted": False,
            "personal_contact_fields_excluded": True,
            "secrets_recorded": False,
        },
        "target": {
            "id": "notion_live_launch_team",
            "known_target": target.get("known_target") or LAUNCH_TEAM_COLLECTION,
            "confirmation_status": target.get("confirmation_status", "pending"),
            "write_gate": gate_id,
            "live_row_query_method": None,
            "live_update_method": None,
            "property_mapping_confirmed": False,
        },
        "read_model": {
            "overview_observed_at": overview.get("generated_at", NOTION_OVERVIEW_OBSERVED_AT),
            "active_cases": portfolio.get("total_active_cases", 0),
            "callbacks_pending": portfolio.get("callbacks_pending", 0),
            "overdue_followups": portfolio.get("overdue_followups", 0),
            "canvas_count": len(canvases),
            "uses_overview_snapshot": True,
        },
        "update_envelopes": update_envelopes,
        "required_before_update": [
            "Confirm live row query method for Launch Team rows.",
            "Confirm Notion update method and allowed properties.",
            "Confirm property mapping for status, next action, follow-up, QA, MID, and Salesforce case.",
            "Confirm the exact action id with a MAVERICK-CONFIRM notion_status_update token.",
        ],
        "dry_run": {
            "query_attempted": False,
            "update_attempted": False,
            "update_allowed": False,
            "reason": "missing live row query method, update method, property mapping, and confirmation token",
            "gate_timestamp": WRITE_GATE_OBSERVED_AT,
        },
        "external_mutation_attempted": False,
    }


def write_outputs(observed_at: str = NOTION_BRIDGE_OBSERVED_AT) -> dict[str, Any]:
    bridge = build_notion_bridge(observed_at=observed_at)
    NOTION_BRIDGE_PATH.write_text(json.dumps(bridge, indent=2), encoding="utf-8")
    return bridge


def main() -> int:
    bridge = write_outputs()
    print(json.dumps({
        "notion_bridge": str(NOTION_BRIDGE_PATH.relative_to(ROOT)),
        "known_target": bridge["target"]["known_target"],
        "active_cases": bridge["read_model"]["active_cases"],
        "update_allowed": bridge["dry_run"]["update_allowed"],
        "external_mutation_attempted": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
