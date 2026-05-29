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

def test_validate_from_plan_scalar_expect_contains_is_whole_string():
    # regression: a scalar "olleh" must NOT char-match against "hello"
    with tempfile.TemporaryDirectory() as d:
        plan = {"checks": [{"command": "echo hello", "expect_exit": "0", "expect_contains": "olleh"}]}
        ok, _ = bl.validate_from_plan(Path(d), plan)
        assert not ok

def test_validate_from_plan_scalar_expect_contains_real_substring_passes():
    with tempfile.TemporaryDirectory() as d:
        plan = {"checks": [{"command": "echo hello world", "expect_exit": "0", "expect_contains": "hello"}]}
        ok, log = bl.validate_from_plan(Path(d), plan)
        assert ok, log

def test_validate_from_plan_ignores_non_dict_checks():
    with tempfile.TemporaryDirectory() as d:
        plan = {"checks": ["junk", {"command": "echo ok", "expect_exit": "0", "expect_contains": ["ok"]}]}
        ok, log = bl.validate_from_plan(Path(d), plan)
        assert ok, log


# ── extract_check_plan (shape guard; LLM call monkeypatched) ──────────────────

def _patched_plan(raw_json):
    orig_cc, orig_llm = bl.dispatch_via_claude_code, bl.call_llm
    bl.dispatch_via_claude_code = lambda s, u: raw_json
    bl.call_llm = lambda s, u: ""
    try:
        return bl.extract_check_plan("vision")
    finally:
        bl.dispatch_via_claude_code, bl.call_llm = orig_cc, orig_llm

def test_extract_check_plan_rejects_non_list_checks():
    assert _patched_plan('{"checks": "echo hi"}') is None

def test_extract_check_plan_rejects_empty_checks():
    assert _patched_plan('{"checks": []}') is None

def test_extract_check_plan_coerces_non_dict_fixtures():
    plan = _patched_plan('{"checks": [{"command": "echo hi"}], "fixtures": []}')
    assert plan is not None and plan["fixtures"] == {}


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


# ── parse_phases ──────────────────────────────────────────────────────────────

_TWO_PHASE_BP = """# BLUEPRINT — demo

## File Tree
```
a.py
b.py
```

## Phases

### Phase 1 — Build the core
- Goal: make a.py
- Worker: Python
- Deliverables:
  - src/a.py
- Validation:
  - Command: `echo ok`
  - Pass condition: prints ok

### Phase 2 — Add the wrapper
- Goal: make b.py
- Worker: Python
- Deliverables:
  - src/b.py
- Validation:
  - Command: `echo ok`
  - Pass condition: prints ok

## Dependency Graph
Phase 1 → Phase 2
"""


def test_parse_phases_extracts_deliverables_and_command():
    phases = bl.parse_phases(_TWO_PHASE_BP)
    assert len(phases) == 2, phases
    assert phases[0]["number"] == 1 and phases[1]["number"] == 2
    assert phases[0]["deliverables"] == ["a.py"]   # leaf only
    assert phases[1]["deliverables"] == ["b.py"]
    assert phases[0]["command"] == "echo ok"
    assert phases[0]["pass_condition"] and "ok" in phases[0]["pass_condition"].lower()


def test_parse_phases_empty_when_no_phase_blocks():
    assert bl.parse_phases("# BLUEPRINT\n## File Tree\nmain.py\n## Notes\nnothing here") == []


# ── validate_phase ────────────────────────────────────────────────────────────

def test_validate_phase_pass_on_zero_exit():
    with tempfile.TemporaryDirectory() as d:
        ok, log = bl.validate_phase(Path(d), "echo wordcount-7", "prints a wordcount")
        assert ok, log

def test_validate_phase_passes_when_output_lacks_pass_condition_words():
    # regression: pass_condition is advisory, NOT a substring gate. exit 0 must pass
    # even when the condition's words never appear in output (no brittle token match).
    with tempfile.TemporaryDirectory() as d:
        ok, _ = bl.validate_phase(Path(d), "echo 7", "prints a wordcount")
        assert ok

def test_validate_phase_fail_on_nonzero_exit():
    with tempfile.TemporaryDirectory() as d:
        ok, log = bl.validate_phase(Path(d), "exit 1", "anything")
        assert not ok and "FAIL" in log

def test_validate_phase_no_command_is_build_validated():
    with tempfile.TemporaryDirectory() as d:
        ok, log = bl.validate_phase(Path(d), None, None)
        assert ok and "build" in log.lower()


# ── _seq_fixture: write VISION/BLUEPRINT/BUILD_STATE for a sequential run ──────

