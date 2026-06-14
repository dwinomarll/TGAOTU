#!/usr/bin/env python3
"""Build a read-only Notion overview for Maverick Cockpit.

The Notion SQL query surface is not available in this session, so this module
captures the verified page/database facts fetched from the Shift4 workspace.
It is deliberately local-only and does not mutate Notion.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "factory" / "active" / "maverick-cockpit"
OVERVIEW_PATH = APP_DIR / "notion-overview.json"
NOTION_OVERVIEW_OBSERVED_AT = "2026-06-14T17:08:36-04:00"


def build_notion_overview(observed_at: str = NOTION_OVERVIEW_OBSERVED_AT) -> dict[str, Any]:
    return {
        "generated_at": observed_at,
        "source_policy": {
            "mode": "read_only_fetch_snapshot",
            "notion_query_data_sources": "unavailable: notion-query-data-sources not found",
            "external_mutation_attempted": False,
            "personal_contact_fields_excluded_from_dashboard": True,
        },
        "sources": [
            {
                "id": "shift4_page",
                "title": "SHIFT-4",
                "url": "https://app.notion.com/p/1996ae29a07c801ba98ec12c0415ba21",
                "evidence": "Portfolio Snapshot and REFERENCES section",
            },
            {
                "id": "launch_team",
                "title": "Launch Team",
                "url": "https://app.notion.com/p/2106ae29a07c81dda782c482d020c533",
                "data_source": "collection://2106ae29-a07c-81cb-9c6e-000ba25c1f45",
                "evidence": "database schema and views",
            },
            {
                "id": "argo_environment",
                "title": "Argo Shift4 Dine Environment",
                "url": "https://app.notion.com/p/3716ae29a07c818f8b64c8a28fea4dbf",
                "evidence": "bot dispatch, priority engine, 14-day rule, first build checklist",
            },
            {
                "id": "portfolio_reconciliation",
                "title": "Portfolio Reconciliation - 2026-04-22",
                "url": "https://app.notion.com/p/08a172aab28548abba3dec346ea06cf5",
                "evidence": "172-account reconciliation and burndown buckets",
            },
            {
                "id": "burndown_board",
                "title": "Burndown Sheet Operations Board",
                "url": "https://app.notion.com/p/4b75c8244fb34ea5a7775c5089c8cfa4",
                "evidence": "close/good/move-active/hold account lists",
            },
            {
                "id": "buddy_mainframe",
                "title": "Buddy Mainframe",
                "url": "https://app.notion.com/p/2f76ae29a07c80a2bc10c0ff048cc3c2",
                "evidence": "Launch Team board grouped by Task Status",
            },
        ],
        "portfolio_snapshot": {
            "source": "SHIFT-4 page Portfolio Snapshot",
            "total_active_cases": 120,
            "callbacks_pending": 37,
            "overdue_followups": 22,
            "resolved_but_open_task": 12,
        },
        "next_action_breakdown": [
            {"action": "Call", "cases": 30, "lane": "call_stack"},
            {"action": "Escalate", "cases": 10, "lane": "escalation_stack"},
            {"action": "Waiting on Internal Team", "cases": 48, "lane": "waiting_stack"},
            {"action": "Waiting on Merchant", "cases": 29, "lane": "waiting_stack"},
            {"action": "Email", "cases": 3, "lane": "email_stack"},
        ],
        "reconciliation": {
            "source": "Portfolio Reconciliation - 2026-04-22",
            "total_accounts": 172,
            "good": 50,
            "complete_in_task": 15,
            "move_to_active": 103,
            "move_to_hold": 4,
            "total_error": 122,
            "error_rate": "70.93%",
            "missed_launch": "59.54%",
            "source_discrepancy": "Burndown notes mention 173 total; reconciliation resolves parsed rows to 172.",
        },
        "case_samples": [
            {"mid": "0022990331", "merchant": "BROTHERS BURGERS", "lane": "complete_in_task", "next": "Close in Launch Team"},
            {"mid": "0022997740", "merchant": "EL VADO MEXICAN RESTAURANT", "lane": "good", "next": "Maintain light-touch cadence"},
            {"mid": "0022885556", "merchant": "HARDENS HAMBURGERS MATHIS", "lane": "move_to_active", "next": "Re-engage and promote to active"},
            {"mid": "0022889186", "merchant": "DEJAVU BAR & LIVE MUSIC", "lane": "move_to_active", "next": "Re-engage and promote to active"},
            {"mid": "0022781078", "merchant": "ALL AMERICAN SMASH WAGON", "lane": "move_to_hold", "next": "Confirm hold reason"},
        ],
        "canvases": [
            {"name": "Mainframe", "type": "board", "purpose": "Group Launch Team work by Task Status"},
            {"name": "Follow-ups", "type": "table", "purpose": "Next Follow-up due today through one week"},
            {"name": "Callback", "type": "table", "purpose": "Call Back checked cases"},
            {"name": "Launch Pad", "type": "table", "purpose": "Command view for check-in and action planning"},
            {"name": "QA Breakdown", "type": "board", "purpose": "Group work by QA Score"},
            {"name": "Map Coverage", "type": "map", "purpose": "Location coverage from Launch Team places"},
            {"name": "Observation Bin", "type": "table", "purpose": "Aging cases from one week to one month"},
            {"name": "Archive Ready", "type": "table", "purpose": "Older unresolved cases needing final decision"},
        ],
        "bot": {
            "name": "Argo / Buddy dispatch",
            "mission": "Rank open loops, overdue work, callbacks, escalations, and QA-ready closures before Edwin spends energy.",
            "target": "reduce active cases to 50 or fewer while keeping every case inside a 14-day handling window",
            "daily_intake_expectation": "5+ new cases plus escalations and emails",
            "quick_replies": [
                "Acknowledge",
                "Reply Gmail",
                "Search Similar",
                "Escalate",
                "Nudge Merchant",
                "Create RMA",
                "Mark Waiting",
                "QA",
                "Resolve",
                "Park",
            ],
            "secret_policy": "Bot token must live in a secret store, never in Notion or transcripts.",
        },
        "priority_engine": [
            {"level": "P0", "name": "Critical", "trigger": "payment outage, merchant blocked, cancellation risk, same-day escalation, or VIP urgent impact"},
            {"level": "P1", "name": "Aging", "trigger": "10+ days with no movement, overdue follow-up, open loop, or escalation pending"},
            {"level": "P2", "name": "Active Work", "trigger": "equipment, RMA, technician, menu, tax, training, network, or support workflow"},
            {"level": "P3", "name": "Waiting", "trigger": "waiting on merchant, internal team, tech, parts, or external response"},
            {"level": "P4", "name": "QA/Close", "trigger": "resolved, transition-ready, archive-ready, or final quality check"},
        ],
        "handling_rule": {
            "window_days": 14,
            "day_0_2": "acknowledge and define next action",
            "day_3_6": "nudge if no movement; update follow-up date",
            "day_7_9": "review for escalation or blocker",
            "day_10_13": "final acceleration lane",
            "day_14": "forced decision: resolve, escalate, RMA/tech path, or park with explicit blocker",
        },
    }


def write_outputs(observed_at: str = NOTION_OVERVIEW_OBSERVED_AT) -> dict[str, Any]:
    overview = build_notion_overview(observed_at=observed_at)
    OVERVIEW_PATH.write_text(json.dumps(overview, indent=2), encoding="utf-8")
    return overview


def main() -> int:
    overview = write_outputs()
    print(json.dumps({
        "notion_overview": str(OVERVIEW_PATH.relative_to(ROOT)),
        "active_cases": overview["portfolio_snapshot"]["total_active_cases"],
        "canvases": len(overview["canvases"]),
        "bot": overview["bot"]["name"],
        "external_mutation_attempted": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
