# claude-desktop-config — Claude Desktop's config file, and where the key actually goes

Everything you need to point Claude Desktop at an Anthropic-compatible endpoint, split into the two files people keep conflating.

## The two surfaces

Claude Desktop has two independent configuration surfaces, and mixing them up is the single most common reason a "custom endpoint" setup silently does nothing.

| Surface | What it configures | Where it lives |
|---------|--------------------|----------------|
| `claude_desktop_config.json` | MCP servers only. Each server's apikey goes in that server's own `env` object, next to `command` and `args`. | macOS `~/Library/Application Support/Claude/claude_desktop_config.json` · Windows `%APPDATA%\Claude\claude_desktop_config.json` |
| Developer Mode third-party inference | The inference endpoint itself: `inferenceProvider`, `inferenceGatewayBaseUrl`, `inferenceGatewayApiKey`. | The in-app window (Help → Troubleshooting → Enable Developer Mode → Developer → Configure Third-Party Inference…), written by the app into OS-managed preferences |

The MCP server list sits under `mcpServers`. There is no file-level apikey field, and no field in it changes which API host Claude Desktop sends inference requests to.

## `claude_desktop_config.json`

Copy this as-is and edit the paths and key names to match your setup:

```json
{
  "mcpServers": {
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "your-brave-api-key"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users/yourname/projects"],
      "env": {}
    }
  }
}
```

Each server carries its own `env` object. Two servers that need different credentials never share one, and a key scoped to one server is not exposed to the others.

## Developer Mode third-party inference (the custom endpoint)

Open the window, set the provider to gateway, and fill in the base url and the key:

```json
{
  "inferenceProvider": "gateway",
  "inferenceGatewayBaseUrl": "https://api.codegateway.dev",
  "inferenceGatewayApiKey": "sk-cg-xxxxxxxxxxxxxxxx"
}
```

Field notes:

- `inferenceProvider` — set to `gateway` to select a self-hosted gateway as the inference provider.
- `inferenceGatewayBaseUrl` — the full URL of your gateway endpoint. Available from Claude Desktop 1.2581.0.
- `inferenceGatewayApiKey` — the API key for that gateway. Also from 1.2581.0.
- `inferenceGatewayAuthScheme` — `bearer` (default) or `x-api-key`. Added in 1.3036.0. Set it only if your gateway accepts one header and not the other.
- `inferenceModels` — an explicit model list. Use it when your gateway does not implement `GET /v1/models`, or to control the picker order. The first entry becomes the default.

The gateway must implement the Anthropic Messages API: `POST /v1/messages`, with streaming and tool use. A gateway that speaks only the OpenAI format needs a translation layer in front of it.

On the base url, the official examples show it both with and without `/v1` — follow your gateway's own documentation.

## Quickstart

1. Get an API key: sign up at https://www.codegateway.dev, create a key (`sk-cg-…`) in your dashboard and copy it. The plaintext is shown once; only its hash is stored.
2. Enable Developer Mode: Help → Troubleshooting → Enable Developer Mode, then Developer → Configure Third-Party Inference…
3. Set `inferenceProvider` to `gateway`, `inferenceGatewayBaseUrl` to your gateway's URL, and paste the key into `inferenceGatewayApiKey`.
4. Send one message and confirm the request appears in your gateway usage log.

## Verify

- No request in the usage log after a restart → the app read the old configuration; fully quit and relaunch it. Configuration is read at startup.
- A 401 → the key in the window does not match the gateway.
- The custom endpoint works but MCP servers do not → the MCP server entries or their `env` keys are wrong; that is the other file, not this one.

## Paths

| OS | Path |
|----|------|
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |

Edit the file before launching Claude Desktop.

## Notes and boundaries

- Claude Desktop is Anthropic's client. This recipe configures a third-party endpoint; it is not affiliated with or endorsed by Anthropic.
- CodeGateway is an independent gateway. It is not affiliated with or endorsed by Anthropic.
- The command paths in the examples are placeholders — swap in the servers you actually run.

## Related

- Guide: [Claude Desktop developer mode and custom endpoint setup](https://www.codegateway.dev/en/blog/claude-desktop-developer-mode-api-proxy)
- Setup page: [https://www.codegateway.dev/en/coding-agent-setup](https://www.codegateway.dev/en/coding-agent-setup)
- Pricing: [https://www.codegateway.dev/en/pricing](https://www.codegateway.dev/en/pricing)

## License

MIT. Use, adapt, ship.