def _write_app(d, blueprint, vision="run `python3 a.py file`\nSuccess: prints a count"):
    p = Path(d)
    (p / "VISION.md").write_text(vision, encoding="utf-8")
    (p / "BLUEPRINT.md").write_text(blueprint, encoding="utf-8")
    import json
    (p / "BUILD_STATE.json").write_text(
        json.dumps({"app_name": "demo",
                    "phases": [{"number": 1, "status": "pending"},
                               {"number": 2, "status": "pending"}]}),
        encoding="utf-8")
    return p


def _run_main(app_dir):
    """Invoke bl.main() against app_dir, capturing the sys.exit code. Returns the code."""
    import json
    orig_argv = sys.argv
    sys.argv = ["build-loop.py", str(app_dir)]
    try:
        bl.main()
        code = 0
    except SystemExit as e:
        code = e.code if isinstance(e.code, int) else 1
    finally:
        sys.argv = orig_argv
    state = json.loads((Path(app_dir) / "BUILD_STATE.json").read_text())
    return code, state


# ── SEQUENTIAL: phases built in order, both validated ─────────────────────────

def test_sequential_builds_phases_in_order_and_validates():
    bp = _TWO_PHASE_BP
    calls = []

    def fake_dispatch(vision, blueprint, target, siblings, prior, error):
        calls.append(target)
        return f"# {target}\nprint('ok')\n"

    orig_dispatch = bl.dispatch_worker
    orig_plan = bl.extract_check_plan
    bl.dispatch_worker = fake_dispatch
    bl.extract_check_plan = lambda v: None   # skip the final VISION gate / LLM call
    try:
        with tempfile.TemporaryDirectory() as d:
            app = _write_app(d, bp)
            code, state = _run_main(app)
    finally:
        bl.dispatch_worker = orig_dispatch
        bl.extract_check_plan = orig_plan

    assert calls == ["a.py", "b.py"], calls            # phase 1 file before phase 2 file
    assert code == 0, state
    assert state["overall_status"] == "complete"
    assert all(p["status"] == "complete" and p["validated"] for p in state["phases"])


# ── SEQUENTIAL GATING: phase 1 fails → phase 2 never built, escalation names phase 1 ──

def test_sequential_gates_later_phases_when_phase1_fails():
    bp = _TWO_PHASE_BP.replace("- Command: `echo ok`\n  - Pass condition: prints ok",
                               "- Command: `exit 1`\n  - Pass condition: prints ok", 1)
    calls = []

    def fake_dispatch(vision, blueprint, target, siblings, prior, error):
        calls.append(target)
        return f"# {target}\nprint('ok')\n"

    orig_dispatch = bl.dispatch_worker
    orig_plan = bl.extract_check_plan
    bl.dispatch_worker = fake_dispatch
    bl.extract_check_plan = lambda v: None
    try:
        with tempfile.TemporaryDirectory() as d:
            app = _write_app(d, bp)
            code, state = _run_main(app)
    finally:
        bl.dispatch_worker = orig_dispatch
        bl.extract_check_plan = orig_plan

    assert "b.py" not in calls, calls                  # phase 2 worker never called
    assert "a.py" in calls
    assert code == 2, state
    assert state["overall_status"] == "blocked"
    escs = state.get("escalations", [])
    assert escs and "Phase 1" in escs[-1]["reason"], escs


# ── FALLBACK: File Tree present but phases lack Deliverables → single-pass path ─

def test_fallback_single_pass_when_phases_have_no_deliverables():
    bp = """# BLUEPRINT — demo

## File Tree
```
a.py
```

## Phases

### Phase 1 — Core
- Goal: do the thing
- Worker: Python
- Validation:
  - Command: `echo ok`
  - Pass condition: prints ok

## Dependency Graph
Phase 1
"""
    # parse_phases yields a phase with NO deliverables → sequential=False → single pass
    assert bl.parse_phases(bp) and not any(p["deliverables"] for p in bl.parse_phases(bp))

    calls = []

    def fake_dispatch(vision, blueprint, target, siblings, prior, error):
        # single-pass builds the detect_target_files targets (a.py), validates whole VISION
        calls.append(target)
        return "import sys\np=sys.argv[1]\nopen(p).read()\nprint(len(open(p).read().split()))\n"

    orig_dispatch = bl.dispatch_worker
    orig_plan = bl.extract_check_plan
    bl.dispatch_worker = fake_dispatch
    bl.extract_check_plan = lambda v: None   # force CLI fallback validation
    try:
        with tempfile.TemporaryDirectory() as d:
            app = _write_app(d, bp)
            code, state = _run_main(app)
    finally:
        bl.dispatch_worker = orig_dispatch
        bl.extract_check_plan = orig_plan

    # single-pass behavior: target from File Tree (a.py) was built, app shipped via CLI fallback
    assert calls and calls[0] == "a.py", calls
    assert code == 0, state
    assert state["overall_status"] == "complete"


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
