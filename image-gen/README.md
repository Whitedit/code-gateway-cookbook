# image-gen — CodeGateway Image Generation Runner

A minimal, single-file CLI that reads a YAML spec and runs batch image generation against the [CodeGateway API](https://www.codegateway.dev) (`/v1/images/generations`, OpenAI-compatible). Supports the four upstream model families:

- **Imagen 4** (`imagen-4.0-fast-generate-001` / `imagen-4.0-generate-001` / `imagen-4.0-ultra-generate-001`) — flat per-image pricing $0.02 / $0.04 / $0.06.
- **Gemini 2.5 Flash Image** (`gemini-2.5-flash-image`) — token-based, ~$0.04–0.08/image, strong text rendering.
- **OpenAI GPT Image 2 / 1.5** (`gpt-image-2` / `gpt-image-1.5`) — quality × aspect matrix, native 16:9 / 9:16.

## Why this exists

Companion to the blog post [*An Honest Receipt: 16 Blog Hero Images for $0.92 in an Hour*](https://www.codegateway.dev/blog/blog-image-pipeline-cost-receipt) — the exact runner used to dogfood image generation for our own blog. Public domain so you can copy / adapt.

## Quickstart

1. **Get a CodeGateway API key**: sign up at https://www.codegateway.dev — new accounts get a $2 starter credit (~40 images at the cheapest tier).
2. **Save your spec** as `image-spec.yaml` (see [`spec-example.yaml`](./spec-example.yaml)).
3. **Run**:

```bash
export CODEGATEWAY_PROD_API_KEY="sk-cg-xxxxxxxx"
python3 generate.py --spec image-spec.yaml --api-key "$CODEGATEWAY_PROD_API_KEY"
```

4. **Dry run** (no API calls, just cost estimate):

```bash
python3 generate.py --spec image-spec.yaml --dry-run --api-key dummy
```

## Spec format

```yaml
- name: my-hero
  model: gpt-image-2
  quality: medium
  size: "1536x1024"     # OpenAI route uses size
  prompt: |
    A wide cinematic flat editorial illustration of <YOUR SCENE>...
  out: /tmp/images/my-hero.png

- name: my-concept
  model: imagen-4.0-fast-generate-001
  aspect: "1:1"          # Vertex route uses aspect_ratio
  prompt: |
    A minimal abstract <SUBJECT>, soft purple gradient...
  out: /tmp/images/my-concept.png
```

The dispatcher routes `gpt-image-*` to `size`+`quality` parameters (OpenAI shape), and `imagen-*` / `gemini-*` to `aspect_ratio` (Vertex shape).

## Output

```
=== Generating 16 image(s) via https://api.codegateway.dev/v1 (dry=False) ===

[+] 297-hero  model=imagen-4.0-generate-001  cost=$0.040  10.5s  712KB  -> /tmp/images/297-hero.png
[+] 297-arch  model=gemini-2.5-flash-image  cost=$0.060  17.6s  627KB  -> /tmp/images/297-arch.png
...

=== SUMMARY ===
  TOTAL COST: $0.760  (n=16 OK)
```

## Pricing reference

Verified 2026-05 (subject to upstream changes — always check [the CodeGateway pricing page](https://www.codegateway.dev/pricing) for the latest):

| Model | Price |
|-------|-------|
| `imagen-4.0-fast-generate-001` | $0.02 / image |
| `imagen-4.0-generate-001` | $0.04 / image |
| `imagen-4.0-ultra-generate-001` | $0.06 / image |
| `gemini-2.5-flash-image` | per-token (~$0.04–0.08 / image) |
| `gpt-image-2` low / med / high | $0.005 / $0.041 / $0.165 (16:9 medium) |
| `gpt-image-1.5` low / med / high | $0.013 / $0.050 / $0.200 (16:9 medium) |

## License

MIT. Use, adapt, ship.

## Related

- Blog: [An Honest Receipt: 16 Blog Hero Images for $0.92 in an Hour](https://www.codegateway.dev/blog/blog-image-pipeline-cost-receipt)
- Docs: [CodeGateway Image Generation API](https://www.codegateway.dev/docs/image-api-guide) (coming soon)
- Pricing: [https://www.codegateway.dev/pricing](https://www.codegateway.dev/pricing)
