#!/usr/bin/env python3
"""
T.G.A.O.T.U. Architect Agent
Reads VISION.md → produces BLUEPRINT.md + BUILD_STATE.md
No human in the loop.

Usage:
    python3 factory/architect.py factory/active/<app-name>/VISION.md
    python3 factory/architect.py --vision "Build an iOS notes app" --name my-app
"""

import argparse
import os
import sys
import json
import re
import shutil
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
try:
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
except ImportError:  # pragma: no cover - Python < 3.9 fallback
    ZoneInfo = None
    ZoneInfoNotFoundError = Exception

# ── Config ────────────────────────────────────────────────────────────────────

FACTORY_DIR = Path(__file__).parent
TGAOTU_DIR = FACTORY_DIR.parent
PROMPT_FILE = FACTORY_DIR / "architect-prompt.md"
ACTIVE_DIR = FACTORY_DIR / "active"
MODEL_CLAUDE = "claude-sonnet-4-6"
MODEL_OLLAMA = "qwen3:8b"
MAC_OLLAMA = "http://100.118.38.42:11434"  # Mac via Tailscale — heavy reasoning
JETSON_OLLAMA = "http://localhost:11434"    # Jetson fallback — smaller model
MAX_TOKENS = 8192
try:
    EDT = ZoneInfo("America/New_York") if ZoneInfo else timezone(timedelta(hours=-4), "EDT")
except ZoneInfoNotFoundError:
    EDT = timezone(timedelta(hours=-4), "EDT")

# ── Helpers ───────────────────────────────────────────────────────────────────

def load_architect_prompt() -> str:
    if not PROMPT_FILE.exists():
        sys.exit(f"ERROR: Architect prompt not found at {PROMPT_FILE}")
    return PROMPT_FILE.read_text(encoding="utf-8")


def load_vision(vision_path: Path) -> str:
    if not vision_path.exists():
        sys.exit(f"ERROR: VISION.md not found at {vision_path}")
    content = vision_path.read_text(encoding="utf-8").strip()
    if "[App Name Here]" in content or content.count("\n") < 5:
        sys.exit("ERROR: VISION.md appears to be unfilled template. Complete it first.")
    return content


def extract_app_name(vision_content: str, fallback: str) -> str:
    for line in vision_content.splitlines():
        if line.strip().startswith("## Name"):
            # Next non-empty line after "## Name"
            continue
        if line.strip() and not line.startswith("#") and not line.startswith("["):
            # Check if previous line was ## Name
            lines = vision_content.splitlines()
            for i, l in enumerate(lines):
                if "## Name" in l and i + 1 < len(lines):
                    candidate = lines[i + 1].strip()
                    if candidate and not candidate.startswith("["):
                        return candidate.lower().replace(" ", "-")
    return fallback


def now_edt_iso() -> str:
    return datetime.now(EDT).isoformat()


def now_edt_display() -> str:
    return datetime.now(EDT).strftime("%Y-%m-%d %H:%M EDT")


def extract_phase_specs(blueprint_content: str) -> list[dict]:
    """Extract phase title, worker, and validation command from BLUEPRINT.md."""
    headers = list(re.finditer(r"^### Phase (\d+)\s+\S+\s*(.+)$", blueprint_content, re.MULTILINE))
    phases = []

    for index, header in enumerate(headers):
        number = int(header.group(1))
        title = header.group(2).strip()
        start = header.end()
        end = headers[index + 1].start() if index + 1 < len(headers) else len(blueprint_content)
        block = blueprint_content[start:end]

        worker_match = re.search(r"^- Worker:\s*(.+)$", block, re.MULTILINE)
        command_match = re.search(r"Command:\s*`(.+?)`", block)

        phases.append({
            "number": number,
            "title": title,
            "worker": worker_match.group(1).strip() if worker_match else "(see BLUEPRINT.md)",
            "validation_command": command_match.group(1).strip() if command_match else "echo validate manually"
        })

    return phases


def call_llm(system_prompt: str, user_message: str) -> str:
    """
    Backend priority:
    1. ANTHROPIC_API_KEY in env → Claude Sonnet (best quality)
    2. Claude Code CLI (`claude --print`) → strong local backend, no API key needed
    3. Mac Ollama via Tailscale → qwen3:8b (heavy reasoning, approved)
    4. Jetson Ollama → qwen3:1.7b (fast local fallback)
    """
    import urllib.request

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")

    # ── 1. Claude (Anthropic) ─────────────────────────────────────────────────
    if api_key:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            response = client.messages.create(
                model=MODEL_CLAUDE,
                max_tokens=MAX_TOKENS,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}]
            )
            print(f"[Architect] Backend: Claude {MODEL_CLAUDE}")
            return response.content[0].text
        except Exception as e:
            print(f"[Architect] Claude failed ({e}), trying Claude Code CLI...")

    # ── 2. Claude Code CLI (claude --print) ───────────────────────────────────
    # The same strong local backend the build Worker uses; no API key required —
    # far better blueprint fidelity than the local Ollama models.
    if shutil.which("claude"):
        prompt = (f"{system_prompt}\n\n{user_message}\n\n"
                  "Do NOT use any tools or write files. Respond with ONLY the requested content.")
        try:
            # Text-only generation: deny all side-effect tools and use the default
            # (gated) permission mode rather than bypassing permissions. A VISION can
            # carry a prompt injection, and this subprocess must never run tools.
            proc = subprocess.run(
                ["claude", "--print",
                 "--disallowedTools", "Bash,Edit,Write,Read,NotebookEdit,WebFetch,WebSearch",
                 "--permission-mode", "default", prompt],
                capture_output=True, text=True, timeout=300,
            )
            if proc.returncode == 0 and proc.stdout.strip():
                print("[Architect] Backend: Claude Code (claude --print)")
                return proc.stdout
            print(f"[Architect] Claude Code returned nothing (exit {proc.returncode}), trying Mac Ollama...")
        except Exception as e:
            print(f"[Architect] Claude Code error ({e}), trying Mac Ollama...")

    # ── 3. Mac Ollama qwen3:8b (Tailscale) ───────────────────────────────────
    combined = f"{system_prompt}\n\n---\n\n{user_message}"
    payload = json.dumps({
        "model": MODEL_OLLAMA,
        "prompt": combined,
        "stream": False,
        "options": {"num_predict": MAX_TOKENS, "temperature": 0.2}
    }).encode()

    for host, label in [(MAC_OLLAMA, "Mac qwen3:8b"), (JETSON_OLLAMA, "Jetson Ollama")]:
        try:
            req = urllib.request.Request(
                f"{host}/api/generate",
                data=payload,
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=180) as resp:
                result = json.loads(resp.read())
                print(f"[Architect] Backend: {label}")
                return result["response"]
        except Exception as e:
            print(f"[Architect] {label} failed ({e}), trying next...")

    sys.exit("ERROR: All LLM backends failed. Check Tailscale + Ollama status.")


