# Where Claude Desktop keeps its files

| What | macOS | Windows |
|------|-------|---------|
| MCP server list | `~/Library/Application Support/Claude/claude_desktop_config.json` | `%APPDATA%\Claude\claude_desktop_config.json` |
| Third-party inference settings | Written by the app (OS-managed preferences) | Written by the app (OS-managed preferences) |
| Claude Code CLI env | `ANTHROPIC_BASE_URL` / `ANTHROPIC_API_KEY` in the shell profile | same, via the shell profile |

`claude_desktop_config.json` holds MCP servers only. The custom API base url for Claude Desktop is set in Developer Mode, not in this file.
