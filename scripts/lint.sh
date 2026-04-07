#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -x .venv/bin/python ]]; then
  echo "ERROR: .venv/bin/python not found. Create venv first: python3 -m venv .venv" >&2
  exit 1
fi

.venv/bin/python -m pylint src

