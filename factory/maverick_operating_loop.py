#!/usr/bin/env python3
"""Build Maverick's local daily operating loop.

The loop turns the verified Notion overview, bot policy, and live-target gates
into a concrete work rhythm. It is local-only: no Notion, Slack, Gmail,
Calendar, GitHub, or iCloud mutation is attempted here.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from maverick_notion_overview import OVERVIEW_PATH, build_notion_overview


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "factory" / "active" / "maverick-cockpit"
OPERATING_LOOP_PATH = APP_DIR / "operating-loop.json"
LIVE_TARGETS_PATH = APP_DIR / "live-targets.json"
OPERATING_LOOP_OBSERVED_AT = "2026-06-14T18:29:18-04:00"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_overview() -> dict[str, Any]:
    if OVERVIEW_PATH.exists():
        return _load_json(OVERVIEW_PATH)
    return build_notion_overview()


def _load_live_targets() -> dict[str, Any]:
    if LIVE_TARGETS_PATH.exists():
        return _load_json(LIVE_TARGETS_PATH)
    return {"targets": []}


def _gate_summary(live_targets: dict[str, Any]) -> list[dict[str, str]]:
    summary = []
    for target in live_targets.get("targets", []):
        summary.append({
            "id": target.get("id", "unknown_target"),
            "system": target.get("system", "unknown"),
            "status": target.get("confirmation_status", "pending"),
            "gate": target.get("write_gate", "confirmation_required"),
            "next_confirmation": "; ".join(target.get("evidence_required", [])[:2]) or "confirm owner and access method",
        })
    return summary


def _canvas_route(canvas: dict[str, Any]) -> dict[str, str]:
    name = canvas.get("name", "Unknown")
    purpose = canvas.get("purpose", "Review this Notion view")
    use_when = {
        "Mainframe": "start-of-day triage by Task Status",
        "Follow-ups": "due today, overdue, and one-week follow-up sweep",
        "Callback": "call block planning and callback recovery",
        "Launch Pad": "case check-in and next-action planning",
        "QA Breakdown": "same-day QA, resolved-but-open, and close-readiness checks",
        "Map Coverage": "location-aware dispatch and coverage questions",
        "Observation Bin": "aging cases that need a stronger decision",
        "Archive Ready": "final close, park, or escalation decision",
    }.get(name, purpose)
    return {"name": name, "type": canvas.get("type", "view"), "use_when": use_when}


def build_operating_loop(
    overview: dict[str, Any] | None = None,
    live_targets: dict[str, Any] | None = None,
    observed_at: str = OPERATING_LOOP_OBSERVED_AT,
) -> dict[str, Any]:
    overview = overview or _load_overview()
    live_targets = live_targets or _load_live_targets()
    portfolio = overview.get("portfolio_snapshot") or {}
    reconciliation = overview.get("reconciliation") or {}
    bot = overview.get("bot") or {}
    handling = overview.get("handling_rule") or {}
    gates = _gate_summary(live_targets)
    pending_gates = [gate for gate in gates if gate["status"] != "confirmed"]

    return {
        "generated_at": observed_at,
        "source_policy": {
            "mode": "local_operating_loop",
            "notion_row_query": (overview.get("source_policy") or {}).get("notion_query_data_sources", "unavailable"),
            "slack_policy": "legacy_watch_read_only_maverick_app_writes_gated",
            "external_mutation_attempted": False,
        },
        "mission": {
            "name": "Maverick daily command",
            "target": bot.get("target", "reduce active case risk while protecting the 14-day window"),
            "active_cases": portfolio.get("total_active_cases", 0),
            "desired_active_cases": 50,
            "window_days": handling.get("window_days", 14),
            "success_signal": "lower overdue follow-ups, callbacks, and unresolved open loops before adding new work",
        },
        "daily_cadence": [
            {
                "step": 1,
                "name": "Read the field",
                "dashboard_zone": "Mission Control",
                "decision": f"{portfolio.get('total_active_cases', 0)} active cases, {portfolio.get('overdue_followups', 0)} overdue follow-ups, {portfolio.get('callbacks_pending', 0)} callbacks",
                "exit_condition": "top risk lane is chosen before opening new work",
            },
            {
                "step": 2,
                "name": "Route through canvases",
                "dashboard_zone": "Canvas Map",
                "decision": "use Launch Team views as navigation, not as hidden context",
                "exit_condition": "each action points to a specific canvas or local evidence file",
            },
            {
                "step": 3,
                "name": "Dispatch guarded bot actions",
                "dashboard_zone": "Bot Dispatch",
                "decision": "quick replies can plan, draft, search, or classify; external effects stay gated",
                "exit_condition": "no write/send/update occurs without a matching confirmation token",
            },
            {
                "step": 4,
                "name": "Close the loop",
                "dashboard_zone": "Learning Loop",
                "decision": "record only memory that changes the next decision",
                "exit_condition": "case state, blocker, next action, and due window are explicit",
            },
        ],
        "today_objectives": [
            {
                "id": "protect_14_day_window",
                "priority": "P1 Aging",
                "metric": f"{portfolio.get('overdue_followups', 0)} overdue follow-ups",
                "action": "work overdue and day-10-to-13 cases before low-risk new tasks",
            },
            {
                "id": "clear_callbacks",
                "priority": "P2 Active Work",
                "metric": f"{portfolio.get('callbacks_pending', 0)} callbacks pending",
                "action": "batch callbacks through the Callback canvas and capture next follow-up",
            },
            {
                "id": "resolve_false_closure",
                "priority": "P4 QA/Close",
                "metric": f"{portfolio.get('resolved_but_open_task', 0)} resolved-but-open tasks",
                "action": "confirm QA or final blocker before marking work closed",
            },
            {
                "id": "reactivate_burndown",
                "priority": "P1 Aging",
                "metric": f"{reconciliation.get('move_to_active', 0)} accounts marked move to active",
                "action": "pull reactivation candidates into active case review without copying stale rows wholesale",
            },
        ],
        "case_lanes": [
            {
                "lane": item.get("action", "Review"),
                "count": item.get("cases", 0),
                "priority": "P0/P1" if item.get("action") == "Escalate" else "P2/P3",
                "rule": f"route through {item.get('lane', 'active').replace('_', ' ')}",
            }
            for item in overview.get("next_action_breakdown", [])
        ],
        "canvas_routes": [_canvas_route(canvas) for canvas in overview.get("canvases", [])],
        "bot_dispatch": {
            "name": bot.get("name", "Argo / Buddy dispatch"),
            "allowed_quick_replies": bot.get("quick_replies", []),
            "guardrail": bot.get("secret_policy", "Secrets must stay out of transcripts."),
            "external_effects": "Notion updates, Slack app messages, Gmail sends, Calendar mutations, GitHub publish, and iCloud export require confirmation gates.",
        },
        "learning_loop": {
            "capture": [
                "new blocker",
                "merchant preference",
                "confirmed next action",
                "due window change",
                "resolution pattern that applies to future cases",
            ],
            "ignore": [
                "personal contact details",
                "unverified assumptions",
                "Slack chatter without active-account match",
                "secrets or bot tokens",
            ],
            "promotion_rule": "promote a note only when it changes routing, priority, or the next useful action.",
        },
        "confirmation_gates": gates,
        "pending_confirmations": [gate["id"] for gate in pending_gates],
        "dashboard_ready": True,
        "external_mutation_attempted": False,
    }


def write_outputs(observed_at: str = OPERATING_LOOP_OBSERVED_AT) -> dict[str, Any]:
    loop = build_operating_loop(observed_at=observed_at)
    OPERATING_LOOP_PATH.write_text(json.dumps(loop, indent=2), encoding="utf-8")
    return loop


def main() -> int:
    loop = write_outputs()
    print(json.dumps({
        "operating_loop": str(OPERATING_LOOP_PATH.relative_to(ROOT)),
        "active_cases": loop["mission"]["active_cases"],
        "daily_objectives": len(loop["today_objectives"]),
        "canvas_routes": len(loop["canvas_routes"]),
        "pending_confirmations": len(loop["pending_confirmations"]),
        "external_mutation_attempted": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
