#!/usr/bin/env python3
"""Characterization tests for factory/build-loop.py (v4).

Covers the deterministic core — file discovery, entrypoint detection, output
sanitizing, VISION-plan + CLI-fallback validation, the subprocess runner, and
the state/report writers. The LLM-calling paths (dispatch_*, extract_check_plan,
main) are exercised by the live proving run, not here.

Dependency-free: each test is a `test_*` function using `assert`; `__main__`
runs them all and reports PASS/FAIL. build-loop.py has a hyphen so it is loaded
via importlib. Run: `python3 factory/test_build_loop.py`
"""

import importlib.util
import sys
import tempfile
from pathlib import Path

FACTORY = Path(__file__).resolve().parent


def _load():
    spec = importlib.util.spec_from_file_location("build_loop", FACTORY / "build-loop.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


bl = _load()


# ── strip_to_code ─────────────────────────────────────────────────────────────

def test_strip_to_code_removes_wrapping_fence():
    assert bl.strip_to_code("```python\nx = 1\n```") == "x = 1"

def test_strip_to_code_removes_think_block():
    assert bl.strip_to_code("<think>plan</think>\nx = 1") == "x = 1"

def test_strip_to_code_passthrough_plain():
    assert bl.strip_to_code("x = 1\ny = 2") == "x = 1\ny = 2"


# ── detect_target_files ───────────────────────────────────────────────────────

def test_detect_target_files_from_file_tree_section():
    bp = "## File Tree\n```\napp/\n  main.py\n  utils.py\n```\n## Phases\nstuff"
    assert bl.detect_target_files("myapp", bp) == ["main.py", "utils.py"]

def test_detect_target_files_dedup_and_leaf_only():
    bp = "# File Structure\nsrc/main.py\nsrc/main.py\nlib/helper.py\n# Next"
    assert bl.detect_target_files("a", bp) == ["main.py", "helper.py"]

def test_detect_target_files_fallback_when_no_tree():
    assert bl.detect_target_files("widget", "no tree here") == ["widget.py"]


# ── detect_entrypoint ─────────────────────────────────────────────────────────

def test_detect_entrypoint_prefers_vision_command():
    assert bl.detect_entrypoint("run `python3 cli.py file`", ["util.py", "cli.py"]) == "cli.py"

def test_detect_entrypoint_convention_main():
    assert bl.detect_entrypoint("no command here", ["util.py", "main.py"]) == "main.py"

def test_detect_entrypoint_first_fallback():
    assert bl.detect_entrypoint("nothing", ["only.py", "other.py"]) == "only.py"


# ── run ───────────────────────────────────────────────────────────────────────

def test_run_captures_exit_and_output():
    with tempfile.TemporaryDirectory() as d:
        rc, out = bl.run(["bash", "-c", "echo hi; exit 3"], Path(d))
        assert rc == 3 and "hi" in out


# ── validate_from_plan ────────────────────────────────────────────────────────

def test_validate_from_plan_pass_path():
    with tempfile.TemporaryDirectory() as d:
        plan = {"fixtures": {"in.txt": "data"},
                "checks": [{"command": "cat in.txt", "expect_exit": "0", "expect_contains": ["data"]}]}
        ok, log = bl.validate_from_plan(Path(d), plan)
        assert ok, log

def test_validate_from_plan_fails_on_missing_substring():
    with tempfile.TemporaryDirectory() as d:
        plan = {"checks": [{"command": "echo hello", "expect_exit": "0", "expect_contains": ["GOODBYE"]}]}
        ok, log = bl.validate_from_plan(Path(d), plan)
        assert not ok and "FAIL" in log

def test_validate_from_plan_nonzero_expectation():
    with tempfile.TemporaryDirectory() as d:
        plan = {"checks": [{"command": "exit 1", "expect_exit": "nonzero", "expect_contains": []}]}
        ok, _ = bl.validate_from_plan(Path(d), plan)
        assert ok

def test_validate_from_plan_empty_checks_is_false():
    with tempfile.TemporaryDirectory() as d:
        ok, _ = bl.validate_from_plan(Path(d), {"checks": []})
        assert not ok


# ── validate_cli_fallback ─────────────────────────────────────────────────────

def test_validate_cli_fallback_pass_with_counting_script():
    with tempfile.TemporaryDirectory() as d:
        # entrypoint: prints a digit for a real file arg, errors (exit!=0) for a missing one
        (Path(d) / "main.py").write_text(
            "import sys\n"
            "p = sys.argv[1]\n"
            "open(p).read()\n"          # raises -> non-zero exit if file missing
            "print(len(open(p).read().split()))\n",
            encoding="utf-8")
        ok, log = bl.validate_cli_fallback(Path(d), "main.py")
        assert ok, log

def test_validate_cli_fallback_fails_when_no_error_on_missing():
    with tempfile.TemporaryDirectory() as d:
        # bad entrypoint: always exits 0, never errors on a missing file -> should FAIL check 2
        (Path(d) / "main.py").write_text("print(1)\n", encoding="utf-8")
        ok, _ = bl.validate_cli_fallback(Path(d), "main.py")
        assert not ok


# ── write_state / delivery_report ─────────────────────────────────────────────

def test_write_state_persists_and_timestamps():
    import json
    with tempfile.TemporaryDirectory() as d:
        bl.write_state(Path(d), {"app_name": "x", "overall_status": "in_progress"})
        saved = json.loads((Path(d) / "BUILD_STATE.json").read_text())
        assert saved["app_name"] == "x" and "last_updated" in saved

def test_delivery_report_delivered_contents():
    with tempfile.TemporaryDirectory() as d:
        bl.delivery_report(Path(d), "myapp", ["main.py", "util.py"], "main.py", 1, "all pass", True)
        body = (Path(d) / "DELIVERY_REPORT.md").read_text()
        assert "DELIVERED" in body and "myapp" in body and "main.py" in body and "util.py" in body

def test_delivery_report_blocked_contents():
    with tempfile.TemporaryDirectory() as d:
        bl.delivery_report(Path(d), "myapp", ["main.py"], "main.py", 4, "fail log", False)
        body = (Path(d) / "DELIVERY_REPORT.md").read_text()
        assert "BLOCKED" in body


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
