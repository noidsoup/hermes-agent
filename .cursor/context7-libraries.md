# Context7 library IDs — Hermes Agent

Pre-resolved IDs for stack docs. Use **`resolve-library-id`** if an ID fails or the topic is outside this table (limit ~3 resolve/query rounds per question).

| Stack piece | Library | Context7 library ID | Notes |
| --- | --- | --- | --- |
| Language | Python | `/websites/python_3_12` | Agent core, tools, gateway. |
| Testing | pytest | `/pytest-dev/pytest` | Test suite via scripts/run_tests.sh. |
| CLI UI | Ink (React) | `/vadimdemedes/ink` | TUI in ui-tui/. |

**Credentials:** Context7 MCP requires `CONTEXT7_API_KEY` in Cursor MCP config (`~/.cursor/mcp.json`) or env.
