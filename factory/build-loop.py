#!/usr/bin/env python3
"""
T.G.A.O.T.U. Build Loop — Stage 3 of the App Factory Protocol (Blueprint III).

Turns a blueprint into a working artifact. Reads
factory/active/<app>/{VISION.md, BLUEPRINT.md, BUILD_STATE.json}, dispatches a
Worker per source file, validates the entrypoint against the VISION's success
signal, self-repairs up to 3 times, escalates if it can't, updates BUILD_STATE,
and writes a Delivery Report. No human in the loop.

Worker routing (Blueprint II router): code-extension targets are dispatched to
Claude Code (`--print --permission-mode bypassPermissions`); other tasks use the
local LLM.

v3: multi-file builds. All source files in the blueprint's File Tree are built
(flat, one Worker each, with sibling files as read-only context). Single-file
apps are the one-element case. Nested directories / per-phase orchestration is future.

Usage:
    python3 factory/build-loop.py factory/active/<app>/
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

FACTORY_DIR = Path(__file__).parent
sys.path.insert(0, str(FACTORY_DIR))
from architect import call_llm, now_edt_iso, now_edt_display  # reuse the proven backend

MAX_REPAIRS = 3
FIXTURE_NAME = "sample.txt"
FIXTURE_TEXT = "hello world\nthe quick brown fox\n"  # 2 lines, 6 words
CODE_EXTS = (".py", ".js", ".ts", ".sh", ".go", ".rb", ".swift", ".rs", ".java")


# ── File discovery ────────────────────────────────────────────────────────────

def strip_to_code(text: str) -> str:
    """Remove qwen3 <think> blocks and a single wrapping markdown fence, if present."""
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
    fence = re.match(r"^```[A-Za-z0-9_+-]*\n(.*)\n```$", text, flags=re.DOTALL)
    return fence.group(1) if fence else text


def detect_target_files(app_name: str, blueprint: str) -> list[str]:
    """All source files from the blueprint's File Tree (relative paths, order-preserved).
    Falls back to a single <app>.py if no File Tree is found."""
    # Grab the "File Tree"/"File Structure" section up to the next heading — robust to
    # whether the LLM fenced it or wrote it as plain text.
    m = re.search(r"#+\s*File (?:Tree|Structure)\b[^\n]*\n(.*?)(?:\n#+\s|\Z)",
                  blueprint, re.DOTALL | re.IGNORECASE)
    block = m.group(1) if m else ""
    files: list[str] = []
    for fm in re.finditer(r"([A-Za-z0-9_./\-]+\.(?:py|js|ts|sh|go|rb|swift|rs|java))", block):
        rel = fm.group(1)  # keep the relative path so subdirectory layouts survive
        if rel not in files:
            files.append(rel)
    return files or [f"{app_name}.py"]


def detect_entrypoint(vision: str, targets: list[str]) -> str:
    """The file the VISION success signal invokes; else a conventional entry name; else first."""
    m = re.search(r"python3?\s+([A-Za-z0-9_\-]+\.py)", vision)
    if m and m.group(1) in targets:
        return m.group(1)
    for cand in ("main.py", "cli.py", "app.py", "__main__.py"):
        if cand in targets:
            return cand
    return targets[0]


# ── Worker ──────────────────────────────────────────────────────────────────

def dispatch_via_claude_code(system: str, user: str) -> str | None:
    """Route a code Worker to Claude Code — Blueprint II router (code -> Claude Code / Codex)
    + Blueprint III agent-assignments (`--print --permission-mode bypassPermissions`).
    Returns the file content, or None to fall back to the local LLM."""
    if not shutil.which("claude"):
        return None
    prompt = (system + "\n\n" + user +
              "\n\nDo NOT use any tools or write files. Respond with ONLY the raw file content.")
    try:
        proc = subprocess.run(
            ["claude", "--print", "--permission-mode", "bypassPermissions", prompt],
            capture_output=True, text=True, timeout=300,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            print("[Build Loop]   backend: Claude Code")
            return proc.stdout
        print(f"[Build Loop]   Claude Code returned nothing (exit {proc.returncode}); falling back")
    except Exception as exc:  # noqa: BLE001
        print(f"[Build Loop]   Claude Code error ({exc}); falling back")
    return None


def dispatch_worker(vision: str, blueprint: str, target: str, siblings: dict[str, str],
                    prior_code: str | None, error_feedback: str | None) -> str:
    system = (
        f"You are a Worker in the T.G.A.O.T.U. factory. You own exactly ONE file: `{target}`. "
        "Write its COMPLETE, final, runnable content so the whole app satisfies the VISION and "
        "BLUEPRINT. Standard library only unless the blueprint says otherwise. "
        "Output ONLY the raw file content — no markdown fences, no commentary."
    )
    msg = f"VISION:\n{vision}\n\n---\nBLUEPRINT:\n{blueprint}\n\n---\nThe one file you own: `{target}`\n"
    if siblings:
        ctx = "\n\n".join(f"# sibling file `{n}` (read-only — do NOT rewrite it):\n{c}"
                          for n, c in siblings.items())
        msg += f"\nOther files in this app (import/reference them, do not duplicate):\n{ctx}\n"
    if prior_code:
        msg += f"\nYour file's current content:\n{prior_code}\n"
    if error_feedback:
        msg += (f"\nThe app FAILED validation:\n{error_feedback}\n"
                f"Fix the cause and output the FULL corrected `{target}`.")
    if target.endswith(CODE_EXTS):
        out = dispatch_via_claude_code(system, msg)
        if out is not None:
            return strip_to_code(out)
    return strip_to_code(call_llm(system, msg))


# ── Validation (against the VISION success signal) ────────────────────────────

def run(cmd: list[str], cwd: Path) -> tuple[int, str]:
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=30)
        return p.returncode, (p.stdout + p.stderr).strip()
    except Exception as e:  # noqa: BLE001
        return 1, f"runner error: {e}"


def extract_check_plan(vision: str) -> dict | None:
    """Turn the VISION's Success Signal (prose) into a structured, runnable check plan.
    Uses Claude Code (reliable JSON) with a local-LLM fallback. Returns:
        {"fixtures": {name: content}, "checks": [{command, expect_exit, expect_contains}]}
    or None if nothing usable could be extracted (→ caller falls back to the CLI check)."""
    system = (
        "You convert a software VISION's success criteria into a runnable test plan. "
        "Output ONLY a JSON object — no prose, no code fences — with keys:\n"
        '  "fixtures": object mapping filename -> file content for any input files the '
        "commands need (e.g. a sample text file); {} if none.\n"
        '  "checks": array of {"command": <shell string, run in the app directory>, '
        '"expect_exit": "0" for success or "nonzero" for an expected error/failure, '
        '"expect_contains": [LOOSE substrings the output should contain — labels or obvious '
        "words, NEVER exact computed numbers]}.\n"
        "Derive the commands from the VISION Success Signal. Cover the happy path AND any "
        "error path it describes."
    )
    raw = dispatch_via_claude_code(system, f"VISION:\n{vision}") or call_llm(system, f"VISION:\n{vision}")
    m = re.search(r"\{.*\}", strip_to_code(raw or ""), re.DOTALL)
    if not m:
        return None
    try:
        plan = json.loads(m.group(0))
    except Exception:  # noqa: BLE001
        return None
    # The plan is untrusted LLM output: a truthy `checks` is not necessarily a
    # non-empty list, and `fixtures` may come back as [] for no-fixture apps.
    # Reject the wrong shape (→ caller falls back to the CLI check) rather than
    # crash later on .items()/.get().
    if not isinstance(plan, dict) or not isinstance(plan.get("checks"), list) or not plan["checks"]:
        return None
    if not isinstance(plan.get("fixtures"), dict):
        plan["fixtures"] = {}
    return plan


def validate_from_plan(app_dir: Path, plan: dict) -> tuple[bool, str]:
    """Run a VISION-derived check plan: write fixtures, run each check, assert exit + contains.
    Commands come from Edwin's own VISION in a sandboxed app dir (trusted context)."""
    for name, content in (plan.get("fixtures") or {}).items():
        try:
            dest = app_dir / str(name)
            dest.parent.mkdir(parents=True, exist_ok=True)  # support subdir fixtures (e.g. sample_notes/x.md)
            dest.write_text(content if isinstance(content, str) else str(content), encoding="utf-8")
        except Exception:  # noqa: BLE001
            pass
    log: list[str] = []
    all_ok = True
    for chk in plan.get("checks", []):
        if not isinstance(chk, dict):
            continue
        cmd = (chk.get("command") or "").strip()
        if not cmd:
            continue
        want_nonzero = str(chk.get("expect_exit", "0")).lower() in ("nonzero", "non-zero", "!=0", "1")
        rc, out = run(["bash", "-c", cmd], app_dir)
        exit_ok = (rc != 0) if want_nonzero else (rc == 0)
        # A scalar string is a common LLM slip; without this it iterates
        # character-by-character so "olleh" would pass against "hello".
        raw_contains = chk.get("expect_contains") or []
        if isinstance(raw_contains, str):
            raw_contains = [raw_contains]
        contains = [s for s in raw_contains if isinstance(s, str)]
        missing = [s for s in contains if s.lower() not in out.lower()]
        ok = exit_ok and not missing
        all_ok = all_ok and ok
        want = "nonzero" if want_nonzero else "0"
        extra = "" if not missing else f" (missing {missing})"
        log.append(f"[{'PASS' if ok else 'FAIL'}] `{cmd}` -> exit {rc} (want {want}){extra}\n  {out[:300]}")
    return (all_ok and bool(log)), "\n".join(log)


