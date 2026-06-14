#!/usr/bin/env python3
"""Normalize Launch Team Notion rows into the Maverick workplace case contract."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _prop(page: dict[str, Any], name: str) -> dict[str, Any]:
    prop = (page.get("properties") or {}).get(name)
    return prop if isinstance(prop, dict) else {}


def _title(page: dict[str, Any], name: str = "Accounts") -> str:
    value = _prop(page, name).get("title") or []
    return "".join(part.get("plain_text", "") for part in value if isinstance(part, dict)).strip()


def _rich_text(page: dict[str, Any], name: str) -> str | None:
    value = _prop(page, name).get("rich_text") or []
    text = "".join(part.get("plain_text", "") for part in value if isinstance(part, dict)).strip()
    return text or None


def _select(page: dict[str, Any], name: str) -> str | None:
    value = _prop(page, name).get("select")
    return value.get("name") if isinstance(value, dict) else None


def _status(page: dict[str, Any], name: str) -> str | None:
    value = _prop(page, name).get("status")
    return value.get("name") if isinstance(value, dict) else None


def _multi(page: dict[str, Any], name: str) -> list[str]:
    value = _prop(page, name).get("multi_select") or []
    return [item.get("name") for item in value if isinstance(item, dict) and item.get("name")]


def _checkbox(page: dict[str, Any], name: str) -> bool | None:
    prop = _prop(page, name)
    if "checkbox" in prop:
        return bool(prop.get("checkbox"))
    formula = prop.get("formula")
    if isinstance(formula, dict) and formula.get("type") == "boolean":
        return bool(formula.get("boolean"))
    return None


def _number(page: dict[str, Any], name: str) -> int | None:
    prop = _prop(page, name)
    if prop.get("type") == "number" and prop.get("number") is not None:
        return int(prop["number"])
    formula = prop.get("formula")
    if isinstance(formula, dict) and formula.get("type") == "number" and formula.get("number") is not None:
        return int(formula["number"])
    rollup = prop.get("rollup")
    if isinstance(rollup, dict) and rollup.get("type") == "number" and rollup.get("number") is not None:
        return int(rollup["number"])
    return None


def _date_value(page: dict[str, Any], name: str) -> str | None:
    prop = _prop(page, name)
    if prop.get("type") == "created_time":
        return prop.get("created_time")
    if prop.get("type") == "last_edited_time":
        return prop.get("last_edited_time")
    value = prop.get("date")
    return value.get("start") if isinstance(value, dict) else None


def _email(page: dict[str, Any], name: str) -> str | None:
    value = _prop(page, name).get("email")
    return value or None


def _phone(page: dict[str, Any], name: str) -> str | None:
    value = _prop(page, name).get("phone_number")
    return value or None


def normalize_notion_case(page: dict[str, Any], *, observed_at: str | None = None) -> dict[str, Any]:
    """Return one case in the Maverick workplace schema shape.

    The adapter never invents never-guess fields. Missing MID, contact data,
    Salesforce case, or location id stay null.
    """
    now = observed_at or datetime.now(timezone.utc).isoformat()
    account = _title(page) or page.get("id") or "unknown-account"
    age = _number(page, "Case Age")
    phase = _rich_text(page, "Case Phase") or _select(page, "Case Phase")
    next_action = _select(page, "Next Action")
    outcomes = _multi(page, "Outcome / Current Status")
    signals: list[str] = []

    if next_action in {"Escalate", "Escalate SkyTab Online"}:
        signals.append("next_action_escalation")
    if age is not None and age >= 14:
        signals.append("day14_wall")
    if _checkbox(page, "Open Loop"):
        signals.append("open_loop")
    if _checkbox(page, "Call Back"):
        signals.append("callback")

    risk_level = "unknown"
    if "next_action_escalation" in signals or "day14_wall" in signals:
        risk_level = "high"
    elif signals:
        risk_level = "medium"
    elif age is not None:
        risk_level = "low"

    return {
        "case": {
            "page_id": page.get("id") or "",
            "account": account,
            "business_name": _rich_text(page, "Business Name"),
            "dba": _rich_text(page, "DBA"),
            "mid": _rich_text(page, "MID"),
            "location_id": _rich_text(page, "Location ID*"),
            "salesforce_case": _rich_text(page, "Salesforce Case #"),
            "language": _select(page, "Language "),
        },
        "workflow": {
            "task_status": _status(page, "Task Status"),
            "next_action": next_action,
            "outcome_status": outcomes,
            "action_items": _rich_text(page, "Action Items"),
            "case_notes": _rich_text(page, "Case notes:"),
            "feedback": _rich_text(page, "Feedback"),
        },
        "timing": {
            "created_at": _date_value(page, "Date"),
            "case_age_days": age,
            "case_phase": phase,
            "next_follow_up": _date_value(page, "Next Follow-up"),
            "last_contact": _date_value(page, "Last Contact"),
            "timezone": _rich_text(page, "Timezone"),
            "timezone_confidence": "missing" if not _rich_text(page, "Timezone") else "low",
        },
        "risk": {
            "risk_level": risk_level,
            "qa_score": _select(page, "QA Score"),
            "open_loop": _checkbox(page, "Open Loop"),
            "no_answer": _checkbox(page, "No Answer"),
            "callback": _checkbox(page, "Call Back"),
            "signals": signals,
        },
        "memory": {
            "first_seen": now,
            "last_seen": now,
            "last_change": None,
            "events": [
                {
                    "at": now,
                    "kind": "observed",
                    "summary": "Normalized from Launch Team source row.",
                }
            ],
            "confidence_notes": "Never-guess fields remain null when absent.",
        },
        "source": {
            "system": "notion",
            "source_id": page.get("id"),
            "source_url": page.get("url"),
            "read_policy": "allowed",
            "write_policy": "confirmation_required",
        },
    }


def load_sample(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    sample = root / "factory" / "active" / "maverick-cockpit" / "samples" / "notion-case.json"
    normalized = normalize_notion_case(load_sample(sample), observed_at="2026-06-14T16:15:58-04:00")
    print(json.dumps(normalized, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
