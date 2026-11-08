# codex-cli — Codex CLI config.toml and endpoint setup

The Codex CLI reads its settings from `~/.codex/config.toml` and its credentials from somewhere else. This recipe is the short version of both, plus the two region errors people hit on a first run.

## Install

Pick one:

```bash
npm install -g @openai/codex     # macOS / Linux / Windows, Node 18+
winget install OpenAI.Codex     # Windows
brew install openai/tap/codex    # macOS
```

Then check the build:

```bash
codex --version
```

## Where the settings live

| What | Where |
|------|-------|
| Model, provider, base URL, approval policy, MCP servers | `~/.codex/config.toml` (generated on first run) |
| Credentials | `~/.codex/auth.json`, or the environment |

`config.toml` and `auth.json` are separate on purpose: settings in one, secrets in the other.

## `config.toml`

```toml
# ~/.codex/config.toml
model = "gpt-5.4"

[model_providers.codegateway]
name = "CodeGateway"
base_url = "https://api.codegateway.dev/v1"
env_key = "OPENAI_API_KEY"

[mcp_servers.example]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-brave-search"]
```

- `model` — the model id the CLI runs.
- `[model_providers.<name>]` — a provider block. `base_url` is the endpoint, `env_key` names the environment variable that holds the credential. (Only these two keys are shown, matching what the Codex CLI guide documents; do not add provider keys the guide does not name.)
- `[mcp_servers.<name>]` — an MCP server the CLI launches. `command` plus `args`; use `url` for a remote server.

Project-scoped overrides belong in `.codex/config.toml` inside the repository — a server that is not registered there is never started. After editing, confirm the server loaded with `/mcp` inside a session.

## Point it at an endpoint with your own key

Two environment variables are enough; no `config.toml` edit is required for this path:

```bash
export OPENAI_BASE_URL="https://api.codegateway.dev/v1"
export OPENAI_API_KEY="sk-cg-xxxxxxxxxxxxxxxx"
codex login --skip
```

Prompts, MCP servers and the `AGENTS.md` chain behave the same way. Skipping OAuth is what lets a key-based endpoint work — the Codex CLI guide documents `codex login --skip` for exactly this path.

## Verify

```bash
codex "What does this repo do?"
```

Then check the request in your gateway usage log.

- A 401 → the key in this shell is missing or wrong.
- A 451 → wrong endpoint, see below.

## The two region errors

They look similar and are not the same thing:

- **451 unsupported region** — the provider is refusing the request by region. Re-running `codex login` does not clear it. Point the CLI at a compatible endpoint via a `[model_providers.<name>]` block with `base_url` and `env_key`, export the key, and start a new session.
- **`unsupported_country_region_territory`** — a transient refusal of this one request: HTTP 503 with a `Retry-After` header. Retry after a few seconds; if it keeps failing, use a different provider's model.

## Notes and boundaries

- Codex CLI is OpenAI's tool. Pointing it at a third-party endpoint is a supported configuration, but it is not affiliated with or endorsed by OpenAI.
- CodeGateway is an independent gateway, not affiliated with or endorsed by OpenAI.
- Model ids and prices change — check the [model catalog](https://www.codegateway.dev/en/pricing/compare) and the [pricing page](https://www.codegateway.dev/en/pricing) before you budget anything.

## Related

- Guide: [Codex CLI complete guide](https://www.codegateway.dev/en/blog/openai-codex-cli-complete-guide-2026)
- Pricing: [https://www.codegateway.dev/en/pricing](https://www.codegateway.dev/en/pricing)

## License

MIT. Use, adapt, ship.
