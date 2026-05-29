#!/usr/bin/env python3
"""
T.G.A.O.T.U. Escalation Gate
3-case-only Edwin contact protocol. Called by build-loop.py when a phase
fails all repair attempts.

Cases that reach Edwin:
  1. STRUCTURAL — phase requires a decision that changes the vision itself
  2. CREDENTIAL — service needs a key/account Edwin hasn't provided
  3. BUDGET     — deploying a service would incur cost Edwin hasn't approved

Everything else is handled by the Manager (Eva). Edwin is not contacted.
"""

import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
# Required from runtime config — NO hardcoded fallback. A baked-in chat id would
# let any environment with a bot token silently leak blockers to one person.
TELEGRAM_CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID", "")

# Keywords that classify a blocker into one of the 3 escalation cases
_CREDENTIAL_SIGNALS = [
    "api key", "api_key", "_token", "_secret", "token", "secret",
    "credential", "auth", "password", "account", "login",
    "permission denied", "unauthorized", "403", "401"
]
_BUDGET_SIGNALS = [
    "cost", "billing", "paid", "subscription", "quota", "limit exceeded",
    "rate limit", "pricing", "charge", "invoice", "stripe", "payment"
]

# ── Classifier ────────────────────────────────────────────────────────────────

def classify_blocker(reason: str) -> str:
    """
    Returns 'structural' | 'credential' | 'budget' | 'manager_only'.
    manager_only = don't contact Edwin — Eva handles it.
    """
    r = reason.lower()

    if any(sig in r for sig in _CREDENTIAL_SIGNALS):
        return "credential"

    if any(sig in r for sig in _BUDGET_SIGNALS):
        return "budget"

    # Structural: can't determine without Edwin's intent. Be conservative —
    # only escalate if the reason explicitly mentions vision scope, requirements,
    # or something that changes what the app fundamentally is.
    structural_signals = [
        "vision", "scope", "requirement", "spec", "fundamental",
        "architecture change", "incompatible", "conflict with"
    ]
    if any(sig in r for sig in structural_signals):
        return "structural"

    # Default: Manager handles it — no Edwin ping
    return "manager_only"


# ── Message Builder ───────────────────────────────────────────────────────────

def _build_message(app_name: str, phase_num: int, phase_title: str,
                   reason: str, case: str) -> str:
    case_labels = {
        "structural": "🏗️ STRUCTURAL DECISION NEEDED",
        "credential": "🔑 CREDENTIAL NEEDED",
        "budget":     "💰 BUDGET APPROVAL NEEDED",
    }
    label = case_labels.get(case, "🚨 BUILD BLOCKED")

    return (
        f"📐 *T.G.A.O.T.U. Factory*\n"
        f"{label}\n\n"
        f"*App:* `{app_name}`\n"
        f"*Phase {phase_num}:* {phase_title}\n\n"
        f"*Issue:* {reason[:300]}\n\n"
        f"Reply with your decision and I'll resume the build."
    )


# ── Telegram Send ─────────────────────────────────────────────────────────────

def _send_telegram(message: str) -> bool:
    """Send message to Edwin via Telegram. Returns True only on confirmed delivery."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        # Fail closed: without BOTH a token and an explicitly configured recipient
        # we do not guess where to send — the escalation file is the record instead.
        print("[Escalation] TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID not both set — logging to file only.")
        return False

    try:
        payload = json.dumps({
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }).encode()
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            data=payload,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read())
            return result.get("ok", False)
    except Exception as e:
        print(f"[Escalation] Telegram send failed: {e}")
        return False


# ── Main Entry Point ──────────────────────────────────────────────────────────

def fire(app_name: str, phase_num: int, phase_title: str,
         reason: str, app_dir: Path) -> dict:
    """
    Classify the blocker. If it's one of the 3 Edwin cases, send Telegram.
    Always write the ESCALATION file.

    Returns: {"case": str, "escalation_required": bool, "notified_edwin": bool,
             "escalation_path": str}
    `escalation_required` is whether this blocker should reach Edwin;
    `notified_edwin` is whether Telegram actually confirmed delivery. A caller
    that pauses for Edwin's decision must key off `notified_edwin`, not intent.
    """
    case = classify_blocker(reason)
    escalation_required = (case != "manager_only")

    # Attempt delivery first so the escalation file records what actually happened.
    delivered = False
    if escalation_required:
        message = _build_message(app_name, phase_num, phase_title, reason, case)
        delivered = _send_telegram(message)
        status = "delivered" if delivered else "FAILED — file only, Edwin NOT reached"
        print(f"[Escalation] Case: {case} | Telegram: {status}")
    else:
        print("[Escalation] Case: manager_only — Eva handles, Edwin not pinged")

    if not escalation_required:
        notified_line = "no — Manager handles"
    elif delivered:
        notified_line = "yes — delivered via Telegram"
    else:
        notified_line = "NO — delivery failed, awaiting manual relay"

    escalation_path = app_dir / f"ESCALATION_P{phase_num}.md"
    escalation_path.write_text(
        f"# ESCALATION — Phase {phase_num}: {phase_title}\n\n"
        f"**App:** {app_name}\n"
        f"**Case:** {case}\n"
        f"**Time:** {datetime.now(timezone.utc).isoformat()}\n"
        f"**Edwin notified:** {notified_line}\n\n"
        f"## Reason\n{reason}\n\n"
        f"## Resolution\n_Pending Edwin's decision._\n\n"
        f"---\n"
        f"*3-case escalation gate: structural | credential | budget → Edwin.*\n"
        f"*All other blockers → Manager (Eva) resolves without Edwin.*\n"
    )

    return {
        "case": case,
        "escalation_required": escalation_required,
        "notified_edwin": delivered,
        "escalation_path": str(escalation_path),
    }


# ── CLI (test mode) ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Quick classifier smoke test
    test_cases = [
        ("Missing ANTHROPIC_API_KEY in environment", "credential"),
        ("Deployment to Railway would cost ~$5/mo", "budget"),
        ("Vision says iOS but app requires macOS features", "structural"),
        ("pytest failed: assertion error in test_utils.py", "manager_only"),
    ]
    print("Escalation Gate — classifier smoke test\n")
    all_pass = True
    for reason, expected in test_cases:
        got = classify_blocker(reason)
        ok = got == expected
        all_pass = all_pass and ok
        print(f"  {'✅' if ok else '❌'} '{reason[:50]}...' → {got} (expected {expected})")
    print(f"\n{'All tests passed.' if all_pass else 'Some tests FAILED.'}")
    sys.exit(0 if all_pass else 1)
