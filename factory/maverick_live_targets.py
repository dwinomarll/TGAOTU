#!/usr/bin/env python3
"""Discover local Maverick live-target candidates without confirming them."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "factory" / "active" / "maverick-cockpit"
LIVE_TARGETS_PATH = APP_DIR / "live-targets.json"
DISCOVERY_PATH = APP_DIR / "target-discovery.json"
CONFIRMATION_REQUEST_PATH = APP_DIR / "confirmation-request.md"
LIVE_TARGET_DISCOVERED_AT = "2026-06-14T16:37:38-04:00"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)


def _git_remote() -> str | None:
    result = _run(["git", "config", "--get", "remote.origin.url"])
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def _gh_available() -> dict[str, Any]:
    path_result = _run(["sh", "-lc", "command -v gh"])
    auth_result = _run(["gh", "auth", "status", "--hostname", "github.com"])
    return {
        "cli_present": path_result.returncode == 0,
        "cli_path": path_result.stdout.strip() if path_result.returncode == 0 else None,
        "authenticated": auth_result.returncode == 0,
        "auth_output_recorded": False,
        "secret_policy": "Do not store gh auth output, tokens, scopes, or credential paths in Maverick artifacts.",
    }


def _icloud_candidates() -> list[dict[str, Any]]:
    home = Path(os.environ.get("HOME", ""))
    candidates = [
        home / "Library" / "Mobile Documents" / "com~apple~CloudDocs",
        home / "Library" / "Mobile Documents",
        home / "iCloud Drive",
    ]
    return [
        {
            "path": str(path),
            "exists": path.exists(),
            "is_dir": path.is_dir(),
            "selected": path.exists() and path.name == "com~apple~CloudDocs",
        }
        for path in candidates
    ]


def build_discovery(observed_at: str = LIVE_TARGET_DISCOVERED_AT) -> dict[str, Any]:
    live_targets = _load_json(LIVE_TARGETS_PATH)
    return {
        "generated_at": observed_at,
        "live_targets": str(LIVE_TARGETS_PATH.relative_to(ROOT)),
        "external_mutation_attempted": False,
        "confirmation_status_changed": False,
        "github": {
            "current_origin": _git_remote(),
            "candidate_repo": "dwinomarll/maverick-cockpit",
            "candidate_branch": "codex/maverick-cockpit",
            "candidate_publish_mode": "pull_request_or_new_private_repo",
            "gh": _gh_available(),
            "write_gate": "github_publish",
        },
        "icloud_drive": {
            "provided_url": "https://www.icloud.com/iclouddrive/09dTCQP4Zljf2MEc0fPTBGyGA",
            "candidates": _icloud_candidates(),
            "write_gate": "icloud_artifact_export",
        },
        "notion": {
            "candidate_collection": "collection://2106ae29-a07c-81cb-9c6e-000ba25c1f45",
            "row_query_status": "unavailable_in_current_tooling",
            "write_gate": "notion_status_update",
        },
        "gmail": {
            "candidate_mailbox": None,
            "access_status": "pending_user_or_connector_confirmation",
            "write_gate": "gmail_send",
        },
        "slack": {
            "candidate_app_id": "A0BALRB6CNQ",
            "communication_target": None,
            "access_status": "pending_channel_or_dm_and_secret_confirmation",
            "legacy_watch_policy": "read_only",
            "write_gate": "slack_write",
        },
        "google_calendar": {
            "candidate_calendar": None,
            "access_status": "pending_user_or_connector_confirmation",
            "write_gate": "google_calendar_update",
        },
        "pending_target_ids": [
            target["id"]
            for target in live_targets["targets"]
            if target.get("confirmation_status") != "confirmed"
        ],
    }


def build_confirmation_request(discovery: dict[str, Any]) -> str:
    selected_icloud = next(
        (item["path"] for item in discovery["icloud_drive"]["candidates"] if item["selected"]),
        "no local iCloud Drive candidate selected",
    )
    return f"""# Maverick Live Target Confirmation Request

Generated: {discovery["generated_at"]}

Maverick has prepared local artifacts and discovered candidate targets. Nothing
has been pushed, uploaded, sent, scheduled, posted, or updated externally.

## Candidate Targets

| Target | Candidate | Required gate |
|---|---|---|
| GitHub repo | `{discovery["github"]["candidate_repo"]}` from origin `{discovery["github"]["current_origin"]}` | `github_publish` |
| GitHub branch | `{discovery["github"]["candidate_branch"]}` | `github_publish` |
| Publish mode | `{discovery["github"]["candidate_publish_mode"]}` | `github_publish` |
| iCloud local path | `{selected_icloud}` | `icloud_artifact_export` |
| iCloud web destination | `{discovery["icloud_drive"]["provided_url"]}` | `icloud_artifact_export` |
| Notion collection | `{discovery["notion"]["candidate_collection"]}` | `notion_status_update` |
| Gmail mailbox | pending | `gmail_send` |
| Slack Maverick app | `{discovery["slack"]["candidate_app_id"]}` | `slack_write` |
| Google Calendar | pending | `google_calendar_update` |

## Confirmation Tokens

To publish Maverick to GitHub, confirm an action id and use:

`MAVERICK-CONFIRM github_publish <action_id>`

To export Maverick artifacts to iCloud, confirm an action id and use:

`MAVERICK-CONFIRM icloud_artifact_export <action_id>`

To enable Notion writes, Gmail sends, Slack app messages, or Calendar updates,
confirm each target and action separately. The legacy Slack signal watch remains
read-only.

## Still Pending

{chr(10).join(f"- `{target_id}`" for target_id in discovery["pending_target_ids"])}
"""


def write_outputs(observed_at: str = LIVE_TARGET_DISCOVERED_AT) -> dict[str, Any]:
    discovery = build_discovery(observed_at=observed_at)
    DISCOVERY_PATH.write_text(json.dumps(discovery, indent=2), encoding="utf-8")
    CONFIRMATION_REQUEST_PATH.write_text(build_confirmation_request(discovery), encoding="utf-8")
    return discovery


def main() -> int:
    discovery = write_outputs()
    print(json.dumps({
        "target_discovery": str(DISCOVERY_PATH.relative_to(ROOT)),
        "confirmation_request": str(CONFIRMATION_REQUEST_PATH.relative_to(ROOT)),
        "github_origin": discovery["github"]["current_origin"],
        "icloud_candidate_count": len(discovery["icloud_drive"]["candidates"]),
        "external_mutation_attempted": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
