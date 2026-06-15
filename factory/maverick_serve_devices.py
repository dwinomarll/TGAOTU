#!/usr/bin/env python3
"""Serve Maverick Cockpit on the local network for device testing."""

from __future__ import annotations

import argparse
import http.server
import socket
import socketserver
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_DIR = ROOT / "factory" / "active" / "maverick-cockpit" / "dashboard"
DEFAULT_PORT = 4181


def _lan_ips() -> list[str]:
    ips: set[str] = set()
    try:
        host = socket.gethostname()
        for info in socket.getaddrinfo(host, None, socket.AF_INET, socket.SOCK_STREAM):
            ip = info[4][0]
            if not ip.startswith("127."):
                ips.add(ip)
    except socket.gaierror:
        pass

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            ip = sock.getsockname()[0]
            if not ip.startswith("127."):
                ips.add(ip)
    except OSError:
        pass

    return sorted(ips)


def main() -> int:
    parser = argparse.ArgumentParser(description="Serve Maverick Cockpit to devices on the local network")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args()

    if not DASHBOARD_DIR.exists():
        raise FileNotFoundError(f"dashboard directory is missing: {DASHBOARD_DIR}")

    handler = lambda *handler_args, **kwargs: http.server.SimpleHTTPRequestHandler(  # noqa: E731
        *handler_args,
        directory=str(DASHBOARD_DIR),
        **kwargs,
    )
    with socketserver.TCPServer(("0.0.0.0", args.port), handler) as server:
        print("Maverick Cockpit is available on this Mac and same-Wi-Fi devices:")
        print(f"  http://127.0.0.1:{args.port}/")
        for ip in _lan_ips():
            print(f"  http://{ip}:{args.port}/")
        print("Use the HTTPS public host for always-on access after publish confirmation.")
        server.serve_forever()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
