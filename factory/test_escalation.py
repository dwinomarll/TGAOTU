#!/usr/bin/env python3
"""Tests for factory/escalation.py — classifier + fail-closed delivery semantics.

Covers the 3-case classifier and the two correctness fixes: no hardcoded chat-id
fallback (fail closed), and `notified_edwin` reflecting confirmed delivery rather
than intent. Dependency-free; run: `python3 factory/test_escalation.py`
"""

import importlib.util
import sys
import tempfile
from pathlib import Path

FACTORY = Path(__file__).resolve().parent


def _load():
    spec = importlib.util.spec_from_file_location("escalation", FACTORY / "escalation.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


esc = _load()


# ── classifier ────────────────────────────────────────────────────────────────

def test_classify_credential():
    assert esc.classify_blocker("Missing ANTHROPIC_API_KEY in environment") == "credential"

def test_classify_budget():
    assert esc.classify_blocker("Deployment to Railway would cost ~$5/mo") == "budget"

def test_classify_structural():
    assert esc.classify_blocker("conflict with the vision scope") == "structural"

def test_classify_manager_only():
    assert esc.classify_blocker("pytest failed: assertion error in test_utils.py") == "manager_only"


# ── P1: no hardcoded recipient, fail closed ────────────────────────────────────

def test_no_hardcoded_chat_id_default():
    # the module must not bake in a personal chat id as the default
    assert "1583595373" not in (esc.TELEGRAM_CHAT_ID or "")

def test_send_telegram_fails_closed_without_full_config():
    orig = (esc.TELEGRAM_BOT_TOKEN, esc.TELEGRAM_CHAT_ID)
    try:
        esc.TELEGRAM_BOT_TOKEN, esc.TELEGRAM_CHAT_ID = "tok", ""   # token, no recipient
        assert esc._send_telegram("hi") is False
        esc.TELEGRAM_BOT_TOKEN, esc.TELEGRAM_CHAT_ID = "", "123"   # recipient, no token
        assert esc._send_telegram("hi") is False
    finally:
        esc.TELEGRAM_BOT_TOKEN, esc.TELEGRAM_CHAT_ID = orig


# ── P2: notified_edwin = confirmed delivery, not intent ─────────────────────────

def test_fire_not_notified_when_delivery_fails():
    orig = (esc.TELEGRAM_BOT_TOKEN, esc.TELEGRAM_CHAT_ID)
    try:
        esc.TELEGRAM_BOT_TOKEN, esc.TELEGRAM_CHAT_ID = "", ""   # delivery will fail
        with tempfile.TemporaryDirectory() as d:
            r = esc.fire("app", 1, "phase", "Missing API_KEY", Path(d))
            assert r["escalation_required"] is True
            assert r["notified_edwin"] is False
            body = (Path(d) / "ESCALATION_P1.md").read_text()
            assert "NO" in body or "failed" in body.lower()
    finally:
        esc.TELEGRAM_BOT_TOKEN, esc.TELEGRAM_CHAT_ID = orig

def test_fire_manager_only_does_not_notify():
    with tempfile.TemporaryDirectory() as d:
        r = esc.fire("app", 2, "phase", "pytest assertion error", Path(d))
        assert r["escalation_required"] is False and r["notified_edwin"] is False

def test_fire_writes_escalation_file():
    with tempfile.TemporaryDirectory() as d:
        esc.fire("widget", 3, "deploy", "needs a paid subscription", Path(d))
        assert (Path(d) / "ESCALATION_P3.md").exists()


if __name__ == "__main__":
    fails = 0
    tests = sorted((n, f) for n, f in globals().items() if n.startswith("test_") and callable(f))
    for name, fn in tests:
        try:
            fn()
            print(f"PASS {name}")
        except Exception as e:  # noqa: BLE001
            fails += 1
            print(f"FAIL {name}: {type(e).__name__}: {e}")
    print(f"\n{len(tests) - fails}/{len(tests)} passed")
    sys.exit(1 if fails else 0)
