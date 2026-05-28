# SimpleMem — hermes-agent

Local persistent memory for this repo. **Committed** so clones share context.

- **Namespace:** `hermes-agent`
- **Store:** `memories.json` in this directory
- **CLI:** `python3 simplemem_cli.py add|query|import-ai-session`
- **Maintenance:** `python3 scripts/maintain_project_knowledge.py`

Enable in `.env` (see `.env.example` SimpleMem section). Default backend is **local**; set `SIMPLEMEM_TOKEN` for cloud MCP.

Do not store secrets, tokens, or PII.
