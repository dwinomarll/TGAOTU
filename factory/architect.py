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
from datetime import datetime, timezone
from pathlib import Path

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

# ── Helpers ───────────────────────────────────────────────────────────────────

def load_architect_prompt() -> str:
    if not PROMPT_FILE.exists():
        sys.exit(f"ERROR: Architect prompt not found at {PROMPT_FILE}")
    return PROMPT_FILE.read_text()


def load_vision(vision_path: Path) -> str:
    if not vision_path.exists():
        sys.exit(f"ERROR: VISION.md not found at {vision_path}")
    content = vision_path.read_text().strip()
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


def call_llm(system_prompt: str, user_message: str) -> str:
    """
    Backend priority:
    1. ANTHROPIC_API_KEY in env → Claude Sonnet (best quality)
    2. Mac Ollama via Tailscale → qwen3:8b (heavy reasoning, approved)
    3. Jetson Ollama → qwen3:1.7b (fast local fallback)
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
            print(f"[Architect] Claude failed ({e}), trying Mac Ollama...")

    # ── 2. Mac Ollama qwen3:8b (Tailscale) ───────────────────────────────────
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
    # Extract phase count from blueprint
    phase_count = blueprint_content.count("### Phase ")
    phases = []
    for i in range(1, phase_count + 1):
        phases.append({
            "number": i,
            "status": "pending" if i > 1 else "ready",
            "validated": False,
            "notes": ""
        })

    state = {
        "app_name": app_name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "current_phase": 1,
        "overall_status": "ready",
        "phases": phases,
        "escalations": [],
        "last_updated": datetime.now(timezone.utc).isoformat()
    }

    state_path = app_dir / "BUILD_STATE.json"
    state_path.write_text(json.dumps(state, indent=2))

    # Also write human-readable BUILD_STATE.md
    md_lines = [
        f"# BUILD STATE — {app_name}",
        "",
        f"## Current Phase: 1",
        f"## Overall Status: ready",
        f"## Created: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "| Phase | Title | Status | Validated | Notes |",
        "|-------|-------|--------|-----------|-------|",
    ]
    for p in phases:
        status_emoji = "⏳" if p["status"] == "pending" else "🟢"
        md_lines.append(
            f"| {p['number']} | (see BLUEPRINT.md) | {status_emoji} {p['status']} | {'✅' if p['validated'] else '—'} | |"
        )
    md_lines += ["", "---", "*Updated by T.G.A.O.T.U. Build Loop*"]

    (app_dir / "BUILD_STATE.md").write_text("\n".join(md_lines))


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
            vision_dest.write_text(vision_content)

    # Write BLUEPRINT.md
    blueprint_path = app_dir / "BLUEPRINT.md"
    blueprint_path.write_text(blueprint)
    print(f"[Architect] BLUEPRINT.md written → {blueprint_path}")

    # Initialize BUILD_STATE
    init_build_state(app_dir, app_name, blueprint)
    print(f"[Architect] BUILD_STATE.md written → {app_dir / 'BUILD_STATE.md'}")

    print(f"\n[Architect] Done. Build Loop can now execute from:")
    print(f"  {app_dir}/")
    print(f"\nNext: python3 factory/build-loop.py {app_dir}")


if __name__ == "__main__":
    main()
