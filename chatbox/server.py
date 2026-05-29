#!/usr/bin/env python3
"""
Ptah Chatbox — v1 (thin wrapper)

A dependency-free HTTP front-end over the Ptah factory. A prompt comes in, an
OpenRouter model turns it into a VISION.md, and the existing factory (architect
-> sequential build-loop) builds + validates the app. The end result (status,
files, delivery report) comes back as JSON.

Standalone:   python3 chatbox/server.py            # serves on 127.0.0.1:8917
              python3 chatbox/client.py "build a CLI that reverses a file"
Integrated:   MA'AT (or anything) POSTs JSON {"prompt": "..."} to /chat.

OpenRouter is used ONLY for the intake (prompt -> VISION). The factory's own
architect + workers keep using the strong local `claude --print` backend.

Config (env):
  OPENROUTER_API_KEY   required (falls back to ~/.hermes/.env if unset)
  OPENROUTER_MODEL     default google/gemini-2.5-flash
  PTAH_CHATBOX_HOST    default 127.0.0.1
  PTAH_CHATBOX_PORT    default 8917
"""

import json
import os
import re
import subprocess
import sys
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

# ── Paths + config ────────────────────────────────────────────────────────────

REPO_DIR = Path(__file__).resolve().parent.parent
FACTORY_DIR = REPO_DIR / "factory"
ACTIVE_DIR = FACTORY_DIR / "active"
ARCHITECT = FACTORY_DIR / "architect.py"
BUILD_LOOP = FACTORY_DIR / "build-loop.py"

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "google/gemini-2.5-flash"


def _api_key() -> str:
    """OPENROUTER_API_KEY from env, falling back to ~/.hermes/.env. Never logged."""
    key = os.getenv("OPENROUTER_API_KEY", "").strip()
    if key:
        return key
    hermes = Path.home() / ".hermes" / ".env"
    if hermes.exists():
        for line in hermes.read_text(encoding="utf-8").splitlines():
            if line.startswith("OPENROUTER_API_KEY"):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def _model() -> str:
    return os.getenv("OPENROUTER_MODEL", DEFAULT_MODEL)


# ── Prompt -> VISION (the OpenRouter intake) ───────────────────────────────────

_SYSTEM = (
    "You convert a user's build request into a Ptah factory VISION.md — the input "
    "to an autonomous Python app factory. Output ONLY the markdown, no fences, no "
    "commentary. Use EXACTLY these sections:\n"
    "## Name\n<short lower-case app name, words separated by spaces or hyphens>\n\n"
    "## What it does\n<1-3 sentences. Prefer a Python 3 standard-library CLI.>\n\n"
    "## How to run\n<the exact `python3 <file> <args>` command a user would type>\n\n"
    "## Success Signal\n<one concrete, automatable check: a command to run and the "
    "exact text/'exit code' that proves success. Keep it runnable with stdlib only.>"
)


def build_vision_messages(prompt: str) -> list:
    return [
        {"role": "system", "content": _SYSTEM},
        {"role": "user", "content": prompt.strip()},
    ]


def _openrouter_chat(messages: list) -> str:
    """Call OpenRouter (OpenAI-compatible). Returns the assistant message text.
    Isolated so tests can monkeypatch it — no network in unit tests."""
    key = _api_key()
    if not key:
        raise RuntimeError("OPENROUTER_API_KEY not set (env or ~/.hermes/.env)")
    payload = json.dumps({"model": _model(), "messages": messages}).encode("utf-8")
    req = urllib.request.Request(
        OPENROUTER_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/dwinomarll/TGAOTU",
            "X-Title": "Ptah Chatbox",
        },
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read())
    return data["choices"][0]["message"]["content"]


def slugify(name: str) -> str:
    """Strict app-dir name: lower-case, alnum + single hyphens only. Prevents a
    hostile prompt from steering the app name into a path traversal."""
    s = re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-")
    return s or "app"


