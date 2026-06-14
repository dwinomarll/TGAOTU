#!/usr/bin/env python3
"""Validate the Maverick Cockpit bootstrap artifacts.

This intentionally avoids non-stdlib dependencies. It checks the active build
contract, schema JSON, and key source references so Phase 1 can be proven even
when live Notion row queries are unavailable.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from maverick_activation_checklist import ACTIVATION_CHECKLIST_OBSERVED_AT, ACTIVATION_CHECKLIST_PATH, build_activation_checklist  # noqa: E402
from maverick_adapters import SNAPSHOT_OBSERVED_AT, build_snapshot  # noqa: E402
from maverick_assemble_repo import GLOBAL_REPO_ASSEMBLED_AT, assemble_package  # noqa: E402
from maverick_case_adapter import normalize_notion_case  # noqa: E402
from maverick_comms_outbox import COMMS_OUTBOX_OBSERVED_AT, OUTBOX_PATH, build_outbox  # noqa: E402
from maverick_confirm_target import CONFIRMATION_ACTION_ID, build_confirmed_targets, evaluate_confirmation  # noqa: E402
from maverick_export_icloud import (
    DEFAULT_DESTINATION_ROOT,
    DESTINATION_PACKAGE_NAME,
    EXPORT_MANIFEST_PATH as ICLOUD_EXPORT_MANIFEST_PATH,
    ICLOUD_EXPORT_ACTION_ID,
    PRESERVED_TOP_LEVEL_ITEMS,
    WORKFLOW_HANDOFF_NAME,
)  # noqa: E402
from maverick_global_repo import GLOBAL_REPO_OBSERVED_AT, build_package_manifest  # noqa: E402
from maverick_github_bridge import GITHUB_BRIDGE_OBSERVED_AT, GITHUB_BRIDGE_PATH, build_github_bridge  # noqa: E402
from maverick_learning_ledger import LEARNING_LEDGER_OBSERVED_AT, LEARNING_LEDGER_PATH, build_learning_ledger  # noqa: E402
from maverick_notion_bridge import NOTION_BRIDGE_OBSERVED_AT, NOTION_BRIDGE_PATH, build_notion_bridge  # noqa: E402
from maverick_live_targets import LIVE_TARGET_DISCOVERED_AT, build_discovery  # noqa: E402
from maverick_notion_overview import NOTION_OVERVIEW_OBSERVED_AT, OVERVIEW_PATH as NOTION_OVERVIEW_PATH, build_notion_overview  # noqa: E402
from maverick_operating_loop import OPERATING_LOOP_OBSERVED_AT, OPERATING_LOOP_PATH, build_operating_loop  # noqa: E402
from maverick_slack_bridge import SLACK_BRIDGE_OBSERVED_AT, SLACK_BRIDGE_PATH, build_slack_bridge  # noqa: E402
from maverick_write_gates import WRITE_GATE_OBSERVED_AT, assess_gate, build_export_manifest  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "factory" / "active" / "maverick-cockpit"

REQUIRED_FILES = [
    ROOT / "docs" / "maverick-cockpit.md",
    APP_DIR / "VISION.md",
    APP_DIR / "BLUEPRINT.md",
    APP_DIR / "BUILD_STATE.json",
    ROOT / "factory" / "schemas" / "maverick-workplace.schema.json",
]

REQUIRED_BLUEPRINT_TERMS = [
    "collection://2106ae29-a07c-81cb-9c6e-000ba25c1f45",
    "Slack read-only watch",
    "Gmail read/draft lane",
    "Google Calendar read lane",
    "iCloud Drive destination",
    "confirmation-gated",
]

REQUIRED_DOC_TERMS = [
    "notion-query-data-sources not found",
    "legacy Slack signal watch remains read-only",
    "A0BALRB6CNQ",
    "Merchant Memory",
    "Email Intelligence",
    "Calendar Guard",
    "iCloud Drive",
]

SOURCE_MAP_PATH = APP_DIR / "source-map.json"
SOURCE_MAP_DOC = ROOT / "docs" / "maverick-source-map.md"
VALID_MIGRATION_ROLES = {"copy_now", "copy_later", "reference", "rebuild", "retire", "blocked"}
REQUIRED_SOURCE_IDS = {
    "doctrine",
    "sop",
    "v2_requirements",
    "v2_gap_analysis",
    "launch_team_property_map",
    "agent_property_bindings",
    "satellite_contract",
    "base_module",
    "casebook_module",
    "timing_module",
    "accountability_module",
    "escalation_module",
    "slack_watch_runbook",
    "slack_watch_config",
    "email_reference",
    "merchant_outreach",
    "legacy_interfaces",
    "runtime_state",
    "icloud_destination",
    "gmail_connector",
    "google_calendar_connector",
}
LEDGER_CONTRACT_PATH = APP_DIR / "ledger-contract.json"
LEDGER_DOC = ROOT / "docs" / "maverick-ledger.md"
RAW_SAMPLE_PATH = APP_DIR / "samples" / "notion-case.json"
NORMALIZED_SAMPLE_PATH = APP_DIR / "samples" / "normalized-case.json"
DASHBOARD_DIR = APP_DIR / "dashboard"
DASHBOARD_FILES = [
    DASHBOARD_DIR / "index.html",
    DASHBOARD_DIR / "styles.css",
    DASHBOARD_DIR / "app.js",
    APP_DIR / "design" / "dashboard-concept.png",
]
ADAPTER_CONTRACT_PATH = APP_DIR / "adapters" / "adapter-contract.json"
ADAPTER_SNAPSHOT_PATH = APP_DIR / "adapters" / "adapter-snapshot.json"
DASHBOARD_DATA_PATH = APP_DIR / "dashboard" / "data" / "maverick-dashboard-data.json"
ADAPTER_DOC = ROOT / "docs" / "maverick-adapters.md"
WRITE_GATE_CONTRACT_PATH = APP_DIR / "write-gates" / "write-gate-contract.json"
EXPORT_MANIFEST_PATH = APP_DIR / "write-gates" / "export-manifest.json"
AUDIT_LOG_PATH = APP_DIR / "write-gates" / "audit-log.ndjson"
WRITE_GATE_DOC = ROOT / "docs" / "maverick-write-gates.md"
LIVE_TARGETS_PATH = APP_DIR / "live-targets.json"
LIVE_TARGETS_DOC = ROOT / "docs" / "maverick-live-targets.md"
GLOBAL_REPO_CONTRACT_PATH = APP_DIR / "global-repo" / "repo-contract.json"
GLOBAL_REPO_README_PATH = APP_DIR / "global-repo" / "README.md"
GLOBAL_REPO_MANIFEST_PATH = APP_DIR / "global-repo" / "package-manifest.json"
GLOBAL_REPO_ASSEMBLY_MANIFEST_PATH = APP_DIR / "global-repo" / "assembly-manifest.json"
GLOBAL_REPO_PACKAGE_DIR = APP_DIR / "global-repo" / "package"
GLOBAL_REPO_DOC = ROOT / "docs" / "maverick-global-repo.md"
REPO_ASSEMBLY_DOC = ROOT / "docs" / "maverick-repo-assembly.md"
TARGET_DISCOVERY_PATH = APP_DIR / "target-discovery.json"
CONFIRMATION_REQUEST_PATH = APP_DIR / "confirmation-request.md"
TARGET_DISCOVERY_DOC = ROOT / "docs" / "maverick-target-discovery.md"
CONFIRMATION_APPLIER_DOC = ROOT / "docs" / "maverick-confirmation-applier.md"
ICLOUD_EXPORT_DOC = ROOT / "docs" / "maverick-icloud-export.md"
MAVERICK_WORKFLOW_DOC = ROOT / "docs" / "maverick-workflow.md"
NOTION_OVERVIEW_DOC = ROOT / "docs" / "maverick-notion-overview.md"
OPERATING_LOOP_DOC = ROOT / "docs" / "maverick-operating-loop.md"
COMMS_OUTBOX_DOC = ROOT / "docs" / "maverick-communication-outbox.md"
ACTIVATION_CHECKLIST_DOC = ROOT / "docs" / "maverick-activation-checklist.md"
LEARNING_LEDGER_DOC = ROOT / "docs" / "maverick-learning-ledger.md"
SLACK_BRIDGE_DOC = ROOT / "docs" / "maverick-slack-bridge.md"
GITHUB_BRIDGE_DOC = ROOT / "docs" / "maverick-github-bridge.md"
NOTION_BRIDGE_DOC = ROOT / "docs" / "maverick-notion-bridge.md"


def fail(message: str) -> int:
    print(f"FAIL: {message}", file=sys.stderr)
    return 1


def load_json(path: Path) -> dict:
    try:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"{path} is not valid JSON: {exc}") from exc


def require_terms(path: Path, terms: list[str]) -> list[str]:
    text = path.read_text(encoding="utf-8")
    return [term for term in terms if term not in text]


def validate_phase1() -> int:
    missing = [str(path.relative_to(ROOT)) for path in REQUIRED_FILES if not path.exists()]
    if missing:
        return fail(f"missing required files: {', '.join(missing)}")

    try:
        state = load_json(APP_DIR / "BUILD_STATE.json")
        schema = load_json(ROOT / "factory" / "schemas" / "maverick-workplace.schema.json")
    except ValueError as exc:
        return fail(str(exc))

    if state.get("app_name") != "maverick-cockpit":
        return fail("BUILD_STATE.json app_name must be maverick-cockpit")

    phases = state.get("phases")
    if not isinstance(phases, list) or len(phases) < 6:
        return fail("BUILD_STATE.json must define at least 6 phases")

    phase_numbers = [phase.get("number") for phase in phases]
    if phase_numbers != list(range(1, len(phases) + 1)):
        return fail("BUILD_STATE.json phase numbers must be sequential")

    if state.get("overall_status") not in {"ready", "in_progress", "blocked", "complete", "delivered"}:
        return fail("BUILD_STATE.json has invalid overall_status")

    if schema.get("title") != "Maverick Workplace":
        return fail("maverick-workplace.schema.json title mismatch")

    required_schema_groups = {"case", "workflow", "timing", "risk", "memory", "source"}
    actual_groups = set(schema.get("properties", {}).keys())
    if not required_schema_groups.issubset(actual_groups):
        return fail("maverick-workplace.schema.json is missing required groups")

    source_systems = schema["properties"]["source"]["properties"]["system"]["enum"]
    if "icloud_drive" not in source_systems:
        return fail("maverick-workplace.schema.json must include icloud_drive source")

    missing_blueprint_terms = require_terms(APP_DIR / "BLUEPRINT.md", REQUIRED_BLUEPRINT_TERMS)
    if missing_blueprint_terms:
        return fail(f"BLUEPRINT.md missing terms: {', '.join(missing_blueprint_terms)}")

    missing_doc_terms = require_terms(ROOT / "docs" / "maverick-cockpit.md", REQUIRED_DOC_TERMS)
    if missing_doc_terms:
        return fail(f"docs/maverick-cockpit.md missing terms: {', '.join(missing_doc_terms)}")

    print("PASS: Maverick Cockpit Phase 1 artifacts are present and consistent.")
    return 0


def validate_source_map() -> int:
    if validate_phase1() != 0:
        return 1

    missing = [path for path in [SOURCE_MAP_PATH, SOURCE_MAP_DOC] if not path.exists()]
    if missing:
        rel = ", ".join(str(path.relative_to(ROOT)) for path in missing)
        return fail(f"missing source-map files: {rel}")

    try:
        source_map = load_json(SOURCE_MAP_PATH)
    except ValueError as exc:
        return fail(str(exc))

    legacy_root_raw = source_map.get("legacy_root")
    if not isinstance(legacy_root_raw, str) or not legacy_root_raw:
        return fail("source-map.json must define legacy_root")
    legacy_root = Path(legacy_root_raw)
    if not legacy_root.exists():
        return fail(f"legacy_root does not exist: {legacy_root}")

    sources = source_map.get("sources")
    if not isinstance(sources, list) or len(sources) < len(REQUIRED_SOURCE_IDS):
        return fail("source-map.json must define the required source inventory")

    ids = set()
    invalid_roles = []
    missing_paths = []
    for source in sources:
        if not isinstance(source, dict):
            return fail("source-map.json sources must be objects")
        source_id = source.get("id")
        if not isinstance(source_id, str) or not source_id:
            return fail("source-map.json source missing id")
        ids.add(source_id)

        role = source.get("migration_role")
        if role not in VALID_MIGRATION_ROLES:
            invalid_roles.append(f"{source_id}:{role}")

        source_path = source.get("source_path")
        if source_path:
            if Path(source_path).is_absolute() or ".." in Path(source_path).parts:
                return fail(f"unsafe source_path for {source_id}: {source_path}")
            if not (legacy_root / source_path).exists():
                missing_paths.append(f"{source_id}:{source_path}")

    missing_ids = sorted(REQUIRED_SOURCE_IDS - ids)
    if missing_ids:
        return fail(f"source-map.json missing source ids: {', '.join(missing_ids)}")

    if invalid_roles:
        return fail(f"source-map.json has invalid migration roles: {', '.join(invalid_roles)}")

    if missing_paths:
        return fail(f"source-map.json references missing legacy paths: {', '.join(missing_paths)}")

    missing_doc_terms = require_terms(
        SOURCE_MAP_DOC,
        ["copy_now", "copy_later", "reference", "rebuild", "retire", "blocked", "iCloud Drive"],
    )
    if missing_doc_terms:
        return fail(f"docs/maverick-source-map.md missing terms: {', '.join(missing_doc_terms)}")

    print("PASS: Maverick Cockpit source map is present and references existing legacy assets.")
    return 0


def validate_ledger() -> int:
    if validate_source_map() != 0:
        return 1

    missing = [
        path
        for path in [LEDGER_CONTRACT_PATH, LEDGER_DOC, RAW_SAMPLE_PATH, NORMALIZED_SAMPLE_PATH, ROOT / "factory" / "maverick_case_adapter.py"]
        if not path.exists()
    ]
    if missing:
        rel = ", ".join(str(path.relative_to(ROOT)) for path in missing)
        return fail(f"missing ledger files: {rel}")

    try:
        contract = load_json(LEDGER_CONTRACT_PATH)
        raw_sample = load_json(RAW_SAMPLE_PATH)
        expected = load_json(NORMALIZED_SAMPLE_PATH)
    except ValueError as exc:
        return fail(str(exc))

    if contract.get("canonical_key") != "case.page_id":
        return fail("ledger-contract.json canonical_key must be case.page_id")

    if contract.get("retention_policy") != "retain_forever_until_user_changes_policy":
        return fail("ledger-contract.json retention policy must preserve every case by default")

    validation = contract.get("validation") or {}
    for key in ["sample_raw_case", "sample_normalized_case"]:
        rel_path = validation.get(key)
        if not isinstance(rel_path, str) or not (ROOT / rel_path).exists():
            return fail(f"ledger-contract.json validation.{key} must point to an existing file")

    actual = normalize_notion_case(raw_sample, observed_at="2026-06-14T16:15:58-04:00")
    if actual != expected:
        return fail("maverick_case_adapter output does not match normalized-case.json")

    required_groups = {"case", "workflow", "timing", "risk", "memory", "source"}
    if set(actual) != required_groups:
        return fail("normalized case must contain exactly the Maverick schema groups")

    if actual["case"]["page_id"] != raw_sample.get("id"):
        return fail("normalized case page_id must come from the Notion page id")

    missing_doc_terms = require_terms(
        LEDGER_DOC,
        ["case.page_id", "MID", "confirmation gate", "Slack writes", "Launch Team"],
    )
    if missing_doc_terms:
        return fail(f"docs/maverick-ledger.md missing terms: {', '.join(missing_doc_terms)}")

    print("PASS: Maverick Cockpit ledger seed normalizes the sample case correctly.")
    return 0


def validate_dashboard() -> int:
    if validate_ledger() != 0:
        return 1

    missing = [path for path in DASHBOARD_FILES if not path.exists()]
    if missing:
        rel = ", ".join(str(path.relative_to(ROOT)) for path in missing)
        return fail(f"missing dashboard files: {rel}")

    html = (DASHBOARD_DIR / "index.html").read_text(encoding="utf-8")
    css = (DASHBOARD_DIR / "styles.css").read_text(encoding="utf-8")
    js = (DASHBOARD_DIR / "app.js").read_text(encoding="utf-8")

    required_html = [
        "Maverick Cockpit",
        "Mission Control",
        "Case Radar",
        "Action Queue",
        "Signal Watch",
        "Merchant Memory",
        "Calendar Guard",
        "Learning Loop",
        "Learning Ledger",
        "Daily Command",
        "Launch Gates",
        "Canvas Map",
        "Bot Dispatch",
        "Comms Outbox",
        "Slack Bridge",
        "GitHub Bridge",
        "Notion Bridge",
        "Activation Matrix",
    ]
    missing_html = [term for term in required_html if term not in html]
    if missing_html:
        return fail(f"dashboard index missing terms: {', '.join(missing_html)}")

    required_js = [
        "setFilter",
        "renderCases",
        "renderActions",
        "addReviewAction",
        "confirmationOnly",
        "renderLaunchGates",
        "renderCanvases",
        "renderOperatingLoop",
        "renderBotDispatch",
        "renderCommsOutbox",
        "renderSlackBridge",
        "renderGithubBridge",
        "renderNotionBridge",
        "renderActivationChecklist",
        "renderLearningLedger",
        "launchGates",
        "activationChecklist",
        "learningLedger",
        "canvases",
        "botDispatch",
        "operatingLoop",
        "commsOutbox",
        "slackBridge",
        "githubBridge",
        "notionBridge",
        "packageStatus",
        "fetch(\"./data/maverick-dashboard-data.json\"",
    ]
    missing_js = [term for term in required_js if term not in js]
    if missing_js:
        return fail(f"dashboard app missing controls: {', '.join(missing_js)}")

    required_css = [
        "grid-template-columns",
        "@media",
        "--teal",
        "--amber",
        "--red",
        ".panel",
        ".launch-grid",
        ".gate-row",
        ".package-strip",
        ".canvas-row",
        ".loop-card",
        ".loop-row",
        ".bot-card",
        ".reply-cloud",
        ".outbox-list",
        ".outbox-row",
        ".bridge-card",
        ".bridge-row",
        ".github-card",
        ".github-row",
        ".notion-card",
        ".notion-row",
        ".activation-list",
        ".activation-row",
        ".ledger-card",
        ".ledger-row",
    ]
    missing_css = [term for term in required_css if term not in css]
    if missing_css:
        return fail(f"dashboard styles missing responsive/design tokens: {', '.join(missing_css)}")

    print("PASS: Maverick Cockpit dashboard shell is present and wired.")
    return 0


def validate_adapters() -> int:
    if validate_dashboard() != 0:
        return 1

    missing = [
        path
        for path in [
            ADAPTER_CONTRACT_PATH,
            ADAPTER_SNAPSHOT_PATH,
            DASHBOARD_DATA_PATH,
            NOTION_OVERVIEW_PATH,
            OPERATING_LOOP_PATH,
            OUTBOX_PATH,
            ACTIVATION_CHECKLIST_PATH,
            LEARNING_LEDGER_PATH,
            SLACK_BRIDGE_PATH,
            GITHUB_BRIDGE_PATH,
            NOTION_BRIDGE_PATH,
            ADAPTER_DOC,
            ROOT / "factory" / "maverick_adapters.py",
        ]
        if not path.exists()
    ]
    if missing:
        rel = ", ".join(str(path.relative_to(ROOT)) for path in missing)
        return fail(f"missing adapter files: {rel}")

    try:
        contract = load_json(ADAPTER_CONTRACT_PATH)
        snapshot = load_json(ADAPTER_SNAPSHOT_PATH)
        dashboard_data = load_json(DASHBOARD_DATA_PATH)
        notion_overview = load_json(NOTION_OVERVIEW_PATH)
        operating_loop = load_json(OPERATING_LOOP_PATH)
        communication_outbox = load_json(OUTBOX_PATH)
        activation_checklist = load_json(ACTIVATION_CHECKLIST_PATH)
        learning_ledger = load_json(LEARNING_LEDGER_PATH)
        slack_bridge = load_json(SLACK_BRIDGE_PATH)
        github_bridge = load_json(GITHUB_BRIDGE_PATH)
        notion_bridge = load_json(NOTION_BRIDGE_PATH)
    except ValueError as exc:
        return fail(str(exc))

    adapters = contract.get("adapters")
    if not isinstance(adapters, list) or len(adapters) < 5:
        return fail("adapter-contract.json must define at least 5 adapters")

    systems = {adapter.get("system") for adapter in adapters}
    for expected in {"notion", "slack", "gmail", "google_calendar", "icloud_drive"}:
        if expected not in systems:
            return fail(f"adapter-contract.json missing {expected} adapter")

    slack = next(adapter for adapter in adapters if adapter.get("system") == "slack")
    if slack.get("write_policy") != "blocked":
        return fail("Slack adapter write_policy must be blocked")

    for pending in ["gmail", "google_calendar"]:
        adapter = next(item for item in adapters if item.get("system") == pending)
        if adapter.get("read_policy") != "pending_access":
            return fail(f"{pending} adapter must remain pending_access until configured")

    expected_snapshot = build_snapshot(observed_at=SNAPSHOT_OBSERVED_AT)
    if snapshot != expected_snapshot:
        return fail("adapter-snapshot.json is stale; run python3 factory/maverick_adapters.py")

    if dashboard_data != snapshot.get("dashboard"):
        return fail("dashboard data JSON must match adapter snapshot dashboard payload")

    if snapshot.get("notion_overview") != notion_overview:
        return fail("adapter snapshot must embed the current Notion overview")
    if snapshot.get("operating_loop") != operating_loop:
        return fail("adapter snapshot must embed the current operating loop")
    if snapshot.get("communication_outbox") != communication_outbox:
        return fail("adapter snapshot must embed the current communication outbox")
    if snapshot.get("activation_checklist") != activation_checklist:
        return fail("adapter snapshot must embed the current activation checklist")
    if snapshot.get("learning_ledger") != learning_ledger:
        return fail("adapter snapshot must embed the current learning ledger")
    if snapshot.get("slack_bridge") != slack_bridge:
        return fail("adapter snapshot must embed the current Slack bridge")
    if snapshot.get("github_bridge") != github_bridge:
        return fail("adapter snapshot must embed the current GitHub bridge")
    if snapshot.get("notion_bridge") != notion_bridge:
        return fail("adapter snapshot must embed the current Notion bridge")

    for key in ["kpis", "cases", "actions", "signals", "memory", "calendar", "learning", "canvases", "launchGates"]:
        if not isinstance(dashboard_data.get(key), list):
            return fail(f"dashboard data missing list: {key}")
    if not isinstance(dashboard_data.get("operatingLoop"), dict):
        return fail("dashboard data missing operatingLoop object")
    if not isinstance(dashboard_data.get("commsOutbox"), dict):
        return fail("dashboard data missing commsOutbox object")
    if not isinstance(dashboard_data.get("activationChecklist"), dict):
        return fail("dashboard data missing activationChecklist object")
    if not isinstance(dashboard_data.get("learningLedger"), dict):
        return fail("dashboard data missing learningLedger object")
    if not isinstance(dashboard_data.get("slackBridge"), dict):
        return fail("dashboard data missing slackBridge object")
    if not isinstance(dashboard_data.get("githubBridge"), dict):
        return fail("dashboard data missing githubBridge object")
    if not isinstance(dashboard_data.get("notionBridge"), dict):
        return fail("dashboard data missing notionBridge object")

    if dashboard_data["kpis"][0].get("value") != 120:
        return fail("dashboard must show the fetched SHIFT-4 active case count")
    if len(dashboard_data.get("canvases") or []) < 8:
        return fail("dashboard must expose the Notion canvas/view map")
    bot_dispatch = dashboard_data.get("botDispatch")
    if not isinstance(bot_dispatch, dict) or len(bot_dispatch.get("quick_replies") or []) < 10:
        return fail("dashboard must expose guarded bot dispatch quick replies")
    daily_command = dashboard_data.get("operatingLoop") or {}
    if len(daily_command.get("todayObjectives") or []) < 4:
        return fail("dashboard must expose the daily command objectives")
    if daily_command.get("mission", {}).get("active_cases") != 120:
        return fail("dashboard daily command must use the fetched active case count")
    outbox = dashboard_data.get("commsOutbox") or {}
    if (outbox.get("slackApp") or {}).get("app_id") != "A0BALRB6CNQ":
        return fail("dashboard comms outbox must expose the Maverick Slack app id")
    if len(outbox.get("drafts") or []) < 4:
        return fail("dashboard comms outbox must expose local communication drafts")
    activation = dashboard_data.get("activationChecklist") or {}
    if (activation.get("summary") or {}).get("total_targets") != 6:
        return fail("dashboard activation checklist must expose all live targets")
    if "slack_maverick_app" not in ((activation.get("summary") or {}).get("pending_target_ids") or []):
        return fail("dashboard activation checklist must expose pending Slack app target")
    dashboard_ledger = dashboard_data.get("learningLedger") or {}
    if (dashboard_ledger.get("summary") or {}).get("promoted_events", 0) < 7:
        return fail("dashboard learning ledger must expose promoted learning events")
    if len(dashboard_ledger.get("rejectedMemory") or []) < 4:
        return fail("dashboard learning ledger must expose rejected unsafe memory")
    bridge = dashboard_data.get("slackBridge") or {}
    if (bridge.get("app") or {}).get("id") != "A0BALRB6CNQ":
        return fail("dashboard Slack bridge must expose the Maverick Slack app id")
    if not bridge.get("messageEnvelopes"):
        return fail("dashboard Slack bridge must expose dry-run message envelopes")
    if (bridge.get("dryRun") or {}).get("send_allowed"):
        return fail("dashboard Slack bridge must keep send_allowed false")
    github_bridge_data = dashboard_data.get("githubBridge") or {}
    if (github_bridge_data.get("repository") or {}).get("candidate_repo") != "dwinomarll/maverick-cockpit":
        return fail("dashboard GitHub bridge must expose the candidate Maverick repo")
    if (github_bridge_data.get("dryRun") or {}).get("publish_allowed"):
        return fail("dashboard GitHub bridge must keep publish_allowed false")
    if (github_bridge_data.get("packageEvidence") or {}).get("assembled_file_count", 0) < 30:
        return fail("dashboard GitHub bridge must expose assembled package evidence")
    notion_bridge_data = dashboard_data.get("notionBridge") or {}
    if (notion_bridge_data.get("target") or {}).get("known_target") != "collection://2106ae29-a07c-81cb-9c6e-000ba25c1f45":
        return fail("dashboard Notion bridge must expose the Launch Team collection")
    if (notion_bridge_data.get("dryRun") or {}).get("update_allowed"):
        return fail("dashboard Notion bridge must keep update_allowed false")
    if (notion_bridge_data.get("readModel") or {}).get("active_cases") != 120:
        return fail("dashboard Notion bridge must expose the read-only active case count")

    package_status = dashboard_data.get("packageStatus")
    if not isinstance(package_status, dict):
        return fail("dashboard data missing packageStatus object")
    if package_status.get("externalMutationAllowed"):
        return fail("dashboard packageStatus must not allow external mutation")
    if not dashboard_data.get("launchGates"):
        return fail("dashboard launchGates must include pending live targets")

    if not snapshot.get("slack", {}).get("never_write_to_slack"):
        return fail("adapter snapshot must preserve Slack never_write_to_slack=true")

    missing_doc_terms = require_terms(
        ADAPTER_DOC,
        ["Notion Launch Team sample", "Maverick learning ledger", "Slack Bridge", "GitHub Bridge", "Notion Bridge", "Slack signal config", "Gmail lane", "Google Calendar lane", "iCloud Drive destination"],
    )
    if missing_doc_terms:
        return fail(f"docs/maverick-adapters.md missing terms: {', '.join(missing_doc_terms)}")

    print("PASS: Maverick Cockpit read-only adapters emit a current dashboard snapshot.")
    return 0


def validate_notion_overview() -> int:
    if validate_dashboard() != 0:
        return 1

    missing = [
        path
        for path in [
            NOTION_OVERVIEW_PATH,
            NOTION_OVERVIEW_DOC,
            ROOT / "factory" / "maverick_notion_overview.py",
        ]
        if not path.exists()
    ]
    if missing:
        rel = ", ".join(str(path.relative_to(ROOT)) for path in missing)
        return fail(f"missing Notion overview files: {rel}")

    try:
        overview = load_json(NOTION_OVERVIEW_PATH)
    except ValueError as exc:
        return fail(str(exc))

    expected = build_notion_overview(observed_at=NOTION_OVERVIEW_OBSERVED_AT)
    if overview != expected:
        return fail("notion-overview.json is stale; run python3 factory/maverick_notion_overview.py")

    policy = overview.get("source_policy") or {}
    if policy.get("external_mutation_attempted"):
        return fail("Notion overview must not attempt external mutation")
    if "notion-query-data-sources not found" not in policy.get("notion_query_data_sources", ""):
        return fail("Notion overview must record the unavailable SQL row-query surface")

    portfolio = overview.get("portfolio_snapshot") or {}
    if portfolio.get("total_active_cases") != 120:
        return fail("Notion overview active case count mismatch")
    if portfolio.get("callbacks_pending") != 37 or portfolio.get("overdue_followups") != 22:
        return fail("Notion overview callback/follow-up counts mismatch")

    reconciliation = overview.get("reconciliation") or {}
    if reconciliation.get("total_accounts") != 172 or reconciliation.get("move_to_active") != 103:
        return fail("Notion overview reconciliation counts mismatch")

    if len(overview.get("canvases") or []) < 8:
        return fail("Notion overview must include the Launch Team canvas/view map")
    bot = overview.get("bot") or {}
    if "secret store" not in bot.get("secret_policy", ""):
        return fail("Notion overview bot policy must require secret storage")
    if len(bot.get("quick_replies") or []) < 10:
        return fail("Notion overview must include bot quick replies")

    missing_doc_terms = require_terms(
        NOTION_OVERVIEW_DOC,
        ["120 active cases", "172 reconciled accounts", "Bot dispatch", "notion-query-data-sources not found"],
    )
    if missing_doc_terms:
        return fail(f"docs/maverick-notion-overview.md missing terms: {', '.join(missing_doc_terms)}")

    print("PASS: Maverick Cockpit Notion overview maps live cases, canvases, and bot dispatch without writes.")
    return 0


def validate_notion_bridge() -> int:
    if validate_comms_outbox() != 0:
        return 1

    missing = [
        path
        for path in [
            NOTION_BRIDGE_PATH,
            NOTION_BRIDGE_DOC,
            ROOT / "factory" / "maverick_notion_bridge.py",
        ]
        if not path.exists()
    ]
    if missing:
        rel = ", ".join(str(path.relative_to(ROOT)) for path in missing)
        return fail(f"missing Notion bridge files: {rel}")

    try:
        bridge = load_json(NOTION_BRIDGE_PATH)
    except ValueError as exc:
        return fail(str(exc))

    expected = build_notion_bridge(observed_at=NOTION_BRIDGE_OBSERVED_AT)
    if bridge != expected:
        return fail("notion-live-bridge.json is stale; run python3 factory/maverick_notion_bridge.py")
    if bridge.get("external_mutation_attempted"):
        return fail("Notion bridge must not attempt external mutation")

    policy = bridge.get("source_policy") or {}
    if policy.get("preferred_source") != "collection://2106ae29-a07c-81cb-9c6e-000ba25c1f45":
        return fail("Notion bridge must preserve the Launch Team collection")
    if "notion-query-data-sources not found" not in policy.get("row_query_status", ""):
        return fail("Notion bridge must record the unavailable row-query surface")
    if policy.get("secrets_recorded") or not policy.get("personal_contact_fields_excluded"):
        return fail("Notion bridge must exclude secrets and personal contact fields")
    if "Workflow/modules/_base.py" not in policy.get("local_cache_fallback", ""):
        return fail("Notion bridge must preserve the local read-only fallback")

    target = bridge.get("target") or {}
    if target.get("write_gate") != "notion_status_update":
        return fail("Notion bridge must use notion_status_update gate")
    if target.get("confirmation_status") != "pending":
        return fail("Notion bridge must keep notion_live_launch_team pending until confirmed")
    if target.get("live_row_query_method") is not None or target.get("live_update_method") is not None:
        return fail("Notion bridge must not invent live row or update methods")
    if target.get("property_mapping_confirmed"):
        return fail("Notion bridge must not mark property mapping confirmed")

    read_model = bridge.get("read_model") or {}
    if read_model.get("active_cases") != 120 or read_model.get("canvas_count") < 8:
        return fail("Notion bridge must expose the read-only overview counts")

    envelopes = bridge.get("update_envelopes")
    if not isinstance(envelopes, list) or not envelopes:
        return fail("Notion bridge must include at least one update envelope")
    for envelope in envelopes:
        if envelope.get("update_allowed"):
            return fail("Notion bridge envelope must keep update_allowed false")
        if envelope.get("external_mutation_attempted"):
            return fail("Notion bridge envelope must not attempt external mutation")
        assessment = envelope.get("gate_assessment_without_token") or {}
        if assessment.get("allowed"):
            return fail("Notion bridge gate assessment without token must deny update")

    dry_run = bridge.get("dry_run") or {}
    if dry_run.get("query_attempted") or dry_run.get("update_attempted") or dry_run.get("update_allowed"):
        return fail("Notion bridge dry run must not query, update, or allow updates")

    missing_doc_terms = require_terms(
        NOTION_BRIDGE_DOC,
        ["collection://2106ae29-a07c-81cb-9c6e-000ba25c1f45", "notion-query-data-sources not found", "MAVERICK-CONFIRM notion_status_update notion-status-batch-plan", "python3 factory/validate_maverick.py --phase notion-bridge"],
    )
    if missing_doc_terms:
        return fail(f"docs/maverick-notion-bridge.md missing terms: {', '.join(missing_doc_terms)}")

    print("PASS: Maverick Cockpit Notion bridge prepares row/update envelopes without mutation.")
    return 0


def validate_operating_loop() -> int:
    if validate_notion_overview() != 0:
        return 1

    missing = [
        path
        for path in [
            OPERATING_LOOP_PATH,
            OPERATING_LOOP_DOC,
            ROOT / "factory" / "maverick_operating_loop.py",
        ]
        if not path.exists()
    ]
    if missing:
        rel = ", ".join(str(path.relative_to(ROOT)) for path in missing)
        return fail(f"missing operating-loop files: {rel}")

    try:
        loop = load_json(OPERATING_LOOP_PATH)
        overview = load_json(NOTION_OVERVIEW_PATH)
        live_targets = load_json(LIVE_TARGETS_PATH)
    except ValueError as exc:
        return fail(str(exc))

    expected = build_operating_loop(
        overview=overview,
        live_targets=live_targets,
        observed_at=OPERATING_LOOP_OBSERVED_AT,
    )
    if loop != expected:
        return fail("operating-loop.json is stale; run python3 factory/maverick_operating_loop.py")
    if loop.get("external_mutation_attempted"):
        return fail("operating loop must not attempt external mutation")
    if (loop.get("source_policy") or {}).get("slack_policy") != "legacy_watch_read_only_maverick_app_writes_gated":
        return fail("operating loop must distinguish read-only Slack watch from gated Slack app writes")

    mission = loop.get("mission") or {}
    if mission.get("active_cases") != 120 or mission.get("desired_active_cases") != 50:
        return fail("operating loop mission must preserve active case pressure and 50-case target")
    if mission.get("window_days") != 14:
        return fail("operating loop must preserve the 14-day handling window")
    if len(loop.get("daily_cadence") or []) < 4:
        return fail("operating loop must define a complete daily cadence")
    if len(loop.get("today_objectives") or []) < 4:
        return fail("operating loop must define today's objectives")
    if len(loop.get("canvas_routes") or []) < 8:
        return fail("operating loop must route through the Notion canvases")
    if "slack_maverick_app" not in (loop.get("pending_confirmations") or []):
        return fail("operating loop must surface the pending Maverick Slack app confirmation")
    if "A0BALRB6CNQ" not in LIVE_TARGETS_PATH.read_text(encoding="utf-8"):
        return fail("live-targets.json must record the Maverick Slack app id")

    missing_doc_terms = require_terms(
        OPERATING_LOOP_DOC,
        ["Daily Command", "A0BALRB6CNQ", "14-day handling window", "python3 factory/validate_maverick.py --phase operating-loop"],
    )
    if missing_doc_terms:
        return fail(f"docs/maverick-operating-loop.md missing terms: {', '.join(missing_doc_terms)}")

    print("PASS: Maverick Cockpit operating loop turns cases, canvases, bot dispatch, and gates into daily command.")
    return 0


def validate_comms_outbox() -> int:
    if validate_operating_loop() != 0:
        return 1

    missing = [
        path
        for path in [
            OUTBOX_PATH,
            COMMS_OUTBOX_DOC,
            ROOT / "factory" / "maverick_comms_outbox.py",
        ]
        if not path.exists()
    ]
    if missing:
        rel = ", ".join(str(path.relative_to(ROOT)) for path in missing)
        return fail(f"missing communication outbox files: {rel}")

    try:
        outbox = load_json(OUTBOX_PATH)
        operating_loop = load_json(OPERATING_LOOP_PATH)
        live_targets = load_json(LIVE_TARGETS_PATH)
    except ValueError as exc:
        return fail(str(exc))

    expected = build_outbox(
        operating_loop=operating_loop,
        live_targets=live_targets,
        observed_at=COMMS_OUTBOX_OBSERVED_AT,
    )
    if outbox != expected:
        return fail("communication-outbox.json is stale; run python3 factory/maverick_comms_outbox.py")
    if outbox.get("external_mutation_attempted"):
        return fail("communication outbox must not attempt external mutation")
    policy = outbox.get("source_policy") or {}
    if not policy.get("secret_storage_required") or not policy.get("personal_contact_fields_excluded"):
        return fail("communication outbox must require secret storage and exclude direct contact fields")

    slack_app = outbox.get("slack_app") or {}
    if slack_app.get("app_id") != "A0BALRB6CNQ":
        return fail("communication outbox must record the Maverick Slack app id")
    if slack_app.get("target_status") != "pending":
        return fail("communication outbox must keep Slack app sends pending until target confirmation")

    drafts = outbox.get("drafts")
    if not isinstance(drafts, list) or len(drafts) < 4:
        return fail("communication outbox must define Slack, Gmail, Calendar, and Notion drafts")
    required_drafts = {
        "slack_daily_command_brief": "slack_write",
        "gmail_followup_batch_plan": "gmail_send",
        "calendar_focus_block_plan": "google_calendar_update",
        "notion_status_batch_plan": "notion_status_update",
    }
    draft_by_id = {draft.get("id"): draft for draft in drafts if isinstance(draft, dict)}
    for draft_id, gate_id in required_drafts.items():
        draft = draft_by_id.get(draft_id)
        if draft is None:
            return fail(f"communication outbox missing draft: {draft_id}")
        if draft.get("gate") != gate_id:
            return fail(f"{draft_id} must use gate {gate_id}")
        if draft.get("external_mutation_attempted"):
            return fail(f"{draft_id} must not attempt external mutation")
        if not str(draft.get("required_token", "")).startswith(f"MAVERICK-CONFIRM {gate_id} "):
            return fail(f"{draft_id} missing scoped MAVERICK-CONFIRM token")

    slack_draft = draft_by_id["slack_daily_command_brief"]
    if slack_draft.get("status") != "blocked_pending_target":
        return fail("Slack daily command draft must stay blocked until a Slack target is confirmed")
    if "120 active cases" not in slack_draft.get("body", ""):
        return fail("Slack daily command draft must summarize the current case pressure")

    combined = OUTBOX_PATH.read_text(encoding="utf-8") + COMMS_OUTBOX_DOC.read_text(encoding="utf-8")
    leaked = [marker for marker in ["xoxb-", "xoxp-", "ghp_", "github_pat_", "oauth_token"] if marker in combined]
    if leaked:
        return fail(f"communication outbox appears to contain secret markers: {', '.join(leaked)}")

    missing_doc_terms = require_terms(
        COMMS_OUTBOX_DOC,
        ["A0BALRB6CNQ", "Comms Outbox", "slack_write", "python3 factory/validate_maverick.py --phase comms-outbox"],
    )
    if missing_doc_terms:
        return fail(f"docs/maverick-communication-outbox.md missing terms: {', '.join(missing_doc_terms)}")

    print("PASS: Maverick Cockpit communication outbox prepares gated local drafts without sends.")
    return 0


def validate_activation_checklist() -> int:
    if validate_comms_outbox() != 0:
        return 1

    missing = [
        path
        for path in [
            ACTIVATION_CHECKLIST_PATH,
            ACTIVATION_CHECKLIST_DOC,
            ROOT / "factory" / "maverick_activation_checklist.py",
        ]
        if not path.exists()
    ]
    if missing:
        rel = ", ".join(str(path.relative_to(ROOT)) for path in missing)
        return fail(f"missing activation checklist files: {rel}")

    try:
        checklist = load_json(ACTIVATION_CHECKLIST_PATH)
    except ValueError as exc:
        return fail(str(exc))

    expected = build_activation_checklist(observed_at=ACTIVATION_CHECKLIST_OBSERVED_AT)
    if checklist != expected:
        return fail("activation-checklist.json is stale; run python3 factory/maverick_activation_checklist.py")
    if checklist.get("external_mutation_attempted"):
        return fail("activation checklist must not attempt external mutation")
    policy = checklist.get("source_policy") or {}
    if policy.get("secrets_recorded") or not policy.get("confirmation_tokens_are_examples"):
        return fail("activation checklist must not record secrets and tokens must be examples")

    summary = checklist.get("activation_summary") or {}
    if summary.get("total_targets") != 6:
        return fail("activation checklist must cover all six live targets")
    if summary.get("pending_targets") != 5:
        return fail("activation checklist must preserve the five pending live targets")
    if "slack_maverick_app" not in (summary.get("pending_target_ids") or []):
        return fail("activation checklist must surface the pending Maverick Slack app")

    lanes = checklist.get("lanes")
    if not isinstance(lanes, list) or len(lanes) != 6:
        return fail("activation checklist must include one lane per live target")
    by_id = {lane.get("target_id"): lane for lane in lanes if isinstance(lane, dict)}
    slack = by_id.get("slack_maverick_app")
    if not slack:
        return fail("activation checklist missing slack_maverick_app lane")
    if slack.get("known_target") != "A0BALRB6CNQ" or slack.get("gate") != "slack_write":
        return fail("Slack activation lane must preserve app id and slack_write gate")
    if slack.get("draft_count") < 1 or "slack_daily_command_brief" not in (slack.get("draft_ids") or []):
        return fail("Slack activation lane must link to the daily command draft")
    if "bot token" not in " ".join(slack.get("missing_evidence") or []):
        return fail("Slack activation lane must require secret-store bot token handling")
    if not str(slack.get("example_confirmation_token", "")).startswith("MAVERICK-CONFIRM slack_write activate-slack_maverick_app"):
        return fail("Slack activation lane must provide a scoped example confirmation token")

    missing_doc_terms = require_terms(
        ACTIVATION_CHECKLIST_DOC,
        ["Activation Matrix", "A0BALRB6CNQ", "confirmation tokens in this file are examples", "python3 factory/validate_maverick.py --phase activation-checklist"],
    )
    if missing_doc_terms:
        return fail(f"docs/maverick-activation-checklist.md missing terms: {', '.join(missing_doc_terms)}")

    print("PASS: Maverick Cockpit activation checklist maps live target readiness without opening gates.")
    return 0


def validate_learning_ledger() -> int:
    if validate_activation_checklist() != 0:
        return 1

    missing = [
        path
        for path in [
            LEARNING_LEDGER_PATH,
            LEARNING_LEDGER_DOC,
            ROOT / "factory" / "maverick_learning_ledger.py",
        ]
        if not path.exists()
    ]
    if missing:
        rel = ", ".join(str(path.relative_to(ROOT)) for path in missing)
        return fail(f"missing learning ledger files: {rel}")

    try:
        ledger = load_json(LEARNING_LEDGER_PATH)
    except ValueError as exc:
        return fail(str(exc))

    expected = build_learning_ledger(observed_at=LEARNING_LEDGER_OBSERVED_AT)
    if ledger != expected:
        return fail("learning-ledger.json is stale; run python3 factory/maverick_learning_ledger.py")
    if ledger.get("external_mutation_attempted"):
        return fail("learning ledger must not attempt external mutation")
    policy = ledger.get("source_policy") or {}
    if not policy.get("personal_contact_fields_excluded") or policy.get("secrets_recorded"):
        return fail("learning ledger must exclude personal contact fields and secrets")

    summary = ledger.get("summary") or {}
    if summary.get("promoted_events", 0) < 7:
        return fail("learning ledger must promote at least seven evidence-backed events")
    if summary.get("rejected_memory", 0) < 4:
        return fail("learning ledger must reject unsafe memory categories")

    events = {event.get("id") for event in ledger.get("learning_events", []) if isinstance(event, dict)}
    for expected_id in {"slack_two_lane_model", "activation_gate_pressure"}:
        if expected_id not in events:
            return fail(f"learning ledger missing promoted event: {expected_id}")

    rejected = {item.get("id") for item in ledger.get("rejected_memory", []) if isinstance(item, dict)}
    for expected_id in {"bot_or_oauth_tokens", "direct_contact_fields"}:
        if expected_id not in rejected:
            return fail(f"learning ledger missing rejected memory: {expected_id}")

    missing_doc_terms = require_terms(
        LEARNING_LEDGER_DOC,
        ["Learning Ledger", "A0BALRB6CNQ", "promote", "python3 factory/validate_maverick.py --phase learning-ledger"],
    )
    if missing_doc_terms:
        return fail(f"docs/maverick-learning-ledger.md missing terms: {', '.join(missing_doc_terms)}")

    print("PASS: Maverick Cockpit learning ledger promotes evidence-backed lessons and rejects unsafe memory.")
    return 0


def validate_slack_bridge() -> int:
    if validate_comms_outbox() != 0:
        return 1

    missing = [
        path
        for path in [
            SLACK_BRIDGE_PATH,
            SLACK_BRIDGE_DOC,
            ROOT / "factory" / "maverick_slack_bridge.py",
        ]
        if not path.exists()
    ]
    if missing:
        rel = ", ".join(str(path.relative_to(ROOT)) for path in missing)
        return fail(f"missing Slack bridge files: {rel}")

    try:
        bridge = load_json(SLACK_BRIDGE_PATH)
    except ValueError as exc:
        return fail(str(exc))

    expected = build_slack_bridge(observed_at=SLACK_BRIDGE_OBSERVED_AT)
    if bridge != expected:
        return fail("slack-app-bridge.json is stale; run python3 factory/maverick_slack_bridge.py")
    if bridge.get("external_mutation_attempted"):
        return fail("Slack bridge must not attempt external mutation")

    policy = bridge.get("source_policy") or {}
    if policy.get("legacy_watch_policy") != "read_only":
        return fail("Slack bridge must preserve the legacy watch read-only policy")
    if policy.get("secrets_recorded"):
        return fail("Slack bridge must not record secrets")

    app = bridge.get("app") or {}
    if app.get("id") != "A0BALRB6CNQ" or app.get("write_gate") != "slack_write":
        return fail("Slack bridge must preserve app id and slack_write gate")
    if app.get("communication_target") is not None or app.get("secret_store_reference") is not None:
        return fail("Slack bridge must not guess channel/DM target or secret store reference")

    envelopes = bridge.get("message_envelopes")
    if not isinstance(envelopes, list) or not envelopes:
        return fail("Slack bridge must include at least one dry-run message envelope")
    for envelope in envelopes:
        if envelope.get("send_allowed"):
            return fail("Slack bridge envelope must keep send_allowed false")
        if envelope.get("channel_or_dm_id") is not None:
            return fail("Slack bridge envelope must not guess a channel or DM id")
        if envelope.get("external_mutation_attempted"):
            return fail("Slack bridge envelope must not attempt external mutation")
        assessment = envelope.get("gate_assessment_without_token") or {}
        if assessment.get("allowed"):
            return fail("Slack bridge gate assessment without token must deny send")

    dry_run = bridge.get("dry_run") or {}
    if dry_run.get("send_allowed") or dry_run.get("send_attempted"):
        return fail("Slack bridge dry run must not allow or attempt send")

    missing_doc_terms = require_terms(
        SLACK_BRIDGE_DOC,
        ["A0BALRB6CNQ", "MAVERICK-CONFIRM slack_write", "legacy Slack signal watch remains read-only", "python3 factory/validate_maverick.py --phase slack-bridge"],
    )
    if missing_doc_terms:
        return fail(f"docs/maverick-slack-bridge.md missing terms: {', '.join(missing_doc_terms)}")

    print("PASS: Maverick Cockpit Slack bridge prepares dry-run app envelopes without sends.")
    return 0


def validate_github_bridge() -> int:
    if validate_repo_assembly() != 0:
        return 1

    missing = [
        path
        for path in [
            GITHUB_BRIDGE_PATH,
            GITHUB_BRIDGE_DOC,
            ROOT / "factory" / "maverick_github_bridge.py",
        ]
        if not path.exists()
    ]
    if missing:
        rel = ", ".join(str(path.relative_to(ROOT)) for path in missing)
        return fail(f"missing GitHub bridge files: {rel}")

    try:
        bridge = load_json(GITHUB_BRIDGE_PATH)
    except ValueError as exc:
        return fail(str(exc))

    expected = build_github_bridge(observed_at=GITHUB_BRIDGE_OBSERVED_AT)
    if bridge != expected:
        return fail("github-publish-bridge.json is stale; run python3 factory/maverick_github_bridge.py")
    if bridge.get("external_mutation_attempted"):
        return fail("GitHub bridge must not attempt external mutation")

    policy = bridge.get("source_policy") or {}
    if policy.get("secrets_recorded") or policy.get("gh_auth_output_recorded"):
        return fail("GitHub bridge must not record secrets or gh auth output")

    repo = bridge.get("repository") or {}
    if repo.get("candidate_repo") != "dwinomarll/maverick-cockpit":
        return fail("GitHub bridge must preserve the candidate Maverick repo")
    if repo.get("write_gate") != "github_publish":
        return fail("GitHub bridge must use github_publish gate")
    if repo.get("confirmation_status") != "pending":
        return fail("GitHub bridge must keep github_global_repo pending until confirmed")

    evidence = bridge.get("package_evidence") or {}
    if evidence.get("assembled_file_count", 0) < 30:
        return fail("GitHub bridge must include assembled package evidence")
    if evidence.get("missing_required_artifacts"):
        return fail("GitHub bridge package evidence must have no missing required artifacts")
    if evidence.get("external_mutation_allowed"):
        return fail("GitHub bridge package evidence must not allow external mutation")

    envelope = bridge.get("publish_envelope") or {}
    if envelope.get("publish_allowed"):
        return fail("GitHub bridge must keep publish_allowed false")
    if envelope.get("required_token") != "MAVERICK-CONFIRM github_publish github-publish-maverick-cockpit":
        return fail("GitHub bridge required token mismatch")
    assessment = envelope.get("gate_assessment_without_token") or {}
    if assessment.get("allowed"):
        return fail("GitHub bridge gate assessment without token must deny publish")

    dry_run = bridge.get("dry_run") or {}
    if dry_run.get("publish_allowed") or dry_run.get("publish_attempted"):
        return fail("GitHub bridge dry run must not allow or attempt publish")

    missing_doc_terms = require_terms(
        GITHUB_BRIDGE_DOC,
        ["dwinomarll/maverick-cockpit", "MAVERICK-CONFIRM github_publish github-publish-maverick-cockpit", "does not push", "python3 factory/validate_maverick.py --phase github-bridge"],
    )
    if missing_doc_terms:
        return fail(f"docs/maverick-github-bridge.md missing terms: {', '.join(missing_doc_terms)}")

    print("PASS: Maverick Cockpit GitHub bridge prepares a dry-run publish envelope without pushes.")
    return 0


def validate_write_gates() -> int:
    if validate_adapters() != 0:
        return 1

    missing = [
        path
        for path in [
            WRITE_GATE_CONTRACT_PATH,
            EXPORT_MANIFEST_PATH,
            AUDIT_LOG_PATH,
            WRITE_GATE_DOC,
            ROOT / "factory" / "maverick_write_gates.py",
        ]
        if not path.exists()
    ]
    if missing:
        rel = ", ".join(str(path.relative_to(ROOT)) for path in missing)
        return fail(f"missing write-gate files: {rel}")

    try:
        contract = load_json(WRITE_GATE_CONTRACT_PATH)
        manifest = load_json(EXPORT_MANIFEST_PATH)
    except ValueError as exc:
        return fail(str(exc))

    try:
        audit_events = [
            json.loads(line)
            for line in AUDIT_LOG_PATH.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    except Exception as exc:  # noqa: BLE001
        return fail(f"audit-log.ndjson is not valid NDJSON: {exc}")

    required_gates = {
        "notion_status_update",
        "gmail_send",
        "google_calendar_update",
        "icloud_artifact_export",
        "github_publish",
        "slack_write",
    }
    gates = contract.get("gates")
    if not isinstance(gates, list):
        return fail("write-gate-contract.json must contain gates")

    gate_by_id = {gate.get("id"): gate for gate in gates if isinstance(gate, dict)}
    missing_gates = sorted(required_gates - set(gate_by_id))
    if missing_gates:
        return fail(f"write-gate-contract.json missing gates: {', '.join(missing_gates)}")

    live_targets = load_json(LIVE_TARGETS_PATH)
    icloud_target = next(
        (target for target in live_targets.get("targets", []) if target.get("id") == "icloud_destination"),
        {},
    )
    icloud_confirmed = icloud_target.get("confirmation_status") == "confirmed"

    for gate_id, gate in gate_by_id.items():
        if not gate.get("external_mutation"):
            return fail(f"{gate_id} must declare external_mutation true")

        assessment = assess_gate(gate_id, "phase6-dry-run")
        if assessment.get("allowed"):
            return fail(f"{gate_id} allows unconfirmed external mutation")
        if assessment.get("external_mutation_attempted"):
            return fail(f"{gate_id} attempted external mutation during validation")

        if gate.get("policy") != "confirmation_required":
            return fail(f"{gate_id} must require confirmation")
        if gate_id == "icloud_artifact_export" and icloud_confirmed:
            if not gate.get("enabled"):
                return fail("icloud_artifact_export must be enabled after the local iCloud target is confirmed")
            if assessment.get("reason") != "missing_or_invalid_confirmation_token":
                return fail("enabled icloud_artifact_export must still deny without an exact token")
        else:
            if gate.get("enabled"):
                return fail(f"{gate_id} must stay disabled until a live target is confirmed")
            if assessment.get("reason") != "gate_not_enabled":
                return fail(f"{gate_id} must deny by gate_not_enabled before live target confirmation")

    expected_manifest = build_export_manifest(observed_at=WRITE_GATE_OBSERVED_AT)
    if manifest != expected_manifest:
        return fail("export-manifest.json is stale; run python3 factory/maverick_write_gates.py")

    if manifest.get("external_mutation_attempted"):
        return fail("export manifest must not record external mutation")
    if manifest.get("missing_artifacts"):
        return fail(f"export manifest has missing artifacts: {', '.join(manifest['missing_artifacts'])}")
    if manifest.get("artifact_count", 0) < 10:
        return fail("export manifest should include the core Maverick artifact set")

    for artifact in manifest.get("artifacts", []):
        digest = artifact.get("sha256")
        if not isinstance(digest, str) or len(digest) != 64:
            return fail(f"export manifest artifact missing sha256: {artifact.get('path')}")

    if not audit_events:
        return fail("audit-log.ndjson must contain at least one event")
    latest = audit_events[-1]
    if latest.get("event_type") != "write_gate_dry_run":
        return fail("audit log latest event must be write_gate_dry_run")
    if latest.get("external_mutation_attempted"):
        return fail("audit log must not record external mutation")

    missing_doc_terms = require_terms(
        WRITE_GATE_DOC,
        ["MAVERICK-CONFIRM", "notion_status_update", "gmail_send", "google_calendar_update", "icloud_artifact_export", "github_publish", "slack_write"],
    )
    if missing_doc_terms:
        return fail(f"docs/maverick-write-gates.md missing terms: {', '.join(missing_doc_terms)}")

    print("PASS: Maverick Cockpit write gates deny unconfirmed external mutations and prepare a local export manifest.")
    return 0


def validate_global_repo() -> int:
    if validate_write_gates() != 0:
        return 1

    missing = [
        path
        for path in [
            GLOBAL_REPO_CONTRACT_PATH,
            GLOBAL_REPO_README_PATH,
            GLOBAL_REPO_MANIFEST_PATH,
            GLOBAL_REPO_DOC,
            ROOT / "factory" / "maverick_global_repo.py",
        ]
        if not path.exists()
    ]
    if missing:
        rel = ", ".join(str(path.relative_to(ROOT)) for path in missing)
        return fail(f"missing global-repo files: {rel}")

    try:
        contract = load_json(GLOBAL_REPO_CONTRACT_PATH)
        manifest = load_json(GLOBAL_REPO_MANIFEST_PATH)
    except ValueError as exc:
        return fail(str(exc))

    if contract.get("publish_gate") != "github_publish":
        return fail("global repo contract must use github_publish gate")
    if contract.get("export_gate") != "icloud_artifact_export":
        return fail("global repo contract must use icloud_artifact_export gate")
    if contract.get("external_mutation_allowed"):
        return fail("global repo package must not allow external mutation")
    if contract.get("publish_status") != "prepared_local_only":
        return fail("global repo package must remain prepared_local_only before confirmation")

    expected_manifest = build_package_manifest(observed_at=GLOBAL_REPO_OBSERVED_AT)
    if manifest != expected_manifest:
        return fail("package-manifest.json is stale; run python3 factory/maverick_global_repo.py")
    if manifest.get("missing_required_artifacts"):
        return fail(f"global repo package missing artifacts: {', '.join(manifest['missing_required_artifacts'])}")
    if manifest.get("external_mutation_allowed"):
        return fail("global repo manifest must not allow external mutation")
    if manifest.get("source_artifact_count", 0) < 20:
        return fail("global repo package should include the Maverick portable artifact set")

    readme_terms = [
        "Maverick Cockpit",
        "python3 factory/validate_maverick.py --phase global-repo",
        "MAVERICK-CONFIRM github_publish",
        "A0BALRB6CNQ",
        "slack_write",
    ]
    missing_readme_terms = require_terms(GLOBAL_REPO_README_PATH, readme_terms)
    if missing_readme_terms:
        return fail(f"global repo README missing terms: {', '.join(missing_readme_terms)}")

    missing_doc_terms = require_terms(
        GLOBAL_REPO_DOC,
        ["github_publish", "icloud_artifact_export", "standalone", "package-manifest.json"],
    )
    if missing_doc_terms:
        return fail(f"docs/maverick-global-repo.md missing terms: {', '.join(missing_doc_terms)}")

    print("PASS: Maverick Cockpit global repo package is prepared locally without external mutation.")
    return 0


def validate_repo_assembly() -> int:
    if validate_global_repo() != 0:
        return 1

    missing = [
        path
        for path in [
            GLOBAL_REPO_ASSEMBLY_MANIFEST_PATH,
            GLOBAL_REPO_PACKAGE_DIR,
            REPO_ASSEMBLY_DOC,
            ROOT / "factory" / "maverick_assemble_repo.py",
        ]
        if not path.exists()
    ]
    if missing:
        rel = ", ".join(str(path.relative_to(ROOT)) for path in missing)
        return fail(f"missing repo-assembly files: {rel}")

    try:
        manifest = load_json(GLOBAL_REPO_ASSEMBLY_MANIFEST_PATH)
    except ValueError as exc:
        return fail(str(exc))

    expected_manifest = assemble_package(observed_at=GLOBAL_REPO_ASSEMBLED_AT)
    if manifest != expected_manifest:
        return fail("assembly-manifest.json is stale; run python3 factory/maverick_assemble_repo.py")
    if manifest.get("external_mutation_attempted"):
        return fail("repo assembly must not attempt external mutation")
    if manifest.get("external_mutation_allowed"):
        return fail("repo assembly must not allow external mutation")
    if manifest.get("file_count", 0) < 30:
        return fail("repo assembly should include the portable Maverick package")

    required_package_files = [
        "README.md",
        "CONFIRMATION_REQUEST.md",
        "docs/maverick-cockpit.md",
        "docs/maverick-notion-overview.md",
        "docs/maverick-operating-loop.md",
        "docs/maverick-communication-outbox.md",
        "docs/maverick-activation-checklist.md",
        "docs/maverick-learning-ledger.md",
        "docs/maverick-slack-bridge.md",
        "docs/maverick-github-bridge.md",
        "docs/maverick-notion-bridge.md",
        "docs/maverick-workflow.md",
        "docs/maverick-icloud-export.md",
        "docs/maverick-repo-assembly.md",
        "cockpit/index.html",
        "cockpit/styles.css",
        "cockpit/app.js",
        "contracts/BUILD_STATE.json",
        "contracts/notion-overview.json",
        "contracts/operating-loop.json",
        "contracts/communication-outbox.json",
        "contracts/activation-checklist.json",
        "contracts/learning-ledger.json",
        "contracts/slack-app-bridge.json",
        "contracts/github-publish-bridge.json",
        "contracts/notion-live-bridge.json",
        "contracts/live-targets.json",
        "contracts/global-repo/package-manifest.json",
        "scripts/validate_maverick.py",
        "scripts/maverick_assemble_repo.py",
        "scripts/maverick_export_icloud.py",
        "scripts/maverick_notion_overview.py",
        "scripts/maverick_operating_loop.py",
        "scripts/maverick_comms_outbox.py",
        "scripts/maverick_activation_checklist.py",
        "scripts/maverick_learning_ledger.py",
        "scripts/maverick_slack_bridge.py",
        "scripts/maverick_github_bridge.py",
        "scripts/maverick_notion_bridge.py",
        "schemas/maverick-workplace.schema.json",
    ]
    manifest_targets = {file_info.get("target") for file_info in manifest.get("files", [])}
    missing_package_files = [target for target in required_package_files if target not in manifest_targets]
    if missing_package_files:
        return fail(f"repo assembly missing package files: {', '.join(missing_package_files)}")

    for file_info in manifest.get("files", []):
        target = file_info.get("target")
        digest = file_info.get("sha256")
        if not isinstance(target, str) or not target:
            return fail("repo assembly file missing target")
        package_file = GLOBAL_REPO_PACKAGE_DIR / target
        if not package_file.exists():
            return fail(f"repo assembly package file missing on disk: {target}")
        if not isinstance(digest, str) or len(digest) != 64:
            return fail(f"repo assembly file missing sha256: {target}")

    missing_doc_terms = require_terms(
        REPO_ASSEMBLY_DOC,
        ["python3 factory/maverick_assemble_repo.py", "package/", "ignored by Git"],
    )
    if missing_doc_terms:
        return fail(f"docs/maverick-repo-assembly.md missing terms: {', '.join(missing_doc_terms)}")

    print("PASS: Maverick Cockpit repo package assembles locally without external mutation.")
    return 0


def validate_target_discovery() -> int:
    if validate_repo_assembly() != 0:
        return 1

    missing = [
        path
        for path in [
            TARGET_DISCOVERY_PATH,
            CONFIRMATION_REQUEST_PATH,
            TARGET_DISCOVERY_DOC,
            ROOT / "factory" / "maverick_live_targets.py",
        ]
        if not path.exists()
    ]
    if missing:
        rel = ", ".join(str(path.relative_to(ROOT)) for path in missing)
        return fail(f"missing target-discovery files: {rel}")

    try:
        discovery = load_json(TARGET_DISCOVERY_PATH)
    except ValueError as exc:
        return fail(str(exc))

    expected = build_discovery(observed_at=LIVE_TARGET_DISCOVERED_AT)
    if discovery != expected:
        return fail("target-discovery.json is stale; run python3 factory/maverick_live_targets.py")

    if discovery.get("external_mutation_attempted"):
        return fail("target discovery must not attempt external mutation")
    if discovery.get("confirmation_status_changed"):
        return fail("target discovery must not confirm live targets")

    github = discovery.get("github", {})
    if github.get("current_origin") != "https://github.com/dwinomarll/TGAOTU.git":
        return fail("target discovery must record current GitHub origin")
    if github.get("write_gate") != "github_publish":
        return fail("GitHub discovery must use github_publish gate")
    gh = github.get("gh", {})
    if gh.get("auth_output_recorded"):
        return fail("target discovery must not record gh auth output")

    icloud = discovery.get("icloud_drive", {})
    candidates = icloud.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        return fail("target discovery must include iCloud candidates")
    if not any(candidate.get("selected") and candidate.get("exists") for candidate in candidates):
        return fail("target discovery must identify an existing selected iCloud candidate")

    live_targets = load_json(LIVE_TARGETS_PATH)
    expected_pending = {
        target["id"]
        for target in live_targets["targets"]
        if target.get("confirmation_status") != "confirmed"
    }
    pending = set(discovery.get("pending_target_ids") or [])
    if pending != expected_pending:
        return fail("target discovery pending ids must match the local live-target ledger")

    combined_text = TARGET_DISCOVERY_PATH.read_text(encoding="utf-8") + CONFIRMATION_REQUEST_PATH.read_text(encoding="utf-8")
    secret_markers = ["ghp_", "github_pat_", "Token:", "oauth_token"]
    leaked = [marker for marker in secret_markers if marker in combined_text]
    if leaked:
        return fail(f"target discovery appears to contain secret markers: {', '.join(leaked)}")

    missing_request_terms = require_terms(
        CONFIRMATION_REQUEST_PATH,
        ["MAVERICK-CONFIRM github_publish", "MAVERICK-CONFIRM icloud_artifact_export", "A0BALRB6CNQ", "legacy Slack signal watch remains"],
    )
    if missing_request_terms:
        return fail(f"confirmation-request.md missing terms: {', '.join(missing_request_terms)}")

    missing_doc_terms = require_terms(
        TARGET_DISCOVERY_DOC,
        ["python3 factory/maverick_live_targets.py", "does not open the gate", "A0BALRB6CNQ", "send Slack messages"],
    )
    if missing_doc_terms:
        return fail(f"docs/maverick-target-discovery.md missing terms: {', '.join(missing_doc_terms)}")

    print("PASS: Maverick Cockpit target discovery records local candidates without confirming live targets.")
    return 0


def validate_confirmation_applier() -> int:
    if validate_target_discovery() != 0:
        return 1

    missing = [
        path
        for path in [
            CONFIRMATION_APPLIER_DOC,
            ROOT / "factory" / "maverick_confirm_target.py",
        ]
        if not path.exists()
    ]
    if missing:
        rel = ", ".join(str(path.relative_to(ROOT)) for path in missing)
        return fail(f"missing confirmation-applier files: {rel}")

    payload = {
        "known_target": "dwinomarll/maverick-cockpit",
        "owner_boundary": "dwinomarll",
        "access_method": "github_cli_authenticated",
        "write_gate": "github_publish",
        "allowed_action": "prepare branch or private repo publish after explicit runner confirmation",
        "evidence": {
            "origin": "https://github.com/dwinomarll/TGAOTU.git",
            "candidate_branch": "codex/maverick-cockpit",
        },
    }
    invalid = evaluate_confirmation("github_global_repo", "MAVERICK-CONFIRM github_publish wrong-action", payload)
    if invalid.get("allowed"):
        return fail("confirmation applier must deny invalid token")
    if invalid.get("external_mutation_attempted"):
        return fail("confirmation applier must not attempt external mutation")

    valid_token = f"MAVERICK-CONFIRM github_publish {CONFIRMATION_ACTION_ID}"
    valid = evaluate_confirmation("github_global_repo", valid_token, payload)
    if not valid.get("allowed"):
        return fail(f"confirmation applier valid dry-run denied: {valid.get('reason')}")
    if valid.get("external_mutation_attempted"):
        return fail("confirmation applier valid dry-run must remain local-only")

    original = load_json(LIVE_TARGETS_PATH)
    updated, assessment = build_confirmed_targets("github_global_repo", valid_token, payload)
    if not assessment.get("allowed"):
        return fail("confirmation applier build_confirmed_targets should allow valid local update")
    if original == updated:
        return fail("confirmation applier should produce an updated local ledger copy")
    actual_after = load_json(LIVE_TARGETS_PATH)
    if actual_after != original:
        return fail("confirmation applier dry-run validation must not modify live-targets.json")

    confirmed = next(target for target in updated["targets"] if target["id"] == "github_global_repo")
    if confirmed.get("confirmation_status") != "confirmed":
        return fail("confirmation applier updated copy must mark target confirmed")
    if confirmed.get("external_mutation_allowed"):
        return fail("confirmation applier must not set external_mutation_allowed true")

    missing_doc_terms = require_terms(
        CONFIRMATION_APPLIER_DOC,
        ["phase7-live-target-confirmation", "Dry-run mode", "does not publish"],
    )
    if missing_doc_terms:
        return fail(f"docs/maverick-confirmation-applier.md missing terms: {', '.join(missing_doc_terms)}")

    print("PASS: Maverick Cockpit confirmation applier validates explicit tokens without external mutation.")
    return 0


def validate_live_targets() -> int:
    if validate_confirmation_applier() != 0:
        return 1

    missing = [path for path in [LIVE_TARGETS_PATH, LIVE_TARGETS_DOC] if not path.exists()]
    if missing:
        rel = ", ".join(str(path.relative_to(ROOT)) for path in missing)
        return fail(f"missing live-target files: {rel}")

    try:
        targets_doc = load_json(LIVE_TARGETS_PATH)
    except ValueError as exc:
        return fail(str(exc))

    required_targets = {
        "github_global_repo",
        "icloud_destination",
        "notion_live_launch_team",
        "gmail_mailbox_lane",
        "slack_maverick_app",
        "google_calendar_lane",
    }
    targets = targets_doc.get("targets")
    if not isinstance(targets, list):
        return fail("live-targets.json must contain targets")

    target_by_id = {target.get("id"): target for target in targets if isinstance(target, dict)}
    missing_targets = sorted(required_targets - set(target_by_id))
    if missing_targets:
        return fail(f"live-targets.json missing targets: {', '.join(missing_targets)}")

    gate_contract = load_json(WRITE_GATE_CONTRACT_PATH)
    gate_ids = {gate.get("id") for gate in gate_contract.get("gates", [])}
    for target_id, target in target_by_id.items():
        gate_id = target.get("write_gate")
        if gate_id not in gate_ids:
            return fail(f"{target_id} references unknown write gate: {gate_id}")
        evidence = target.get("evidence_required")
        if not isinstance(evidence, list) or not evidence:
            return fail(f"{target_id} must list evidence_required")

    pending = sorted(
        target_id
        for target_id, target in target_by_id.items()
        if target.get("confirmation_status") != "confirmed"
    )
    if pending:
        return fail(f"live targets pending confirmation: {', '.join(pending)}")

    missing_doc_terms = require_terms(
        LIVE_TARGETS_DOC,
        ["github_global_repo", "icloud_destination", "notion_live_launch_team", "gmail_mailbox_lane", "slack_maverick_app", "google_calendar_lane"],
    )
    if missing_doc_terms:
        return fail(f"docs/maverick-live-targets.md missing terms: {', '.join(missing_doc_terms)}")

    print("PASS: Maverick Cockpit live targets are confirmed.")
    return 0


def _file_sha256(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_icloud_export() -> int:
    if validate_confirmation_applier() != 0:
        return 1

    destination_root = DEFAULT_DESTINATION_ROOT
    destination_package = destination_root / DESTINATION_PACKAGE_NAME
    workflow_handoff = destination_root / WORKFLOW_HANDOFF_NAME
    missing = [
        path
        for path in [
            ICLOUD_EXPORT_DOC,
            MAVERICK_WORKFLOW_DOC,
            ICLOUD_EXPORT_MANIFEST_PATH,
            destination_root,
            destination_package,
            workflow_handoff,
            ROOT / "factory" / "maverick_export_icloud.py",
        ]
        if not path.exists()
    ]
    if missing:
        display = ", ".join(str(path) for path in missing)
        return fail(f"missing iCloud export files: {display}")

    try:
        manifest = load_json(ICLOUD_EXPORT_MANIFEST_PATH)
        assembly = load_json(GLOBAL_REPO_ASSEMBLY_MANIFEST_PATH)
        live_targets = load_json(LIVE_TARGETS_PATH)
    except ValueError as exc:
        return fail(str(exc))

    if manifest.get("action_id") != ICLOUD_EXPORT_ACTION_ID:
        return fail("iCloud export manifest action_id mismatch")
    if manifest.get("destination_root") != str(destination_root):
        return fail("iCloud export manifest destination_root mismatch")
    if manifest.get("destination_package_dir") != str(destination_package):
        return fail("iCloud export manifest destination_package_dir mismatch")
    if not manifest.get("local_icloud_filesystem_write_performed"):
        return fail("iCloud export manifest must record the local filesystem copy")
    if manifest.get("slack_write_attempted"):
        return fail("iCloud export must not attempt Slack writes")

    gate = manifest.get("gate") or {}
    if gate.get("id") != "icloud_artifact_export" or not gate.get("allowed") or not gate.get("token_matches"):
        return fail("iCloud export manifest must include an allowed tokened gate result")

    icloud_target = next(
        (target for target in live_targets.get("targets", []) if target.get("id") == "icloud_destination"),
        None,
    )
    if not icloud_target or icloud_target.get("confirmation_status") != "confirmed":
        return fail("icloud_destination must be confirmed in live-targets.json")

    missing_preserved = [item for item in PRESERVED_TOP_LEVEL_ITEMS if not (destination_root / item).exists()]
    if missing_preserved:
        return fail(f"existing iCloud MAVERICK items were not preserved: {', '.join(missing_preserved)}")

    workflow_text = workflow_handoff.read_text(encoding="utf-8")
    if "Maverick Cockpit Workflow" not in workflow_text or "legacy Slack signal watch remains read-only" not in workflow_text:
        return fail("iCloud workflow handoff is missing required workflow terms")

    copied_files = manifest.get("copied_files")
    if not isinstance(copied_files, list) or not copied_files:
        return fail("iCloud export manifest must list copied files")
    if manifest.get("copied_file_count") != assembly.get("file_count"):
        return fail("iCloud copied file count must match the repo assembly file count")

    for file_info in copied_files:
        source_rel = file_info.get("source")
        target_raw = file_info.get("target")
        digest = file_info.get("sha256")
        if not isinstance(source_rel, str) or not isinstance(target_raw, str):
            return fail("iCloud copied file entry must include source and target")
        if not isinstance(digest, str) or len(digest) != 64:
            return fail(f"iCloud copied file missing sha256: {target_raw}")
        source = ROOT / source_rel
        target = Path(target_raw)
        if not source.exists() or not target.exists():
            return fail(f"iCloud copied file missing on disk: {source_rel}")
        if _file_sha256(source) != digest or _file_sha256(target) != digest:
            return fail(f"iCloud copied file hash mismatch: {target_raw}")

    missing_doc_terms = require_terms(
        ICLOUD_EXPORT_DOC,
        ["MAVERICK_COCKPIT_WORKFLOW.md", "maverick_export_icloud.py", "A0BALRB6CNQ", "slack_write"],
    )
    if missing_doc_terms:
        return fail(f"docs/maverick-icloud-export.md missing terms: {', '.join(missing_doc_terms)}")

    print("PASS: Maverick Cockpit workflow package is copied to the local iCloud MAVERICK folder.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Maverick Cockpit artifacts")
    parser.add_argument(
        "--phase",
        choices=[
            "phase1",
            "source-map",
            "ledger",
            "dashboard",
            "adapters",
            "write-gates",
            "global-repo",
            "repo-assembly",
            "target-discovery",
            "confirmation-applier",
            "notion-overview",
            "notion-bridge",
            "operating-loop",
            "comms-outbox",
            "activation-checklist",
            "learning-ledger",
            "slack-bridge",
            "github-bridge",
            "icloud-export",
            "live-targets",
        ],
        default="phase1",
    )
    args = parser.parse_args()

    if args.phase == "source-map":
        return validate_source_map()

    if args.phase == "ledger":
        return validate_ledger()

    if args.phase == "dashboard":
        return validate_dashboard()

    if args.phase == "adapters":
        return validate_adapters()

    if args.phase == "notion-overview":
        return validate_notion_overview()

    if args.phase == "notion-bridge":
        return validate_notion_bridge()

    if args.phase == "operating-loop":
        return validate_operating_loop()

    if args.phase == "comms-outbox":
        return validate_comms_outbox()

    if args.phase == "activation-checklist":
        return validate_activation_checklist()

    if args.phase == "learning-ledger":
        return validate_learning_ledger()

    if args.phase == "slack-bridge":
        return validate_slack_bridge()

    if args.phase == "github-bridge":
        return validate_github_bridge()

    if args.phase == "write-gates":
        return validate_write_gates()

    if args.phase == "global-repo":
        return validate_global_repo()

    if args.phase == "repo-assembly":
        return validate_repo_assembly()

    if args.phase == "target-discovery":
        return validate_target_discovery()

    if args.phase == "confirmation-applier":
        return validate_confirmation_applier()

    if args.phase == "icloud-export":
        return validate_icloud_export()

    if args.phase == "live-targets":
        return validate_live_targets()

    if args.phase != "phase1":
        return fail(f"{args.phase} validation is planned but not implemented yet")

    return validate_phase1()


if __name__ == "__main__":
    raise SystemExit(main())
