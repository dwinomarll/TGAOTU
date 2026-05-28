#!/usr/bin/env python3
"""
T.G.A.O.T.U. Build Loop — Stage 3 of the App Factory Protocol (Blueprint III).

Turns a blueprint into a working artifact. Reads
factory/active/<app>/{VISION.md, BLUEPRINT.md, BUILD_STATE.json}, dispatches an
LLM Worker to write the app's single source file, validates against the VISION's
success signal, self-repairs up to 3 times, escalates if it can't, updates
BUILD_STATE, and writes a Delivery Report. No human in the loop.

Worker routing (Blueprint II router): code-extension targets are dispatched to
Claude Code (`--print --permission-mode bypassPermissions`); other tasks use the
local LLM. Scope: single-file builds (one Worker, one file). Multi-file / per-phase
orchestration is future.

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
FIXTURE_TEXT = "hello world\nthe quick brown fox\n"  # 2 lines, 6 words, 31 chars
CODE_EXTS = (".py", ".js", ".ts", ".sh", ".go", ".rb", ".swift", ".rs", ".java")


# ── Worker ──────────────────────────────────────────────────────────────────

def strip_to_code(text: str) -> str:
    """Remove qwen3 <think> blocks and a single wrapping markdown fence, if present."""
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
    fence = re.match(r"^```[A-Za-z0-9_+-]*\n(.*)\n```$", text, flags=re.DOTALL)
    return fence.group(1) if fence else text


def detect_target_file(app_name: str, blueprint: str) -> str:
    """Primary source file: first `name.ext` leaf in the blueprint File Tree, else <app>.py."""
    m = re.search(r"([A-Za-z0-9_\-]+\.(?:py|js|ts|sh|go|rb))\b", blueprint)
    return m.group(1) if m else f"{app_name}.py"


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
            print("[Build Loop] Worker backend: Claude Code (code task)")
            return proc.stdout
        print(f"[Build Loop] Claude Code returned nothing (exit {proc.returncode}); falling back")
    except Exception as exc:  # noqa: BLE001
        print(f"[Build Loop] Claude Code worker error ({exc}); falling back")
    return None


def dispatch_worker(vision: str, blueprint: str, target: str,
                    prior_code: str | None, error_feedback: str | None) -> str:
    system = (
        "You are a Worker in the T.G.A.O.T.U. factory. You own exactly ONE file. "
        "Write the COMPLETE, final, runnable content of that file so it satisfies the "
        "VISION and BLUEPRINT. Standard library only unless the blueprint says otherwise. "
        "Output ONLY the raw file content — no markdown fences, no commentary."
    )
    msg = f"VISION:\n{vision}\n\n---\nBLUEPRINT:\n{blueprint}\n\n---\nThe one file you own: `{target}`\n"
    if prior_code:
        msg += f"\nCurrent content of `{target}`:\n{prior_code}\n"
    if error_feedback:
        msg += (f"\nThe previous version FAILED validation:\n{error_feedback}\n"
                f"Fix the cause and output the FULL corrected `{target}`.")
    # Route by task type (Blueprint II router): code phases → a capable coder
    # (Claude Code), everything else → the local LLM. Repair feedback flows to either.
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


def validate(app_dir: Path, target: str) -> tuple[bool, str]:
    """v1 success-signal check for a file-arg CLI: real file → exit 0 + numeric output;
    missing file → non-zero exit. Sets up the fixture (R4: workplace pre-built)."""
    (app_dir / FIXTURE_NAME).write_text(FIXTURE_TEXT, encoding="utf-8")
    log = []

    rc1, out1 = run(["python3", target, FIXTURE_NAME], app_dir)
    ok1 = rc1 == 0 and any(c.isdigit() for c in out1)
    log.append(f"[{'PASS' if ok1 else 'FAIL'}] `python3 {target} {FIXTURE_NAME}` -> exit {rc1}\n  {out1[:300]}")

    rc2, out2 = run(["python3", target, "__does_not_exist__.txt"], app_dir)
    ok2 = rc2 != 0
    log.append(f"[{'PASS' if ok2 else 'FAIL'}] `python3 {target} __does_not_exist__.txt` -> exit {rc2} (want non-zero)\n  {out2[:300]}")

    return (ok1 and ok2), "\n".join(log)


# ── State + reporting ─────────────────────────────────────────────────────────

def write_state(app_dir: Path, state: dict) -> None:
    state["last_updated"] = now_edt_iso()
    (app_dir / "BUILD_STATE.json").write_text(json.dumps(state, indent=2), encoding="utf-8")


def delivery_report(app_dir: Path, app_name: str, target: str, attempts: int,
                    val_log: str, shipped: bool) -> None:
    status = "DELIVERED" if shipped else "BLOCKED — escalated to Manager"
    lines = [
        f"# DELIVERY REPORT — {app_name}",
        "",
        f"**Status:** {status}",
        f"**Built:** {now_edt_display()}",
        f"**Artifact:** `{(app_dir / target)}`",
        f"**Worker attempts:** {attempts} (max {MAX_REPAIRS + 1})",
        "",
        "## Validation (VISION success signal)",
        "```",
        val_log,
        "```",
        "",
        "## How to verify",
        f"```bash\ncd {app_dir}\npython3 {target} {FIXTURE_NAME}\npython3 {target} missing.txt   # should error, exit non-zero\n```",
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

    target = detect_target_file(app_name, blueprint)
    print(f"[Build Loop] {app_name}: Worker owns `{target}`")

    state["overall_status"] = "in_progress"
    write_state(app_dir, state)

    code = None
    error = None
    shipped = False
    val_log = ""
    attempt = 0

    while attempt <= MAX_REPAIRS:
        attempt += 1
        label = "build" if attempt == 1 else f"self-repair {attempt - 1}/{MAX_REPAIRS}"
        print(f"[Build Loop] Worker dispatch ({label})...")
        code = dispatch_worker(vision, blueprint, target, code, error)
        (app_dir / target).write_text(code + ("\n" if not code.endswith("\n") else ""), encoding="utf-8")

        ok, val_log = validate(app_dir, target)
        print(val_log)
        if ok:
            shipped = True
            print(f"[Build Loop] ✅ Validation passed on attempt {attempt}.")
            break
        error = val_log
        print(f"[Build Loop] ✗ Validation failed; {'escalating' if attempt > MAX_REPAIRS else 'repairing'}.")

    # Update state
    for ph in state.get("phases", []):
        ph["status"] = "complete" if shipped else "blocked"
        ph["validated"] = shipped
    state["overall_status"] = "complete" if shipped else "blocked"
    if not shipped:
        state.setdefault("escalations", []).append({
            "time": now_edt_iso(),
            "reason": f"Validation failed after {MAX_REPAIRS} self-repairs",
            "owner": "Manager (Eva)",
            "status": "open",
        })
    write_state(app_dir, state)
    delivery_report(app_dir, app_name, target, attempt, val_log, shipped)

    if shipped:
        print(f"\n[Build Loop] DELIVERED → {app_dir / target}")
        print(f"[Build Loop] Report → {app_dir / 'DELIVERY_REPORT.md'}")
        sys.exit(0)
    else:
        print(f"\n[Build Loop] BLOCKED after {MAX_REPAIRS} repairs — escalated to Manager. See DELIVERY_REPORT.md")
        sys.exit(2)


if __name__ == "__main__":
    main()
