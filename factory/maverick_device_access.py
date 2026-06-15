#!/usr/bin/env python3
"""Build Maverick's device access contract.

The cockpit must be usable from every user device. Localhost is acceptable for
development checks only; the durable path is an HTTPS static deployment backed
by the repo package.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "factory" / "active" / "maverick-cockpit"
DEVICE_ACCESS_PATH = APP_DIR / "device-access.json"
DASHBOARD_DEVICE_ACCESS_PATH = APP_DIR / "dashboard" / "data" / "maverick-device-access.json"
DEVICE_ACCESS_OBSERVED_AT = "2026-06-14T20:20:00-04:00"
LAN_PORT = 4181


def build_device_access(observed_at: str = DEVICE_ACCESS_OBSERVED_AT) -> dict[str, Any]:
    return {
        "generated_at": observed_at,
        "name": "maverick-device-access",
        "version": 1,
        "hard_rule": "Maverick must work from every Edwin device through a stable device-safe URL; localhost is never the user-facing answer.",
        "primary_access": {
            "mode": "always_on_static_https",
            "status": "pending_public_publish_target",
            "required": True,
            "reason": "iPhone, iPad, Mac, and remote devices cannot depend on a Mac-only localhost session.",
            "acceptable_hosts": [
                "Netlify static site",
                "Cloudflare Pages static site",
                "GitHub Pages or equivalent HTTPS static host",
            ],
            "publish_gate": "github_publish",
        },
        "fallback_access": {
            "mode": "same_wifi_lan",
            "status": "available_when_mac_is_awake",
            "required_server_bind": "0.0.0.0",
            "port": LAN_PORT,
            "url_template": f"http://<mac-lan-ip>:{LAN_PORT}/",
            "start_command": f"python3 factory/maverick_serve_devices.py --port {LAN_PORT}",
            "limits": [
                "Mac must be awake and on the same network.",
                "iPhone must be on the same Wi-Fi or reachable VPN.",
                "This is not the always-on production answer.",
            ],
        },
        "installable_app": {
            "status": "ready_for_https_hosts",
            "manifest": "factory/active/maverick-cockpit/dashboard/manifest.webmanifest",
            "service_worker": "factory/active/maverick-cockpit/dashboard/service-worker.js",
            "offline_cache": [
                "./",
                "./index.html",
                "./styles.css",
                "./app.js",
                "./data/maverick-dashboard-data.json",
                "./data/maverick-device-access.json",
            ],
            "notes": "Service workers require HTTPS or localhost. They activate after Maverick is on the public HTTPS host.",
        },
        "blocked_patterns": [
            "Do not give 127.0.0.1 as the final user device URL.",
            "Do not depend on a single Codex browser tab for user-facing access.",
            "Do not call a LAN URL always-on unless the Mac is managed to stay awake.",
        ],
        "acceptance_checks": [
            "Dashboard renders on mobile width without horizontal layout failure.",
            "A stable HTTPS URL is recorded once the public host is confirmed.",
            "PWA manifest and service worker are shipped with the cockpit package.",
            "LAN fallback command is available for same-Wi-Fi testing.",
        ],
    }


def write_device_access(access: dict[str, Any]) -> None:
    DEVICE_ACCESS_PATH.write_text(json.dumps(access, indent=2), encoding="utf-8")
    DASHBOARD_DEVICE_ACCESS_PATH.parent.mkdir(parents=True, exist_ok=True)
    DASHBOARD_DEVICE_ACCESS_PATH.write_text(json.dumps(access, indent=2), encoding="utf-8")


def main() -> int:
    access = build_device_access()
    write_device_access(access)
    print(json.dumps({
        "device_access": str(DEVICE_ACCESS_PATH.relative_to(ROOT)),
        "dashboard_device_access": str(DASHBOARD_DEVICE_ACCESS_PATH.relative_to(ROOT)),
        "primary_status": access["primary_access"]["status"],
        "fallback_url_template": access["fallback_access"]["url_template"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