def validate_cli_fallback(app_dir: Path, entrypoint: str) -> tuple[bool, str]:
    """Fallback when no check plan can be extracted: assume a file-arg CLI.
    real file → exit 0 + numeric output; missing file → non-zero exit."""
    (app_dir / FIXTURE_NAME).write_text(FIXTURE_TEXT, encoding="utf-8")
    log = []
    rc1, out1 = run(["python3", entrypoint, FIXTURE_NAME], app_dir)
    ok1 = rc1 == 0 and any(c.isdigit() for c in out1)
    log.append(f"[{'PASS' if ok1 else 'FAIL'}] `python3 {entrypoint} {FIXTURE_NAME}` -> exit {rc1}\n  {out1[:300]}")
    rc2, out2 = run(["python3", entrypoint, "__does_not_exist__.txt"], app_dir)
    ok2 = rc2 != 0
    log.append(f"[{'PASS' if ok2 else 'FAIL'}] `python3 {entrypoint} __does_not_exist__.txt` -> exit {rc2} (want non-zero)\n  {out2[:300]}")
    return (ok1 and ok2), "\n".join(log)


def validate(app_dir: Path, entrypoint: str, plan: dict | None) -> tuple[bool, str]:
    """Validate against the VISION-derived check plan; fall back to the file-arg CLI check."""
    return validate_from_plan(app_dir, plan) if plan else validate_cli_fallback(app_dir, entrypoint)


