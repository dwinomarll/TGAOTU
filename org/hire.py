#!/usr/bin/env python3
"""
Ptah — Hire a New Agent
Generates agent contract from TEMPLATE.md, adds to ROSTER.md.
No human steps. Pure agentic onboarding.

Usage:
    python3 org/hire.py --role "Database Engineer" --team Engineering \
      --input "BLUEPRINT.md phase spec" --output "SQL migration files" \
      --tools "psql,python3,git"
"""

import argparse
import re
import sys
from datetime import date
from pathlib import Path

ORG_DIR = Path(__file__).parent
TEMPLATE = ORG_DIR / "onboarding" / "TEMPLATE.md"
AGENTS_DIR = ORG_DIR / "agents"
ROSTER = ORG_DIR / "ROSTER.md"

TEAMS = ["Product", "Design", "Architecture", "Engineering", "QA", "DevOps", "Supervisor"]
TEAM_PREFIX = {
    "Product": "PM", "Design": "DESIGN", "Architecture": "ARCH",
    "Engineering": "ENG", "QA": "QA", "DevOps": "DEVOPS", "Supervisor": "SUP"
}


def next_agent_id(team: str) -> str:
    prefix = TEAM_PREFIX.get(team, team[:3].upper())
    existing = list(AGENTS_DIR.glob(f"{prefix.lower()}-*.md"))
    numbers = []
    for f in existing:
        m = re.search(r"-(\d+)\.md$", f.name)
        if m:
            numbers.append(int(m.group(1)))
    n = max(numbers) + 1 if numbers else 1
    return f"{prefix}-{n}"


def generate_contract(agent_id: str, role: str, team: str,
                      input_doc: str, output_doc: str, tools: list[str]) -> str:
    today = date.today().isoformat()
    tool_rows = "\n".join(f"| {t.strip()} | |" for t in tools)

    return f"""# Agent Contract — {agent_id}

## Identity
- **Agent ID:** {agent_id}
- **Name:** {role}
- **Team:** {team}
- **Role:** (fill in — one sentence describing what this agent does)
- **Hired by:** Eva (COO)
- **Hired on:** {today}

## Responsibilities
- **Primary function:** (fill in — what this agent produces)
- **Input document:** {input_doc}
- **Output document:** {output_doc}
- **Done means:** (fill in — exact verifiable definition of done)

## Tools & Access
| Tool | Purpose |
|------|---------|
{tool_rows}

## Operating Instructions

### You are the {role}

(Fill in: 2-3 sentences describing the agent's mindset and domain.)

### Decision Rules (make these without asking)
1. (fill in)
2. (fill in)
3. (fill in)

### Output Format

```
(Fill in exact output format)
```

### Quality Gate
- [ ] (fill in check 1)
- [ ] (fill in check 2)
- [ ] (fill in check 3)

## Escalation Path
| Condition | Escalate To |
|-----------|------------|
| Input document is missing or malformed | Eva (COO) |
| Required tool is unavailable | Eva (COO) |
| Output fails quality gate 3 times | SUP-1 (Tech Lead) |
| Decision changes the vision scope | Eva → Edwin |
"""


def add_to_roster(agent_id: str, role: str, team: str,
                  input_doc: str, output_doc: str) -> None:
    if not ROSTER.exists():
        return

    content = ROSTER.read_text()
    # Find the right team section and append row
    section_header = f"## {team} Team"
    if section_header not in content and team not in ["Supervisor"]:
        section_header = f"## {team}"

    new_row = f"| **{agent_id}** | {role} | {input_doc} | {output_doc} | 🟡 Onboarding | `org/agents/{agent_id.lower()}.md` |"

    if section_header in content:
        # Insert before the next ## section
        lines = content.splitlines()
        insert_after = -1
        in_section = False
        for i, line in enumerate(lines):
            if line.startswith(section_header):
                in_section = True
            elif in_section and line.startswith("## "):
                insert_after = i - 1
                break
        if insert_after > 0:
            lines.insert(insert_after, new_row)
            ROSTER.write_text("\n".join(lines))
            return

    # Append at end if section not found
    with open(ROSTER, "a") as f:
        f.write(f"\n\n## {team} Team (new)\n\n| Agent | Role | Input | Output | Status | Contract |\n|-------|------|-------|--------|--------|----------|\n{new_row}\n")


def main():
    parser = argparse.ArgumentParser(description="Hire a new Ptah agent")
    parser.add_argument("--role", required=True, help="Agent role title")
    parser.add_argument("--team", required=True, choices=TEAMS, help="Team to assign")
    parser.add_argument("--input", required=True, dest="input_doc", help="Input document")
    parser.add_argument("--output", required=True, dest="output_doc", help="Output document")
    parser.add_argument("--tools", default="", help="Comma-separated tools from ALLOWLIST")
    args = parser.parse_args()

    agent_id = next_agent_id(args.team)
    tools = [t.strip() for t in args.tools.split(",") if t.strip()]

    contract = generate_contract(
        agent_id, args.role, args.team,
        args.input_doc, args.output_doc, tools
    )

    contract_path = AGENTS_DIR / f"{agent_id.lower()}.md"
    contract_path.write_text(contract)
    print(f"[Hire] Contract written → {contract_path}")

    add_to_roster(agent_id, args.role, args.team, args.input_doc, args.output_doc)
    print(f"[Hire] Added to ROSTER.md — status: 🟡 Onboarding")
    print(f"\n[Hire] Agent {agent_id} is ready for onboarding.")
    print(f"       Fill in the operating instructions in: {contract_path}")
    print(f"       Then update status in ROSTER.md to 🟢 Active")


if __name__ == "__main__":
    main()
