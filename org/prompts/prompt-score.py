#!/usr/bin/env python3
"""Update outcome + effectiveness score for a logged prompt."""

import argparse
import json
from pathlib import Path

LOG = Path(__file__).parent / "prompt-audit.ndjson"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hash", required=True, help="full_prompt_hash value")
    parser.add_argument("--outcome", required=True, choices=["success", "failure", "partial"])
    parser.add_argument("--score", required=True, type=int, choices=[1, 2, 3, 4, 5])
    parser.add_argument("--notes", default="")
    args = parser.parse_args()

    if not LOG.exists():
        print("No prompt audit log found.")
        return

    lines = LOG.read_text().splitlines()
    updated = 0
    new_lines = []
    for line in lines:
        entry = json.loads(line)
        if entry.get("full_prompt_hash") == args.hash:
            entry["outcome"] = args.outcome
            entry["effectiveness_score"] = args.score
            entry["qa_notes"] = args.notes
            updated += 1
        new_lines.append(json.dumps(entry))

    LOG.write_text("\n".join(new_lines) + "\n")
    print(f"Updated {updated} entry/entries with score {args.score} ({args.outcome}).")


if __name__ == "__main__":
    main()