def init_build_state(app_dir: Path, app_name: str, blueprint_content: str) -> None:
    phase_specs = extract_phase_specs(blueprint_content)
    if not phase_specs:
        phase_specs = [
            {
                "number": i,
                "title": "(see BLUEPRINT.md)",
                "worker": "(see BLUEPRINT.md)",
                "validation_command": "echo validate manually"
            }
            for i in range(1, blueprint_content.count("### Phase ") + 1)
        ]

    phases = []
    for phase in phase_specs:
        phases.append({
            "number": phase["number"],
            "title": phase["title"],
            "worker": phase["worker"],
            "status": "pending" if phase["number"] > 1 else "ready",
            "validated": False,
            "validation_command": phase["validation_command"],
            "notes": ""
        })

    state = {
        "app_name": app_name,
        "created_at": now_edt_iso(),
        "last_updated": now_edt_iso(),
        "current_phase": 1,
        "overall_status": "ready",
        "phases": phases,
        "escalations": []
    }

    state_path = app_dir / "BUILD_STATE.json"
    state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")

    # Also write human-readable BUILD_STATE.md
    md_lines = [
        f"# BUILD STATE — {app_name}",
        "",
        f"## Current Phase: 1",
        f"## Overall Status: ready",
        f"## Created: {now_edt_display()}",
        f"## Last Updated: {now_edt_display()}",
        "",
        "| Phase | Title | Worker | Status | Validated | Validation | Notes |",
        "|-------|-------|--------|--------|-----------|------------|-------|",
    ]
    for p in phases:
        status_emoji = "⏳" if p["status"] == "pending" else "🟢"
        md_lines.append(
            f"| {p['number']} | {p['title']} | {p['worker']} | {status_emoji} {p['status']} | {'yes' if p['validated'] else 'no'} | `{p['validation_command']}` | |"
        )
    md_lines += [
        "",
        "## Escalations",
        "",
        "| Time | Phase | Reason | Owner | Status | Resolution |",
        "|---|---:|---|---|---|---|",
        "",
        "---",
        "*Updated by T.G.A.O.T.U. Build Loop*"
    ]

    (app_dir / "BUILD_STATE.md").write_text("\n".join(md_lines), encoding="utf-8")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="T.G.A.O.T.U. Architect Agent")
    parser.add_argument("vision_file", nargs="?", help="Path to VISION.md")
    parser.add_argument("--vision", help="Raw vision text (alternative to file)")
    parser.add_argument("--name", help="App name (used as directory name)")
    parser.add_argument("--dry-run", action="store_true", help="Print blueprint to stdout, don't write files")
    args = parser.parse_args()

    # Load inputs
    if args.vision_file:
        vision_path = Path(args.vision_file)
        vision_content = load_vision(vision_path)
        app_name = args.name or extract_app_name(vision_content, vision_path.parent.name)
    elif args.vision:
        vision_content = args.vision
        app_name = args.name or "unnamed-app"
    else:
        parser.print_help()
        sys.exit(1)

    app_dir = ACTIVE_DIR / app_name
    architect_prompt = load_architect_prompt()

    print(f"[Architect] Reading vision for: {app_name}")

    user_message = f"""Here is the VISION.md for the app you need to blueprint:

---
{vision_content}
---

Produce a complete BLUEPRINT.md following the format in your instructions.
Make all decisions. Do not ask questions. Output only the BLUEPRINT.md content."""

    blueprint = call_llm(architect_prompt, user_message)

    if args.dry_run:
        print("\n" + "="*60)
        print("BLUEPRINT.md (dry run — not written)")
        print("="*60)
        print(blueprint)
        return

    # Write output files
    app_dir.mkdir(parents=True, exist_ok=True)

    # Copy VISION.md if it came from a file
    if args.vision_file:
        vision_dest = app_dir / "VISION.md"
        if not vision_dest.exists():
            vision_dest.write_text(vision_content, encoding="utf-8")

    # Write BLUEPRINT.md
    blueprint_path = app_dir / "BLUEPRINT.md"
    blueprint_path.write_text(blueprint, encoding="utf-8")
    print(f"[Architect] BLUEPRINT.md written → {blueprint_path}")

    # Initialize BUILD_STATE
    init_build_state(app_dir, app_name, blueprint)
    print(f"[Architect] BUILD_STATE.md written → {app_dir / 'BUILD_STATE.md'}")

    print(f"\n[Architect] Done. Build Loop can now execute from:")
    print(f"  {app_dir}/")
    print(f"\nNext: python3 factory/build-loop.py {app_dir}")


if __name__ == "__main__":
    main()
