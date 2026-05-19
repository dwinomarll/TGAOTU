# Prompt Audit Log — Guide

> Every directive sent from one agent to another is logged here.
> QA-1 reviews and scores. EFF-1 monitors for waste. Eva improves.

---

## Log File

`org/prompts/prompt-audit.ndjson` — one JSON object per line.

Each entry:
```json
{
  "ts": "2026-05-19T19:00:00Z",
  "sender": "Eva (COO)",
  "receiver": "ENG-iOS",
  "purpose": "my-app / Phase 2 — Data Models",
  "prompt_length": 847,
  "prompt_preview": "You are ENG-iOS. You have one assignment...",
  "full_prompt_hash": "1234567890",
  "outcome": "success | failure | partial",
  "effectiveness_score": 4,
  "qa_notes": "Agent produced all deliverables. Prompt was clear. Minor: validation command needed escaping."
}
```

## Effectiveness Scale (QA-1 grades every prompt)

| Score | Meaning |
|-------|---------|
| 5 | Agent produced all deliverables exactly as specified. No drift. |
| 4 | Agent produced all deliverables. Minor formatting or style variation. |
| 3 | Agent produced most deliverables. One missed or partially done. |
| 2 | Agent drifted significantly. Missing deliverables or scope creep. |
| 1 | Agent failed entirely or produced wrong output. Prompt needs rewrite. |

## How QA-1 Updates Scores

After each phase QA report, QA-1 appends outcome + score to the matching prompt entry:
```bash
python3 org/prompts/prompt-score.py \
  --hash <prompt_hash> \
  --outcome success \
  --score 4 \
  --notes "Clean output. Prompt was clear."
```

## How Eva Uses This Log

- Prompts scoring ≤ 2 three times → rewrite the directive template
- Prompts scoring 5 consistently → promote to `org/prompts/templates/` as canonical
- EFF-1 reports on average score per agent per week
- Over time: canonical templates replace generated prompts → fewer tokens per directive

## Viewing the Log

```bash
# Recent 10 prompts
tail -10 org/prompts/prompt-audit.ndjson | python3 -m json.tool

# Prompts by agent
grep '"receiver": "ENG-iOS"' org/prompts/prompt-audit.ndjson | wc -l

# Low-scoring prompts
python3 -c "
import json
for line in open('org/prompts/prompt-audit.ndjson'):
    e = json.loads(line)
    if e.get('effectiveness_score', 5) <= 2:
        print(e['ts'], e['receiver'], e['purpose'], e.get('qa_notes',''))
"
```