def extract_app_name(vision_md: str, fallback: str = "app") -> str:
    m = re.search(r"^##\s*Name\s*\n+([^\n]+)", vision_md, re.MULTILINE | re.IGNORECASE)
    return slugify(m.group(1)) if m and m.group(1).strip() else slugify(fallback)


def derive_vision(prompt: str) -> tuple[str, str]:
    """prompt -> (app_slug, vision_md) via OpenRouter."""
    raw = _openrouter_chat(build_vision_messages(prompt))
    vision_md = raw.strip()
    # strip an accidental wrapping markdown fence
    fence = re.match(r"^```[a-zA-Z]*\n(.*)\n```$", vision_md, re.DOTALL)
    if fence:
        vision_md = fence.group(1).strip()
    return extract_app_name(vision_md, fallback="app"), vision_md


# ── Run the factory ────────────────────────────────────────────────────────────

def run_factory(app_dir: Path) -> dict:
    """architect (VISION -> BLUEPRINT) then build-loop (sequential build). Returns
    {status, files, delivery_report}. Assumes app_dir/VISION.md already written."""
    arch = subprocess.run(
        [sys.executable, str(ARCHITECT), str(app_dir / "VISION.md")],
        capture_output=True, text=True, timeout=600,
    )
    if arch.returncode != 0:
        return {"status": "architect_failed", "files": [],
                "delivery_report": (arch.stdout + arch.stderr)[-2000:]}
    build = subprocess.run(
        [sys.executable, str(BUILD_LOOP), str(app_dir)],
        capture_output=True, text=True, timeout=1800,
    )
    report_path = app_dir / "DELIVERY_REPORT.md"
    report = report_path.read_text(encoding="utf-8") if report_path.exists() else ""
    state_path = app_dir / "BUILD_STATE.json"
    files = []
    if state_path.exists():
        try:
            files = json.loads(state_path.read_text(encoding="utf-8")).get("files", [])
        except Exception:  # noqa: BLE001
            pass
    status = "delivered" if build.returncode == 0 else "blocked"
    return {"status": status, "files": files, "delivery_report": report}


def handle_chat(prompt: str) -> dict:
    """The full v1 loop: prompt -> VISION -> factory -> result."""
    if not prompt or not prompt.strip():
        return {"error": "empty prompt"}
    slug, vision_md = derive_vision(prompt)
    app_dir = ACTIVE_DIR / slug
    app_dir.mkdir(parents=True, exist_ok=True)
    (app_dir / "VISION.md").write_text(vision_md + "\n", encoding="utf-8")
    result = run_factory(app_dir)
    result["app"] = slug
    result["app_dir"] = str(app_dir)
    return result


# ── HTTP ────────────────────────────────────────────────────────────────────────

class ChatHandler(BaseHTTPRequestHandler):
    def _json(self, code: int, obj: dict) -> None:
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):  # noqa: N802
        if self.path in ("/", "/health"):
            self._json(200, {"service": "Ptah Chatbox", "ok": True,
                             "usage": 'POST /chat {"prompt": "..."}'})
        else:
            self._json(404, {"error": "not found"})

    def do_POST(self):  # noqa: N802
        if self.path != "/chat":
            self._json(404, {"error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length) or b"{}")
            prompt = body.get("prompt", "")
        except Exception as e:  # noqa: BLE001
            self._json(400, {"error": f"bad request: {e}"})
            return
        try:
            self._json(200, handle_chat(prompt))
        except Exception as e:  # noqa: BLE001
            self._json(500, {"error": str(e)})

    def log_message(self, fmt, *args):  # quieter logging
        sys.stderr.write("[Ptah Chatbox] " + (fmt % args) + "\n")


def serve() -> None:
    host = os.getenv("PTAH_CHATBOX_HOST", "127.0.0.1")
    port = int(os.getenv("PTAH_CHATBOX_PORT", "8917"))
    httpd = ThreadingHTTPServer((host, port), ChatHandler)
    print(f"[Ptah Chatbox] listening on http://{host}:{port}  (model: {_model()})")
    print('[Ptah Chatbox] POST /chat {"prompt": "..."}')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.shutdown()


if __name__ == "__main__":
    serve()