# ── Per-phase decomposition (the Architect's ordered plan) ────────────────────

def parse_phases(blueprint: str) -> list[dict]:
    """Parse the BLUEPRINT's `### Phase N — Title` blocks into ordered phase dicts.

    Each phase dict: {number:int, title:str, deliverables:[relative paths],
    command:str|None, pass_condition:str|None}. Deliverables keep their
    File-Tree-relative path (e.g. "sample_notes/alpha.md"); the build creates any
    parent directories as needed. Returns [] if nothing parses."""
    # Split into per-phase blocks: each starts at "### Phase N — Title" and runs
    # until the next "### " heading or any "## " heading (end of the Phases section).
    phases: list[dict] = []
    pat = re.compile(
        r"#{3,}\s*Phase\s+(\d+)\s*[—\-:]\s*([^\n]*)\n(.*?)(?=\n#{2,}\s|\Z)",
        re.DOTALL,
    )
    for m in pat.finditer(blueprint):
        number = int(m.group(1))
        title = m.group(2).strip()
        body = m.group(3)

        # Deliverables: bullets under a "Deliverables:" line, up to the next
        # non-deliverable section bullet (Goal/Worker/Validation/Command/etc.).
        deliverables: list[str] = []
        dm = re.search(
            r"Deliverables\s*:\s*\n(.*?)(?=\n\s*-\s*(?:Goal|Worker|Validation|Command|Pass condition)\b"
            r"|\n\s*Command\s*:|\n\s*Pass condition\s*:|\Z)",
            body, re.DOTALL | re.IGNORECASE,
        )
        if dm:
            for line in dm.group(1).splitlines():
                bm = re.match(r"\s*-\s*(.+?)\s*$", line)
                if not bm:
                    continue
                item = bm.group(1).strip().strip("`").strip()
                # Only treat file-like entries (with an extension) as deliverables.
                fm = re.search(r"([A-Za-z0-9_./\-]+\.[A-Za-z0-9]+)", item)
                if not fm:
                    continue
                rel = fm.group(1)  # keep the File-Tree-relative path (may include subdirs)
                if rel not in deliverables:
                    deliverables.append(rel)

        # Validation command inside backticks after "Command:".
        cm = re.search(r"Command\s*:\s*`([^`]+)`", body, re.IGNORECASE)
        command = cm.group(1).strip() if cm else None

        # Pass condition: the text after "Pass condition:" up to end of that line.
        pm = re.search(r"Pass condition\s*:\s*([^\n]*)", body, re.IGNORECASE)
        pass_condition = pm.group(1).strip() if pm and pm.group(1).strip() else None

        phases.append({
            "number": number,
            "title": title,
            "deliverables": deliverables,
            "command": command,
            "pass_condition": pass_condition,
        })
    return phases


