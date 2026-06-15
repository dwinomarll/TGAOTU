#!/usr/bin/env python3
"""Build a read-only Maverick Cockpit adapter snapshot.

This runner intentionally avoids live external writes. It reads local seed data
and safe legacy config, then emits dashboard-ready JSON.
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from maverick_activation_checklist import ACTIVATION_CHECKLIST_PATH, build_activation_checklist
from maverick_case_adapter import load_sample, normalize_notion_case
from maverick_comms_outbox import OUTBOX_PATH, build_outbox
from maverick_device_access import DEVICE_ACCESS_PATH, build_device_access
from maverick_github_bridge import GITHUB_BRIDGE_PATH, build_github_bridge
from maverick_learning_ledger import LEARNING_LEDGER_PATH, build_learning_ledger
from maverick_notion_bridge import NOTION_BRIDGE_PATH, build_notion_bridge
from maverick_notion_overview import OVERVIEW_PATH, build_notion_overview
from maverick_operating_loop import OPERATING_LOOP_PATH, build_operating_loop
from maverick_slack_bridge import SLACK_BRIDGE_PATH, build_slack_bridge


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "factory" / "active" / "maverick-cockpit"
CONTRACT_PATH = APP_DIR / "adapters" / "adapter-contract.json"
SNAPSHOT_PATH = APP_DIR / "adapters" / "adapter-snapshot.json"
DASHBOARD_DATA_PATH = APP_DIR / "dashboard" / "data" / "maverick-dashboard-data.json"
SNAPSHOT_OBSERVED_AT = "2026-06-14T16:28:44-04:00"
LIVE_TARGETS_PATH = APP_DIR / "live-targets.json"
PACKAGE_MANIFEST_PATH = APP_DIR / "global-repo" / "package-manifest.json"
ASSEMBLY_MANIFEST_PATH = APP_DIR / "global-repo" / "assembly-manifest.json"
TARGET_DISCOVERY_PATH = APP_DIR / "target-discovery.json"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_optional_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return _load_json(path)


def _load_notion_overview() -> dict[str, Any]:
    if OVERVIEW_PATH.exists():
        return _load_json(OVERVIEW_PATH)
    return build_notion_overview()


def _load_operating_loop(overview: dict[str, Any]) -> dict[str, Any]:
    if OPERATING_LOOP_PATH.exists():
        return _load_json(OPERATING_LOOP_PATH)
    return build_operating_loop(overview=overview)


def _load_comms_outbox(operating_loop: dict[str, Any]) -> dict[str, Any]:
    if OUTBOX_PATH.exists():
        return _load_json(OUTBOX_PATH)
    return build_outbox(operating_loop=operating_loop)


def _load_activation_checklist() -> dict[str, Any]:
    if ACTIVATION_CHECKLIST_PATH.exists():
        return _load_json(ACTIVATION_CHECKLIST_PATH)
    return build_activation_checklist()


def _load_learning_ledger() -> dict[str, Any]:
    if LEARNING_LEDGER_PATH.exists():
        return _load_json(LEARNING_LEDGER_PATH)
    return build_learning_ledger()


def _load_slack_bridge() -> dict[str, Any]:
    if SLACK_BRIDGE_PATH.exists():
        return _load_json(SLACK_BRIDGE_PATH)
    return build_slack_bridge()


def _load_github_bridge() -> dict[str, Any]:
    if GITHUB_BRIDGE_PATH.exists():
        return _load_json(GITHUB_BRIDGE_PATH)
    return build_github_bridge()


def _load_notion_bridge() -> dict[str, Any]:
    if NOTION_BRIDGE_PATH.exists():
        return _load_json(NOTION_BRIDGE_PATH)
    return build_notion_bridge()


def _load_device_access() -> dict[str, Any]:
    if DEVICE_ACCESS_PATH.exists():
        return _load_json(DEVICE_ACCESS_PATH)
    return build_device_access()


def _status_slug(normalized: dict[str, Any]) -> str:
    risk_signals = set(normalized["risk"]["signals"])
    next_action = normalized["workflow"]["next_action"]
    if "next_action_escalation" in risk_signals:
        return "escalation"
    if next_action == "Call":
        return "active"
    if next_action == "Email":
        return "follow-ups"
    if normalized["risk"].get("callback"):
        return "callback"
    if normalized["timing"].get("timezone_confidence") == "missing":
        return "needs-tz"
    return "read-only"


def _case_row(normalized: dict[str, Any]) -> dict[str, Any]:
    account = normalized["case"]["account"]
    notes = normalized["workflow"].get("case_notes") or normalized["workflow"].get("action_items") or "Review case context"
    age = normalized["timing"].get("case_age_days")
    status = _status_slug(normalized)
    return {
        "id": normalized["case"]["page_id"][:8],
        "merchant": account,
        "issue": notes,
        "status": status,
        "sla": f"{age}d active" if isinstance(age, int) else "Needs review",
        "update": "Adapter seed",
        "risk": "danger" if normalized["risk"]["risk_level"] in {"high", "critical"} else "warn" if normalized["risk"]["signals"] else "ok",
    }


def _overview_case_rows(overview: dict[str, Any]) -> list[dict[str, Any]]:
    labels = {
        "complete_in_task": ("confirmation", "ready to close"),
        "good": ("active", "cadence"),
        "move_to_active": ("follow-ups", "reactivate"),
        "move_to_hold": ("escalation", "hold decision"),
    }
    rows = []
    for sample in overview.get("case_samples", []):
        lane = sample.get("lane", "active")
        status, update = labels.get(lane, ("active", "review"))
        rows.append({
            "id": sample.get("mid", "MID unknown"),
            "merchant": sample.get("merchant", "Unknown merchant"),
            "issue": sample.get("next", "Review Launch Team record"),
            "status": status,
            "sla": "Notion overview",
            "update": update,
            "risk": "danger" if lane == "move_to_hold" else "warn" if lane in {"move_to_active", "complete_in_task"} else "ok",
        })
    return rows


def _overview_actions(overview: dict[str, Any]) -> list[dict[str, Any]]:
    actions = []
    for item in overview.get("next_action_breakdown", []):
        action = item.get("action", "Review")
        cases = item.get("cases", 0)
        lane = item.get("lane", "active")
        status = {
            "call_stack": "callback",
            "email_stack": "follow-ups",
            "escalation_stack": "escalation",
            "waiting_stack": "confirmation",
        }.get(lane, "active")
        actions.append({
            "title": f"{action}: {cases} cases",
            "detail": f"Route through {lane.replace('_', ' ')}",
            "status": status,
            "time": "Notion",
            "urgent": status == "escalation",
        })
    bot = overview.get("bot") or {}
    actions.append({
        "title": "Confirm bot dispatch guardrails",
        "detail": bot.get("secret_policy", "Keep bot secrets out of artifacts"),
        "status": "confirmation",
        "time": "Gate",
    })
    return actions


def _overview_memory(overview: dict[str, Any]) -> list[dict[str, Any]]:
    reconciliation = overview.get("reconciliation") or {}
    return [
        {
            "merchant": "Portfolio Reconciliation",
            "detail": f"{reconciliation.get('total_accounts', 0)} accounts · {reconciliation.get('move_to_active', 0)} move to active",
            "tag": "Burndown",
        },
        {
            "merchant": "Argo Priority Engine",
            "detail": "P0-P4 lanes with 14-day handling rule",
            "tag": "Bot layer",
        },
        {
            "merchant": "Launch Team Canvases",
            "detail": f"{len(overview.get('canvases') or [])} views mapped for cockpit navigation",
            "tag": "Canvas map",
        },
    ]


def _action(normalized: dict[str, Any]) -> dict[str, Any]:
    account = normalized["case"]["account"]
    next_action = normalized["workflow"].get("next_action") or "Review"
    status = _status_slug(normalized)
    detail = normalized["workflow"].get("action_items") or normalized["workflow"].get("case_notes") or "Confirm the next case move."
    if normalized["timing"].get("timezone_confidence") == "missing":
        status = "needs-tz"
        title = f"Request time zone for {account}"
    elif normalized["risk"].get("callback"):
        status = "callback"
        title = f"Call back {account}"
    else:
        title = f"{next_action} {account}"
    return {"title": title, "detail": detail, "status": status, "time": "Adapter seed"}


def _memory(normalized: dict[str, Any]) -> dict[str, Any]:
    account = normalized["case"]["account"]
    mid = normalized["case"].get("mid") or "MID unknown"
    return {
        "merchant": account,
        "detail": f"{mid} · first seen {normalized['memory']['first_seen'][:10]}",
        "tag": "Ledger seed",
    }


def _load_slack_config(contract: dict[str, Any]) -> dict[str, Any]:
    adapter = next(item for item in contract["adapters"] if item["id"] == "slack_signal_config")
    path = Path(adapter["source"])
    config = _load_json(path)
    return {
        "name": config.get("name"),
        "mode": config.get("mode"),
        "active_window_days": config.get("active_window_days"),
        "channel_count": len(config.get("channels") or []),
        "risk_keyword_count": len((config.get("rules") or {}).get("risk_keywords") or []),
        "never_write_to_slack": bool((config.get("rules") or {}).get("never_write_to_slack")),
        "only_alert_when_active_account_matches": bool((config.get("rules") or {}).get("only_alert_when_active_account_matches")),
    }


def _launch_gates() -> list[dict[str, Any]]:
    live_targets = _load_optional_json(LIVE_TARGETS_PATH)
    target_rows = live_targets.get("targets") or []
    labels = {
        "github": "GitHub",
        "icloud_drive": "iCloud Drive",
        "google_calendar": "Google Calendar",
        "gmail": "Gmail",
        "notion": "Notion",
    }
    gates = []
    for target in target_rows:
        status = target.get("confirmation_status") or "pending"
        system = target.get("system") or target.get("id", "target")
        gates.append({
            "id": target.get("id"),
            "label": labels.get(system, system.replace("_", " ").title()),
            "target": target.get("known_target") or "pending",
            "gate": target.get("write_gate"),
            "status": status,
            "detail": target.get("notes") or "Awaiting confirmation",
        })
    return gates


def _package_status() -> dict[str, Any]:
    package = _load_optional_json(PACKAGE_MANIFEST_PATH)
    assembly = _load_optional_json(ASSEMBLY_MANIFEST_PATH)
    discovery = _load_optional_json(TARGET_DISCOVERY_PATH)
    return {
        "repo": package.get("suggested_repo_name", "maverick-cockpit"),
        "sourceArtifacts": package.get("source_artifact_count", 0),
        "assembledFiles": assembly.get("file_count", 0),
        "publishStatus": package.get("publish_status", "prepared_local_only"),
        "externalMutationAllowed": bool(package.get("external_mutation_allowed")),
        "githubOrigin": (discovery.get("github") or {}).get("current_origin", "pending"),
        "icloudPath": next(
            (
                item.get("path")
                for item in (discovery.get("icloud_drive") or {}).get("candidates", [])
                if item.get("selected")
            ),
            "pending",
        ),
    }


def build_snapshot(observed_at: str | None = None) -> dict[str, Any]:
    now = observed_at or datetime.now(timezone.utc).isoformat()
    contract = _load_json(CONTRACT_PATH)
    raw_sample_path = ROOT / contract["adapters"][0]["source"]
    normalized = normalize_notion_case(load_sample(raw_sample_path), observed_at=now)
    overview = _load_notion_overview()
    operating_loop = _load_operating_loop(overview)
    comms_outbox = _load_comms_outbox(operating_loop)
    activation_checklist = _load_activation_checklist()
    learning_ledger = _load_learning_ledger()
    slack_bridge = _load_slack_bridge()
    github_bridge = _load_github_bridge()
    notion_bridge = _load_notion_bridge()
    device_access = _load_device_access()
    slack = _load_slack_config(contract)

    adapter_status = []
    for adapter in contract["adapters"]:
        status = "ready"
        if adapter["read_policy"] == "pending_access" or adapter["mode"].startswith("pending"):
            status = "pending"
        if adapter["id"] == "icloud_destination":
            status = "destination_registered"
        adapter_status.append({
            "id": adapter["id"],
            "system": adapter["system"],
            "mode": adapter["mode"],
            "read_policy": adapter["read_policy"],
            "write_policy": adapter["write_policy"],
            "status": status,
        })

    case_rows = _overview_case_rows(overview) or [_case_row(normalized)]
    actions = _overview_actions(overview) or [_action(normalized)]
    launch_gates = _launch_gates()
    pending_gates = sum(1 for gate in launch_gates if gate["status"] != "confirmed")
    status_counts = Counter(row["status"] for row in case_rows)
    portfolio = overview.get("portfolio_snapshot") or {}
    reconciliation = overview.get("reconciliation") or {}
    kpis = [
        {"label": "Active Cases", "value": portfolio.get("total_active_cases", status_counts.get("active", 0)), "note": "SHIFT-4 field", "tone": "teal"},
        {"label": "Follow-ups", "value": portfolio.get("overdue_followups", status_counts.get("follow-ups", 0)), "note": "Overdue", "tone": "amber"},
        {"label": "Callback", "value": portfolio.get("callbacks_pending", status_counts.get("callback", 0)), "note": "Pending", "tone": "blue"},
        {"label": "Escalation", "value": 10, "note": "Next action", "tone": "red"},
        {"label": "Canvases", "value": len(overview.get("canvases") or []), "note": "Notion views", "tone": "teal"},
        {"label": "Reconcile", "value": reconciliation.get("total_accounts", 0), "note": "Burndown", "tone": "muted"},
        {"label": "Confirmation required", "value": pending_gates, "note": "Writes gated", "tone": "amber"},
    ]

    dashboard = {
        "kpis": kpis,
        "cases": case_rows,
        "actions": actions,
        "signals": [
            {"icon": "S", "label": "Slack", "detail": f"{slack['channel_count']} watched sources", "count": slack["risk_keyword_count"], "color": "#dc2626"},
            {"icon": "N", "label": "Notion", "detail": "Launch Team overview", "count": portfolio.get("total_active_cases", len(case_rows)), "color": "#111827"},
            {"icon": "B", "label": "Bot", "detail": (overview.get("bot") or {}).get("name", "Argo / Buddy dispatch"), "count": len((overview.get("bot") or {}).get("quick_replies") or []), "color": "#0f766e"},
            {"icon": "G", "label": "Gmail", "detail": "Pending mailbox access", "count": 0, "color": "#1d64d8"},
            {"icon": "C", "label": "Calendar", "detail": "Pending source map", "count": 0, "color": "#c27803"},
        ],
        "memory": _overview_memory(overview) or [_memory(normalized)],
        "calendar": [
            {"time": "Day 0-2", "title": "Acknowledge and define next action", "duration": "14-day rule"},
            {"time": "Day 10-13", "title": "Final acceleration lane", "duration": "before forced decision"},
        ],
        "learning": [
            ["Cases Visible", str(portfolio.get("total_active_cases", len(case_rows))), "Notion"],
            ["Slack Sources", str(slack["channel_count"]), "read-only"],
            ["Bot Replies", str(len((overview.get("bot") or {}).get("quick_replies") or [])), "guarded"],
            ["Package Files", str(_package_status()["assembledFiles"]), "local"],
        ],
        "canvases": overview.get("canvases") or [],
        "botDispatch": overview.get("bot") or {},
        "priorityEngine": overview.get("priority_engine") or [],
        "operatingLoop": {
            "mission": operating_loop.get("mission") or {},
            "dailyCadence": operating_loop.get("daily_cadence") or [],
            "todayObjectives": operating_loop.get("today_objectives") or [],
            "caseLanes": operating_loop.get("case_lanes") or [],
            "pendingConfirmations": operating_loop.get("pending_confirmations") or [],
        },
        "commsOutbox": {
            "slackApp": comms_outbox.get("slack_app") or {},
            "deliveryRules": comms_outbox.get("delivery_rules") or [],
            "drafts": comms_outbox.get("drafts") or [],
        },
        "activationChecklist": {
            "summary": activation_checklist.get("activation_summary") or {},
            "lanes": activation_checklist.get("lanes") or [],
        },
        "learningLedger": {
            "summary": learning_ledger.get("summary") or {},
            "events": learning_ledger.get("learning_events") or [],
            "rejectedMemory": learning_ledger.get("rejected_memory") or [],
        },
        "slackBridge": {
            "app": slack_bridge.get("app") or {},
            "requiredBeforeSend": slack_bridge.get("required_before_send") or [],
            "messageEnvelopes": slack_bridge.get("message_envelopes") or [],
            "dryRun": slack_bridge.get("dry_run") or {},
        },
        "githubBridge": {
            "repository": github_bridge.get("repository") or {},
            "packageEvidence": github_bridge.get("package_evidence") or {},
            "publishEnvelope": github_bridge.get("publish_envelope") or {},
            "requiredBeforePublish": github_bridge.get("required_before_publish") or [],
            "dryRun": github_bridge.get("dry_run") or {},
        },
        "notionBridge": {
            "target": notion_bridge.get("target") or {},
            "readModel": notion_bridge.get("read_model") or {},
            "updateEnvelopes": notion_bridge.get("update_envelopes") or [],
            "requiredBeforeUpdate": notion_bridge.get("required_before_update") or [],
            "dryRun": notion_bridge.get("dry_run") or {},
        },
        "deviceAccess": device_access,
        "launchGates": launch_gates,
        "packageStatus": _package_status(),
        "confirmationRequest": "factory/active/maverick-cockpit/confirmation-request.md",
        "nextDeadline": f"{portfolio.get('overdue_followups', 0)} overdue follow-ups · {portfolio.get('callbacks_pending', 0)} callbacks",
    }

    return {
        "generated_at": now,
        "contract": str(CONTRACT_PATH.relative_to(ROOT)),
        "adapters": adapter_status,
        "slack": slack,
        "notion_overview": overview,
        "operating_loop": operating_loop,
        "communication_outbox": comms_outbox,
        "activation_checklist": activation_checklist,
        "learning_ledger": learning_ledger,
        "slack_bridge": slack_bridge,
        "github_bridge": github_bridge,
        "notion_bridge": notion_bridge,
        "device_access": device_access,
        "normalized_cases": [normalized],
        "dashboard": dashboard,
    }


def write_snapshot(snapshot: dict[str, Any]) -> None:
    SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    DASHBOARD_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    SNAPSHOT_PATH.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    DASHBOARD_DATA_PATH.write_text(json.dumps(snapshot["dashboard"], indent=2), encoding="utf-8")


def main() -> int:
    snapshot = build_snapshot(observed_at=SNAPSHOT_OBSERVED_AT)
    write_snapshot(snapshot)
    print(json.dumps({
        "snapshot": str(SNAPSHOT_PATH.relative_to(ROOT)),
        "dashboard_data": str(DASHBOARD_DATA_PATH.relative_to(ROOT)),
        "adapters": len(snapshot["adapters"]),
        "cases": len(snapshot["normalized_cases"]),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
