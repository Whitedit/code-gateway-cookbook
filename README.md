# code-gateway-cookbook

Copy-paste recipes for Claude Desktop, Claude Code and Codex CLI on top of the [CodeGateway](https://www.codegateway.dev) API — every recipe is a self-contained folder you can clone, read and run as-is.

> Looking for the exact `claude_desktop_config.json` contents, the Anthropic API price list, or the Codex CLI config? Start with the recipe table below.

## Recipes

| Folder | What it does | Companion guide |
|--------|--------------|-----------------|
| [`claude-desktop-config/`](./claude-desktop-config) | The Claude Desktop configuration file, explained field by field: where `claude_desktop_config.json` lives, which key goes in the MCP server `env` object, and how the custom API base url is set in Developer Mode third-party inference. | [Claude Desktop developer mode and custom endpoint setup](https://www.codegateway.dev/en/blog/claude-desktop-developer-mode-api-proxy) |
| [`codex-cli/`](./codex-cli) | Codex CLI config.toml and environment setup — install paths, `~/.codex/config.toml` keys, pointing the CLI at an Anthropic-compatible or OpenAI-compatible endpoint, and the two region errors people hit first. | [Codex CLI complete guide](https://www.codegateway.dev/en/blog/openai-codex-cli-complete-guide-2026) |
| [`image-gen/`](./image-gen) | Batch image generation runner — single-file Python CLI that reads a YAML spec and calls the CodeGateway image API. Supports Imagen 4, Gemini 2.5 Flash Image, and OpenAI GPT Image. | [An Honest Receipt: 16 Blog Hero Images for $0.92 in an Hour](https://www.codegateway.dev/blog/blog-image-pipeline-cost-receipt) |

Each recipe ships with a README that states the scenario, a quickstart, and a link back to the guide it supports, so you can see exactly where each piece is used.

## Which config file do I actually need?

Three files come up in every Claude Desktop question, and they do different jobs:

| File | Holds | Does not hold |
|------|-------|---------------|
| `claude_desktop_config.json` | The MCP server list. Each server's own apikey goes in that server's `env` object, next to `command` and `args`. | No top-level apikey field, and no base URL — the file cannot change which API host Claude Desktop talks to. |
| Developer Mode third-party inference | `inferenceProvider`, `inferenceGatewayBaseUrl`, `inferenceGatewayApiKey` — the custom API endpoint and its credential. | Not a file you edit by hand in most setups; it is written by the app into OS-managed preferences. |
| `~/.codex/config.toml` | Codex CLI's model, provider, base URL, approval policy and MCP servers. | Not where credentials live — those are in `~/.codex/auth.json` or the environment. |

The one-line version: **`claude_desktop_config.json` is the MCP list, not the API host.** Changing the endpoint is a Developer Mode action; changing the endpoint for the Codex CLI is an environment variable.

See [`claude-desktop-config/`](./claude-desktop-config) for the file anatomy and the copy-paste blocks.

## Common questions

Short answers, with the exact file and field names.

**claude_desktop_config.json apikey — where does it go?**
Into the `env` object of the individual MCP server entry that the key authenticates, next to that entry's `command` and `args` — not at the top level of the file.

**claude_desktop_config.json env api — can it set a base url?**
No. The file has no top-level `env` key and no base-URL key of any kind. The custom API base url goes into the Developer Mode third-party inference window as `inferenceGatewayBaseUrl`.

**claude_desktop_config.json authentication key — which key does the file read?**
The key named in each server's own `env` object. There is no file-level authentication key that redirects Claude Desktop to a different API host.

**claude desktop configuration file apikey — which file holds it?**
`claude_desktop_config.json` holds the MCP server list and each server's `env` keys. Claude Desktop's own inference credential is separate: `inferenceGatewayApiKey`, set in Developer Mode.

**claude_desktop_config.json example — what does a working file look like?**
The MCP server list sits under `mcpServers`, with each entry carrying `command`, `args`, and its own `env`. See the copy-paste block in [`claude-desktop-config/`](./claude-desktop-config).

**claude desktop custom api base url — how is it set?**
In the Developer Mode third-party inference window, as `inferenceGatewayBaseUrl`, next to `inferenceGatewayApiKey`. The gateway must implement `POST /v1/messages`, with streaming and tool use.

**codex cli config.toml — where do the settings live?**
`~/.codex/config.toml` holds the model, provider, base URL, approval policy and MCP servers. Credentials live in `~/.codex/auth.json` or the environment — `OPENAI_BASE_URL` and `OPENAI_API_KEY`.

## Anthropic API pricing

Published rates change; this section records the reading and the source, not a promise.

- **Unit:** USD per 1M tokens (MTok), input and output priced separately. A 5-minute cache write bills at 1.25x the input rate and a 1-hour cache write at 2x it; a cache-hit read bills at 0.1x the input rate — except Opus 5.5 and Sonnet 5.5, where a cache read is 0.05x, and Fable 5.1, where it is 0.025x.
- **Claude token cost** therefore depends mostly on how much context you carry per request and how long the output runs, not on the headline price table.
- **Anthropic pricing** and **claude api pricing** are the same list on Anthropic's side; the numbers people usually want for a **claude api pricing** estimate are input and output per MTok, plus the cache multipliers.
- The full per-model table, with the current rates, is on the [price comparison page](https://www.codegateway.dev/en/pricing/compare).

Do not budget from a screenshot of this file — check the live pages.

## Layout

Every recipe is a self-contained subdirectory with:

- The script(s) or config file(s) — runnable as-is.
- A `README.md` describing the scenario, quickstart, and link back to the related guide.
- Example input / spec / config files.

## License

MIT. Use, adapt, ship.

## Related

- Product: [https://www.codegateway.dev](https://www.codegateway.dev)
- Docs: [https://www.codegateway.dev/en/docs](https://www.codegateway.dev/en/docs)
- Blog: [https://www.codegateway.dev/en/blog](https://www.codegateway.dev/en/blog)
- Pricing: [https://www.codegateway.dev/en/pricing](https://www.codegateway.dev/en/pricing)
