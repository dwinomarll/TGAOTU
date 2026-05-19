# T.G.A.O.T.U. — Approved Surfaces, Tools, Skills & MCPs

> Agents operating under T.G.A.O.T.U. may ONLY use surfaces listed here.
> New surfaces require Edwin's commission before being added to this list.

---

## Approved Places (destinations + sources)

| Surface | Purpose | Access |
|---|---|---|
| **Notion** | Project management, long-term archival | curl + `NOTION_TOKEN_EVA` from `/etc/eva-notion-bridge/env` |
| **GitHub** (`dwinomarll/TGAOTU`) | Blueprint + code versioning | `mcp__github__*` or `gh` CLI |
| **Hostinger VPS** (`srv1613305`) | eva-gateway, n8n, OpenClaw | `ssh vps` (Tailscale-routed) |
| **Edwin's Mac** (`100.118.38.42`) | Heavy LLM (qwen3:8b via Ollama :11434) | Tailscale only |
| **Jetson local** (`~/eva-workspace/`) | Active monorepo, scripts, services | Direct file access |
| **OpenRouter** | LLM routing (Gemini Flash, Sonnet) | API key in env |
| **Telegram** | Delivery channel to Edwin | eva-gateway bot (srv1613305) |

**NOT approved without commission:** OpenAI direct, ElevenLabs (billing blocked), external storage services, social media APIs.

---

## Approved Tools (CLI + services)

| Tool | Location | Use |
|---|---|---|
| **Warp CLI** | `~/eva-workspace/scripts/warp.py` | Factory cockpit — list/build/dispatch/deploy |
| **n8n** | `srv1613305:32777` | Automation, cron, Notion bridges, webhook triggers |
| **Eva-gateway** | `~/eva-workspace/eva-gateway/` on srv1613305 | Telegram intake + LLM routing |
| **Eva-service FastAPI** | `localhost:8000` | /ask /see /speak /listen /health |
| **Eva Notion Bridge** | `localhost:8091` | Notion read/write helper |
| **Ollama (Jetson)** | `localhost:11434` (CPU-only) | qwen3:1.7b, gemma3:1b, phi4-mini |
| **Ollama (Mac)** | `100.118.38.42:11434` | qwen3:8b (heavy reasoning) |
| **Blender pipeline** | `~/eva-workspace/scripts/blender_*` | 3D render, video generation |
| **Piper TTS** | system | Voice output |
| **git** | system | Version control |

---

## Approved Skills (Claude Code subagents)

| Skill | Trigger | Purpose |
|---|---|---|
| `sherlock` | Before any landscape question or deep search | Read-only synthesis — crawls all surfaces |
| `roaster` | Notion intel + external world scan | Daily context gathering |
| `fire-sherlock-first` | Auto-trigger before >3 file reads | Prevents Eva from self-running blind searches |
| `brainstorming` | Before any creative or architectural work | Intent + design before implementation |
| `dispatching-parallel-agents` | 2+ independent tasks | Parallel execution without shared state |
| `mirror-test` | Before every Eva reply | Veto drift + fabrication patterns |
| `signal-dreaming` | Boot or on demand | Memory consolidation |
| `eva-normal` | Revert Eva voice | Exit character modes |

---

## Approved MCPs (Model Context Protocol servers)

| MCP | Tools Available | Use |
|---|---|---|
| `mcp__engram__*` | `mem_save`, `mem_search`, `mem_context`, `mem_session_summary` | Cross-session memory — PROACTIVE saves |
| `mcp__github__*` | `create_or_update_file`, `push_files`, `get_file_contents` | Git operations without CLI |
| `mcp__plugin_ecc_github__*` | Same as above (ECC plugin variant) | GitHub via ECC plugin layer |
| `mcp__claude_ai_Notion__*` | `notion-fetch`, `notion-create-pages`, `notion-update-page` | Notion read/write |
| `mcp__plugin_ecc_playwright__*` | `browser_navigate`, `browser_snapshot`, `browser_take_screenshot` | Browser automation (visual tasks) |
| `mcp__plugin_ecc_memory__*` | `create_entities`, `search_nodes`, `read_graph` | Knowledge graph (supplemental) |
| `mcp__plugin_telegram_telegram__*` | `reply`, `react`, `edit_message` | Telegram send (delivery channel) |
| `mcp__plugin_fetch_fetch__*` | `fetch_html`, `fetch_json`, `fetch_markdown` | Web content retrieval |
| `mcp__plugin_ecc_exa__*` | `web_search_exa`, `web_fetch_exa` | Deep research + web search |

---

## Approved Models (LLM routing)

| Model | Host | Use Case |
|---|---|---|
| `qwen3:1.7b` | Jetson (default) | Fast edge tasks, short responses |
| `gemma3:1b` | Jetson | Speed-critical tasks |
| `phi4-mini:3.8b` | Jetson | Code tasks, light reasoning |
| `qwen3:8b` | Mac (Tailscale) | Heavy reasoning, long context |
| `claude-sonnet-4-6` | Anthropic (this session) | Architecture, management, complex tasks |
| `gemini-flash` | OpenRouter | Codegen (Blender scripts, integrations) |
| `claude-haiku-4-5` | VPS (eva-gateway) | Fast Telegram responses |

---

## Not Approved (requires commission before use)

- Direct OpenAI API calls (use OpenRouter instead)
- ElevenLabs (billing blocked — env var disable, one re-enable when funded)
- Any new external API without Edwin's explicit go-ahead
- Any service requiring a new credential not already in the vault