def validate_phase(app_dir: Path, command: str | None, pass_condition: str | None) -> tuple[bool, str]:
    """Validate a single phase by running its validation command. Gate on EXIT CODE.

    A BLUEPRINT's `pass_condition` is a human-readable description of intent
    ("prints a word count") — NOT a literal output substring. Matching it against
    program output produces false negatives, so it is logged for context but never
    used as a gate. A phase that needs output assertions should encode them in the
    command itself (e.g. `... | grep -q 5`). command=None → validated-by-build.

    NOTE: the command runs in the app dir; reference files by their File-Tree-relative
    paths — the build preserves subdirectories."""
    if not command:
        return True, "[PASS] (no command — validated by build)"
    rc, out = run(["bash", "-c", command], app_dir)
    ok = rc == 0
    note = f" — expected: {pass_condition}" if pass_condition else ""
    log = f"[{'PASS' if ok else 'FAIL'}] `{command}` -> exit {rc} (want 0){note}\n  {out[:300]}"
    return ok, log


# ── State + reporting ─────────────────────────────────────────────────────────

def write_state(app_dir: Path, state: dict) -> None:
    state["last_updated"] = now_edt_iso()
    (app_dir / "BUILD_STATE.json").write_text(json.dumps(state, indent=2), encoding="utf-8")


def delivery_report(app_dir: Path, app_name: str, targets: list[str], entrypoint: str,
                    attempts: int, val_log: str, shipped: bool, phase_log: str | None = None) -> None:
    status = "DELIVERED" if shipped else "BLOCKED — escalated to Manager"
    files_md = "\n".join(f"- `{(app_dir / t)}`" for t in targets)
    lines = [
        f"# DELIVERY REPORT — {app_name}",
        "",
        f"**Status:** {status}",
        f"**Built:** {now_edt_display()}",
        f"**Files ({len(targets)}):**",
        files_md,
        f"**Entrypoint:** `{entrypoint}`",
        f"**Worker attempts:** {attempts} (max {MAX_REPAIRS + 1})",
        "",
    ]
    if phase_log:
        lines += [
            "## Phase validation (Architect's ordered plan)",
            "```",
            phase_log,
            "```",
            "",
        ]
    lines += [
        "## Validation (VISION success signal)",
        "```",
        val_log,
        "```",
        "",
        "## How to verify",
        f"```bash\ncd {app_dir}\npython3 {entrypoint} {FIXTURE_NAME}\npython3 {entrypoint} missing.txt   # should error, exit non-zero\n```",
        "",
        "---",
        "*Produced by T.G.A.O.T.U. Build Loop (Stage 3).*",
    ]
    (app_dir / "DELIVERY_REPORT.md").write_text("\n".join(lines), encoding="utf-8")


