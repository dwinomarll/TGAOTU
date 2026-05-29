#!/usr/bin/env python3
"""Ptah Chatbox — thin CLI client.

Usage: python3 chatbox/client.py "build a CLI that reverses a file"
POSTs the prompt to a running Ptah Chatbox server and prints the JSON result.
"""

import json
import os
import sys
import urllib.request


def main() -> None:
    if len(sys.argv) < 2:
        print('usage: python3 chatbox/client.py "<build request>"', file=sys.stderr)
        sys.exit(2)
    prompt = " ".join(sys.argv[1:])
    host = os.getenv("PTAH_CHATBOX_HOST", "127.0.0.1")
    port = os.getenv("PTAH_CHATBOX_PORT", "8917")
    req = urllib.request.Request(
        f"http://{host}:{port}/chat",
        data=json.dumps({"prompt": prompt}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=1800) as resp:
        result = json.loads(resp.read())
    print(json.dumps(result, indent=2))
    sys.exit(0 if result.get("status") == "delivered" else 1)


if __name__ == "__main__":
    main()
