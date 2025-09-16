#!/usr/bin/env bash
set -euo pipefail

SRC="/home/heiner/waldsensor-sh.github.io/data/v2/latest"
OUT="/home/heiner/waldsensor-sh.github.io/data/v2/latest/all.json"

# alle per-node-JSONs (ohne _all.json) einsammeln
mapfile -t files < <(find "$SRC" -maxdepth 1 -type f -name '*.json' ! -name '_all.json' | sort)

# zu einem Array mergen
if command -v jq >/dev/null 2>&1; then
  jq -s '.' "${files[@]}" > "$OUT"
else
  echo "jq fehlt (sudo apt install jq)" >&2
  exit 1
fi
