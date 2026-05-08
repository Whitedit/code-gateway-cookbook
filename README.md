# code-gateway-cookbook

Public scripts, recipes, and code samples for the [CodeGateway](https://www.codegateway.dev) blog and docs. Everything here is plain Python / shell / YAML, copyable, and tied to a specific blog post or docs page so you can see exactly where it's used.

## Recipes

| Folder | Description | Companion post |
|--------|-------------|---------------|
| [`image-gen/`](./image-gen) | Batch image generation runner — single-file Python CLI that reads a YAML spec and calls the CodeGateway image API. Supports Imagen 4, Gemini 2.5 Flash Image, and OpenAI GPT Image. | [An Honest Receipt: 16 Blog Hero Images for $0.92 in an Hour](https://www.codegateway.dev/blog/blog-image-pipeline-cost-receipt) |

More recipes get added as new blog posts and docs reference them. Coming soon: Claude Code automation snippets, Codex CLI integration scripts, batch billing analytics.

## Layout

Every recipe is a self-contained subdirectory with:

- The script(s) — runnable as-is.
- A `README.md` describing the scenario, quickstart, and link back to the related blog post.
- Example input / spec / config files.

## License

MIT. Use, adapt, ship.

## Related

- Product: [https://www.codegateway.dev](https://www.codegateway.dev)
- Docs: [https://www.codegateway.dev/docs](https://www.codegateway.dev/docs)
- Blog: [https://www.codegateway.dev/blog](https://www.codegateway.dev/blog)
- Pricing: [https://www.codegateway.dev/pricing](https://www.codegateway.dev/pricing)
