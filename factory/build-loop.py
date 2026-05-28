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
    """All source files from the blueprint's File Tree (leaf names, flat, order-preserved).
    Falls back to a single <app>.py if no File Tree is found."""
    # Grab the "File Tree"/"File Structure" section up to the next heading — robust to
    # whether the LLM fenced it or wrote it as plain text.
    m = re.search(r"#+\s*File (?:Tree|Structure)\b[^\n]*\n(.*?)(?:\n#+\s|\Z)",
                  blueprint, re.DOTALL | re.IGNORECASE)
    block = m.group(1) if m else ""
    files: list[str] = []
    for fm in re.finditer(r"([A-Za-z0-9_./\-]+\.(?:py|js|ts|sh|go|rb|swift|rs|java))", block):
        leaf = fm.group(1).split("/")[-1]
        if leaf not in files:
            files.append(leaf)
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


def validate(app_dir: Path, entrypoint: str) -> tuple[bool, str]:
    """Success-signal check for a file-arg CLI: real file → exit 0 + numeric output;
    missing file → non-zero exit. Sets up the fixture (R4: workplace pre-built)."""
    (app_dir / FIXTURE_NAME).write_text(FIXTURE_TEXT, encoding="utf-8")
    log = []

    rc1, out1 = run(["python3", entrypoint, FIXTURE_NAME], app_dir)
    ok1 = rc1 == 0 and any(c.isdigit() for c in out1)
    log.append(f"[{'PASS' if ok1 else 'FAIL'}] `python3 {entrypoint} {FIXTURE_NAME}` -> exit {rc1}\n  {out1[:300]}")

    rc2, out2 = run(["python3", entrypoint, "__does_not_exist__.txt"], app_dir)
    ok2 = rc2 != 0
    log.append(f"[{'PASS' if ok2 else 'FAIL'}] `python3 {entrypoint} __does_not_exist__.txt` -> exit {rc2} (want non-zero)\n  {out2[:300]}")

    return (ok1 and ok2), "\n".join(log)


# ── State + reporting ─────────────────────────────────────────────────────────

def write_state(app_dir: Path, state: dict) -> None:
    state["last_updated"] = now_edt_iso()
    (app_dir / "BUILD_STATE.json").write_text(json.dumps(state, indent=2), encoding="utf-8")


def delivery_report(app_dir: Path, app_name: str, targets: list[str], entrypoint: str,
                    attempts: int, val_log: str, shipped: bool) -> None:
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

    state["overall_status"] = "in_progress"
    write_state(app_dir, state)

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
            (app_dir / tgt).write_text(code + ("" if code.endswith("\n") else "\n"), encoding="utf-8")
            built[tgt] = code

        ok, val_log = validate(app_dir, entrypoint)
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
    delivery_report(app_dir, app_name, targets, entrypoint, attempt, val_log, shipped)

    if shipped:
        print(f"\n[Build Loop] DELIVERED ({len(targets)} file(s)) → {app_dir}")
        print(f"[Build Loop] Report → {app_dir / 'DELIVERY_REPORT.md'}")
        sys.exit(0)
    print(f"\n[Build Loop] BLOCKED after {MAX_REPAIRS} repairs — escalated to Manager. See DELIVERY_REPORT.md")
    sys.exit(2)


if __name__ == "__main__":
    main()
