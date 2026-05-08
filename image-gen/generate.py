#!/usr/bin/env python3
"""CodeGateway image generation runner.

Reads a YAML/JSON spec, calls https://api.codegateway.dev/v1/images/generations
(production by default), saves PNGs to disk, and prints a per-image cost report.

Usage:
    generate.py --spec /tmp/spec.yaml \\
        --api-base https://api.codegateway.dev/v1 \\
        --api-key $CODEGATEWAY_PROD_API_KEY \\
        [--dry-run] [--out-dir /tmp/sprint4b-images]

Spec entry shape (YAML list):
    - name: 297-hero
      model: imagen-4.0-fast-generate-001    # required
      prompt: "..."                            # required
      size: "1792x1024"                        # OpenAI route models only
      aspect: "16:9"                           # Vertex route models (Imagen / Gemini)
      n: 1                                     # default 1
      out: /tmp/sprint4b-images/297-hero.png   # absolute path
      quality: medium                          # OpenAI route (low/medium/high)
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

# ── Pricing matrix (2026-05-07) ──────────────────────────────────────────────

IMAGEN_PRICE_PER_IMG = {
    "imagen-4.0-fast-generate-001":  0.02,
    "imagen-4.0-generate-001":       0.04,
    "imagen-4.0-ultra-generate-001": 0.06,
}

GEMINI_PRICING = {
    "gemini-2.5-flash-image": {
        "input_per_mtok":         0.30,
        "output_text_per_mtok":   2.50,
        "output_image_per_mtok": 30.00,
    },
}

OPENAI_IMAGE_MATRIX = {
    "gpt-image-2": {
        "low":    {"square": 0.006, "portrait": 0.005, "landscape": 0.005},
        "medium": {"square": 0.053, "portrait": 0.041, "landscape": 0.041},
        "high":   {"square": 0.211, "portrait": 0.165, "landscape": 0.165},
    },
    "gpt-image-1.5": {
        "low":    {"square": 0.009, "portrait": 0.013, "landscape": 0.013},
        "medium": {"square": 0.034, "portrait": 0.050, "landscape": 0.050},
        "high":   {"square": 0.133, "portrait": 0.200, "landscape": 0.200},
    },
}

VERTEX_MODELS = set(IMAGEN_PRICE_PER_IMG) | set(GEMINI_PRICING)
OPENAI_MODELS = set(OPENAI_IMAGE_MATRIX)

# ── Spec loader ──────────────────────────────────────────────────────────────


def _load_spec(path: Path) -> list[dict[str, Any]]:
    """Load YAML or JSON spec. Tiny YAML subset implemented inline to avoid
    dragging in PyYAML — only supports the shape documented in this file's
    docstring."""
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        data = json.loads(text)
        return list(data) if isinstance(data, list) else [data]
    return _parse_yaml_list(text)


def _parse_yaml_list(text: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    cur: dict[str, Any] | None = None
    cur_key: str | None = None
    cur_buf: list[str] | None = None
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if line.startswith("- "):
            _flush_buf(cur, cur_key, cur_buf)
            if cur is not None:
                items.append(cur)
            cur = {}
            cur_key, cur_buf = None, None
            line = "  " + line[2:]
        if cur is None:
            raise ValueError(f"unexpected content before first list item: {raw!r}")
        if line.startswith("    ") and cur_key is not None and cur_buf is not None:
            cur_buf.append(line.strip())
            continue
        _flush_buf(cur, cur_key, cur_buf)
        cur_key, cur_buf = None, None
        s = line.strip()
        if ":" not in s:
            raise ValueError(f"line missing colon: {raw!r}")
        k, _, v = s.partition(":")
        k = k.strip()
        v = v.strip()
        if v == "|":
            cur_key, cur_buf = k, []
            continue
        if v == "":
            cur_key, cur_buf = k, []
            continue
        if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
            v = v[1:-1]
        if v.isdigit():
            cur[k] = int(v)
        else:
            cur[k] = v
    _flush_buf(cur, cur_key, cur_buf)
    if cur is not None:
        items.append(cur)
    return items


def _flush_buf(cur: dict | None, key: str | None, buf: list[str] | None) -> None:
    if cur is not None and key is not None and buf is not None:
        cur[key] = "\n".join(buf).strip()


# ── HTTP client ──────────────────────────────────────────────────────────────


def _post(url: str, body: dict, headers: dict, timeout: int = 180) -> dict:
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
        return json.loads(resp.read().decode("utf-8"))


# ── Per-image cost ───────────────────────────────────────────────────────────


def _aspect_class(size: str | None, aspect: str | None) -> str:
    """Classify into square/portrait/landscape based on size or aspect."""
    if size and "x" in size:
        try:
            w, h = (int(x) for x in size.lower().split("x", 1))
            if w == h:
                return "square"
            return "portrait" if h > w else "landscape"
        except ValueError:
            pass
    if aspect and ":" in aspect:
        a, b = aspect.split(":", 1)
        try:
            ai, bi = int(a), int(b)
            if ai == bi:
                return "square"
            return "portrait" if bi > ai else "landscape"
        except ValueError:
            pass
    return "square"


def _estimate_cost(spec: dict, response: dict) -> float:
    model = spec["model"]
    n = int(spec.get("n", 1))
    if model in IMAGEN_PRICE_PER_IMG:
        return IMAGEN_PRICE_PER_IMG[model] * n
    if model in GEMINI_PRICING:
        usage = response.get("usage", {})
        rate = GEMINI_PRICING[model]
        in_tok = int(usage.get("prompt_tokens") or 0)
        out_tok = int(usage.get("completion_tokens") or 0)
        in_cost = in_tok / 1_000_000 * rate["input_per_mtok"]
        out_cost = out_tok / 1_000_000 * rate["output_image_per_mtok"]
        if in_cost + out_cost > 0:
            return in_cost + out_cost
        return 0.06 * n
    if model in OPENAI_IMAGE_MATRIX:
        quality = (spec.get("quality") or "medium").lower()
        ac = _aspect_class(spec.get("size"), spec.get("aspect"))
        return OPENAI_IMAGE_MATRIX[model][quality][ac] * n
    return 0.0


# ── Request body builder ─────────────────────────────────────────────────────


def _build_body(spec: dict) -> dict:
    body: dict[str, Any] = {
        "model": spec["model"],
        "prompt": spec["prompt"],
        "n": int(spec.get("n", 1)),
        "response_format": "b64_json",
    }
    model = spec["model"]
    if model in OPENAI_MODELS:
        if "size" in spec:
            body["size"] = spec["size"]
        if "quality" in spec:
            body["quality"] = spec["quality"]
    elif model in VERTEX_MODELS:
        if "aspect" in spec:
            body["aspect_ratio"] = spec["aspect"]
        if "size" in spec:
            body["size"] = spec["size"]
    return body


# ── Main ─────────────────────────────────────────────────────────────────────


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--spec", required=True)
    p.add_argument("--api-base", default="https://api.codegateway.dev/v1")
    p.add_argument("--api-key", default=os.environ.get("CODEGATEWAY_PROD_API_KEY"))
    p.add_argument("--out-dir", default="/tmp/sprint4b-images")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    if not args.api_key:
        sys.stderr.write(
            "error: --api-key or CODEGATEWAY_PROD_API_KEY required\n"
        )
        return 2

    spec = _load_spec(Path(args.spec))
    if not spec:
        sys.stderr.write(f"empty spec: {args.spec}\n")
        return 1

    Path(args.out_dir).mkdir(parents=True, exist_ok=True)

    headers = {
        "Authorization": f"Bearer {args.api_key}",
        "Content-Type": "application/json",
        "User-Agent": "CodeGateway-Image-Gen/1.0",
    }

    print(f"=== Generating {len(spec)} image(s) via {args.api_base} (dry={args.dry_run}) ===\n")
    total_cost = 0.0
    summary: list[tuple[str, str, float, str]] = []
    for entry in spec:
        name = entry.get("name") or entry.get("model", "?")
        out_path = Path(entry.get("out") or f"{args.out_dir}/{name}.png")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        if args.dry_run:
            est = _estimate_cost(entry, {})
            print(f"[dry] {name}  model={entry['model']}  est=${est:.3f}  out={out_path}")
            summary.append((name, entry["model"], est, "dry"))
            total_cost += est
            continue
        body = _build_body(entry)
        try:
            t0 = time.time()
            resp = _post(f"{args.api_base}/images/generations", body, headers)
            dt = time.time() - t0
            data = resp.get("data") or []
            if not data:
                err = resp.get("error") or resp
                summary.append((name, entry["model"], 0, f"FAIL {err}"))
                print(f"[!] {name}  FAIL: {err}", file=sys.stderr)
                continue
            for i, img in enumerate(data):
                img_path = out_path if i == 0 else out_path.with_stem(f"{out_path.stem}-{i}")
                if "b64_json" in img:
                    img_path.write_bytes(base64.b64decode(img["b64_json"]))
                elif "url" in img:
                    with urllib.request.urlopen(img["url"], timeout=60) as r:  # noqa: S310
                        img_path.write_bytes(r.read())
                else:
                    summary.append((name, entry["model"], 0, "no b64_json/url"))
                    continue
            cost = _estimate_cost(entry, resp)
            total_cost += cost
            sz = out_path.stat().st_size if out_path.exists() else 0
            summary.append((name, entry["model"], cost, f"OK {dt:.1f}s {sz//1024}KB"))
            print(f"[+] {name}  model={entry['model']}  cost=${cost:.3f}  {dt:.1f}s  {sz//1024}KB  -> {out_path}")
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")[:300]
            summary.append((name, entry["model"], 0, f"HTTP {e.code}: {err_body}"))
            print(f"[!] {name}  HTTP {e.code}: {err_body}", file=sys.stderr)
        except Exception as e:  # noqa: BLE001
            summary.append((name, entry["model"], 0, f"ERR {e}"))
            print(f"[!] {name}  ERR: {e}", file=sys.stderr)

    print("\n=== SUMMARY ===")
    for name, model, cost, status in summary:
        print(f"  {name:30s} {model:35s} ${cost:.3f}  {status}")
    print(f"\n  TOTAL COST: ${total_cost:.3f}  (n={len([s for s in summary if s[3].startswith('OK')])} OK)")
    return 0 if all(s[3].startswith(("OK", "dry")) for s in summary) else 1


if __name__ == "__main__":
    raise SystemExit(main())
