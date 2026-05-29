#!/usr/bin/env python3
"""Tests for the Ptah Chatbox deterministic core.

The OpenRouter call (_openrouter_chat) and the factory run (run_factory) are
monkeypatched — no live network, no real build. Covers slug/name safety, VISION
assembly, fence stripping, and the prompt -> VISION -> write -> factory wiring.
Run: python3 chatbox/test_chatbox.py
"""

import importlib.util
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _load():
    spec = importlib.util.spec_from_file_location("ptah_chatbox", HERE / "server.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


srv = _load()


# ── slugify (path-traversal safety) ────────────────────────────────────────────

def test_slugify_basic():
    assert srv.slugify("My Cool App!") == "my-cool-app"

def test_slugify_blocks_traversal_chars():
    # slashes / dots collapse to hyphens -> no path escape from a hostile name
    assert srv.slugify("../../etc/passwd") == "etc-passwd"
    assert "/" not in srv.slugify("a/b") and ".." not in srv.slugify("a..b")

def test_slugify_empty_falls_back():
    assert srv.slugify("   ") == "app"


# ── extract_app_name ────────────────────────────────────────────────────────────

def test_extract_app_name_from_vision():
    v = "## Name\nWord Counter\n\n## What it does\ncounts words\n"
    assert srv.extract_app_name(v) == "word-counter"

def test_extract_app_name_fallback_when_missing():
    assert srv.extract_app_name("## What it does\nno name section", "fallback") == "fallback"


# ── build_vision_messages ───────────────────────────────────────────────────────

def test_build_vision_messages_carries_prompt():
    msgs = srv.build_vision_messages("build a reverse tool")
    assert msgs[0]["role"] == "system" and "VISION.md" in msgs[0]["content"]
    assert msgs[1]["role"] == "user" and msgs[1]["content"] == "build a reverse tool"


# ── derive_vision (OpenRouter mocked) ───────────────────────────────────────────

_CANNED = ("## Name\nReverse Tool\n\n## What it does\nReverses a file's lines.\n\n"
           "## How to run\npython3 reverse.py FILE\n\n## Success Signal\n"
           "`python3 reverse.py s.txt` prints the lines reversed; exit 0.")

def test_derive_vision_parses_name_and_body():
    orig = srv._openrouter_chat
    srv._openrouter_chat = lambda messages: _CANNED
    try:
        slug, vision = srv.derive_vision("reverse a file")
    finally:
        srv._openrouter_chat = orig
    assert slug == "reverse-tool"
    assert "## Success Signal" in vision and "reverse.py" in vision

def test_derive_vision_strips_markdown_fence():
    orig = srv._openrouter_chat
    srv._openrouter_chat = lambda messages: "```markdown\n" + _CANNED + "\n```"
    try:
        slug, vision = srv.derive_vision("reverse a file")
    finally:
        srv._openrouter_chat = orig
    assert slug == "reverse-tool" and not vision.startswith("```")


# ── handle_chat wiring (OpenRouter + factory both mocked) ──────────────────────

def test_handle_chat_writes_vision_and_runs_factory():
    orig_chat, orig_run, orig_active = srv._openrouter_chat, srv.run_factory, srv.ACTIVE_DIR
    captured = {}

    def fake_run(app_dir):
        captured["app_dir"] = Path(app_dir)
        captured["vision"] = (Path(app_dir) / "VISION.md").read_text()
        return {"status": "delivered", "files": ["reverse.py"], "delivery_report": "ok"}

    try:
        with tempfile.TemporaryDirectory() as d:
            srv._openrouter_chat = lambda messages: _CANNED
            srv.run_factory = fake_run
            srv.ACTIVE_DIR = Path(d)
            result = srv.handle_chat("reverse a file")
    finally:
        srv._openrouter_chat, srv.run_factory, srv.ACTIVE_DIR = orig_chat, orig_run, orig_active

    assert result["app"] == "reverse-tool"
    assert result["status"] == "delivered" and result["files"] == ["reverse.py"]
    assert "## Name" in captured["vision"]                 # VISION was written for the factory
    assert captured["app_dir"].name == "reverse-tool"

def test_handle_chat_rejects_empty_prompt():
    assert "error" in srv.handle_chat("   ")


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
