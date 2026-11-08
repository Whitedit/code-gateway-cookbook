#!/usr/bin/env bash
# Verify a Codex CLI endpoint setup.
# Usage: ./verify.sh
# Reads OPENAI_BASE_URL / OPENAI_API_KEY from the environment.
set -euo pipefail

: "${OPENAI_BASE_URL:?OPENAI_BASE_URL is not set}"
: "${OPENAI_API_KEY:?OPENAI_API_KEY is not set}"

echo "codex version:"
codex --version || echo "  codex not on PATH"

echo
echo "endpoint: ${OPENAI_BASE_URL}"

echo
echo "models endpoint:"
curl -sS -o /dev/null -w "  HTTP %{http_code}\n" \
  -H "Authorization: Bearer ${OPENAI_API_KEY}" \
  "${OPENAI_BASE_URL}/models"

echo
echo "If the models endpoint returns 200, run:  codex \"What does this repo do?\""
echo "and confirm the request in your gateway usage log."