# ── Main loop ─────────────────────────────────────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(description="T.G.A.O.T.U. Build Loop")
    ap.add_argument("app_dir", help="Path to factory/active/<app>/")
    args = ap.parse_args()

    app_dir = Path(args.app_dir).resolve()
    vision = (app_dir / "VISION.md").read_text(encoding="utf-8")
    blueprint = (app_dir / "BLUEPRINT.md").read_text(encoding="utf-8")
    state = json.loads((app_dir / "BUILD_STATE.json").read_text(encoding="utf-8"))
    app_name = state.get("app_name", app_dir.name)

    targets = detect_target_files(app_name, blueprint)
    entrypoint = detect_entrypoint(vision, targets)
    print(f"[Build Loop] {app_name}: {len(targets)} file(s) {targets}; entrypoint `{entrypoint}`")

    plan = extract_check_plan(vision)
    if plan:
        print(f"[Build Loop] Check plan: {len(plan.get('checks', []))} check(s), "
              f"{len(plan.get('fixtures') or {})} fixture(s) — from the VISION success signal")
    else:
        print("[Build Loop] No check plan extracted — using file-arg CLI fallback.")

    state["overall_status"] = "in_progress"
    write_state(app_dir, state)

    # Choose the path: honor the Architect's ordered phases when they decompose into
    # files; otherwise fall back to the proven single-pass build.
    phases = parse_phases(blueprint)
    sequential = bool(phases) and any(ph["deliverables"] for ph in phases)

    if sequential:
        shipped, attempt, val_log, phase_log = _run_sequential(
            app_dir, app_name, vision, blueprint, state, phases, entrypoint, plan)
        delivery_report(app_dir, app_name, targets, entrypoint, attempt, val_log, shipped, phase_log)
    else:
        shipped, attempt, val_log = _run_single_pass(
            app_dir, vision, blueprint, state, targets, entrypoint, plan)
        delivery_report(app_dir, app_name, targets, entrypoint, attempt, val_log, shipped)

    if shipped:
        print(f"\n[Build Loop] DELIVERED ({len(targets)} file(s)) → {app_dir}")
        print(f"[Build Loop] Report → {app_dir / 'DELIVERY_REPORT.md'}")
        sys.exit(0)
    print(f"\n[Build Loop] BLOCKED after {MAX_REPAIRS} repairs — escalated to Manager. See DELIVERY_REPORT.md")
    sys.exit(2)


def _run_single_pass(app_dir: Path, vision: str, blueprint: str, state: dict,
                     targets: list[str], entrypoint: str,
                     plan: dict | None) -> tuple[bool, int, str]:
    """The original single-pass build: build all targets, validate once against the
    whole VISION, self-repair up to MAX_REPAIRS. Used when the blueprint has no
    parseable phases-with-deliverables."""
    built: dict[str, str] = {}
    error = None
    shipped = False
    val_log = ""
    attempt = 0

    while attempt <= MAX_REPAIRS:
        attempt += 1
        label = "build" if attempt == 1 else f"self-repair {attempt - 1}/{MAX_REPAIRS}"
        print(f"[Build Loop] Attempt {attempt} ({label})")
        for tgt in targets:
            print(f"[Build Loop]   Worker → `{tgt}`")
            siblings = {n: c for n, c in built.items() if n != tgt}
            code = dispatch_worker(vision, blueprint, tgt, siblings, built.get(tgt), error)
            dest = app_dir / tgt
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(code + ("" if code.endswith("\n") else "\n"), encoding="utf-8")
            built[tgt] = code

        ok, val_log = validate(app_dir, entrypoint, plan)
        print(val_log)
        if ok:
            shipped = True
            print(f"[Build Loop] ✅ Validation passed on attempt {attempt}.")
            break
        error = val_log
        print(f"[Build Loop] ✗ Validation failed; {'escalating' if attempt > MAX_REPAIRS else 'repairing'}.")

    for ph in state.get("phases", []):
        ph["status"] = "complete" if shipped else "blocked"
        ph["validated"] = shipped
    state["overall_status"] = "complete" if shipped else "blocked"
    state["files"] = targets
    if not shipped:
        state.setdefault("escalations", []).append({
            "time": now_edt_iso(),
            "reason": f"Validation failed after {MAX_REPAIRS} self-repairs",
            "owner": "Manager (Eva)",
            "status": "open",
        })
    write_state(app_dir, state)
    return shipped, attempt, val_log


def _state_phase_entry(state: dict, number: int) -> dict | None:
    """Find the BUILD_STATE phase entry that corresponds to phase `number`, if any.
    State phases may carry a `number`/`phase`/`id` field or just be positional."""
    entries = state.get("phases")
    if not isinstance(entries, list):
        return None
    for e in entries:
        if isinstance(e, dict):
            for key in ("number", "phase", "id"):
                if str(e.get(key)) == str(number):
                    return e
    # Positional fallback: phase N is the Nth entry (1-indexed).
    idx = number - 1
    if 0 <= idx < len(entries) and isinstance(entries[idx], dict):
        return entries[idx]
    return None


