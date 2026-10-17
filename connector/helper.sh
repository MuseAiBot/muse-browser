#!/bin/bash
# muse-browser API helper. Requires MUSE_BROWSER_URL and MUSE_BROWSER_TOKEN.
set -euo pipefail
BASE="${MUSE_BROWSER_URL:-http://localhost:8765}"
AUTH=(-H "Authorization: Bearer ${MUSE_BROWSER_TOKEN:?set MUSE_BROWSER_TOKEN}")
api() { curl -sf "${AUTH[@]}" "$BASE$1" ${2:+-d "$2"} -H 'Content-Type: application/json'; }
case "${1:-}" in
  status) api /status ;;
  sessions) api /sessions ;;
  create) api /sessions "{\"profile\":\"${2:-default}\"}" ;;
  nav) api "/sessions/$2/navigate" "{\"url\":\"$3\"}" ;;
  text) api "/sessions/$2/text" ;;
  hist) api "/history?${2:-limit=20}" ;;
  *) echo "usage: $0 status|sessions|create <profile>|nav <sid> <url>|text <sid>|hist <query>" >&2; exit 1 ;;
esac