def _run_sequential(app_dir: Path, app_name: str, vision: str, blueprint: str, state: dict,
                    phases: list[dict], entrypoint: str,
                    plan: dict | None) -> tuple[bool, int, str, str]:
    """Honor the Architect's ordered phases: build each phase's deliverables in order,
    validate that phase, gate later phases on it, then run the overall VISION check as a
    final gate. `built` accumulates across phases so later phases see earlier files."""
    ordered = sorted(phases, key=lambda p: p["number"])
    built: dict[str, str] = {}
    phase_logs: list[str] = []
    total_attempts = 0
    blocked_phase: dict | None = None

    for ph in ordered:
        number, title = ph["number"], ph["title"]
        deliverables = ph["deliverables"]
        print(f"[Build Loop] ── Phase {number} — {title}: {deliverables}")

        entry = _state_phase_entry(state, number)
        if entry is not None:
            entry["status"] = "in_progress"
        write_state(app_dir, state)

        error = None
        ok = False
        phase_log = ""
        attempt = 0
        while attempt <= MAX_REPAIRS:
            attempt += 1
            total_attempts += 1
            label = "build" if attempt == 1 else f"self-repair {attempt - 1}/{MAX_REPAIRS}"
            print(f"[Build Loop]   Phase {number} attempt {attempt} ({label})")
            for tgt in deliverables:
                print(f"[Build Loop]     Worker → `{tgt}`")
                siblings = {n: c for n, c in built.items() if n != tgt}
                code = dispatch_worker(vision, blueprint, tgt, siblings, built.get(tgt), error)
                dest = app_dir / tgt
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(code + ("" if code.endswith("\n") else "\n"), encoding="utf-8")
                built[tgt] = code

            ok, phase_log = validate_phase(app_dir, ph["command"], ph["pass_condition"])
            print(phase_log)
            if ok:
                print(f"[Build Loop]   ✅ Phase {number} validated on attempt {attempt}.")
                break
            error = phase_log
            print(f"[Build Loop]   ✗ Phase {number} failed; "
                  f"{'blocking' if attempt > MAX_REPAIRS else 'repairing'}.")

        phase_logs.append(f"Phase {number} — {title}\n{phase_log}")

        if entry is not None:
            entry["status"] = "complete" if ok else "blocked"
            entry["validated"] = ok
        write_state(app_dir, state)

        if not ok:
            blocked_phase = ph
            print(f"[Build Loop] ✗ Phase {number} blocked — halting; later phases skipped.")
            break

    all_phases_ok = blocked_phase is None
    shipped = all_phases_ok
    val_log = ""

    # Final gate: when a VISION-level check plan exists, run it once as an overall
    # end-to-end check after all phases pass. When there is no plan, the per-phase
    # validations ARE the validation — ship on all-phases-complete (do not impose a
    # file-arg CLI fallback, which would misfire on non-CLI multi-phase apps).
    if all_phases_ok and plan:
        print("[Build Loop] All phases passed — running overall VISION check.")
        ok, val_log = validate(app_dir, entrypoint, plan)
        print(val_log)
        shipped = ok
        if not ok:
            print("[Build Loop] ✗ Overall VISION check failed — blocking.")

    # Mark any phase entries that were never reached (later than the blocked one) as blocked.
    if not all_phases_ok and blocked_phase is not None:
        for ph in ordered:
            if ph["number"] > blocked_phase["number"]:
                entry = _state_phase_entry(state, ph["number"])
                if entry is not None:
                    entry["status"] = "blocked"
                    entry["validated"] = False

    state["overall_status"] = "complete" if shipped else "blocked"
    state["files"] = list(built.keys())
    if not shipped:
        if blocked_phase is not None:
            reason = (f"Phase {blocked_phase['number']} — {blocked_phase['title']} "
                      f"failed validation after {MAX_REPAIRS} self-repairs")
        else:
            reason = f"Overall VISION check failed after all phases passed"
        state.setdefault("escalations", []).append({
            "time": now_edt_iso(),
            "reason": reason,
            "owner": "Manager (Eva)",
            "status": "open",
        })
    write_state(app_dir, state)

    phase_log_text = "\n\n".join(phase_logs)
    return shipped, total_attempts, val_log, phase_log_text


if __name__ == "__main__":
    main()
