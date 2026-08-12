#!/usr/bin/env bash
# Usage: infra/scripts/run_mode.sh <local|prod>
# Switches the ENV_MODE default in config/app.py (local convenience only —
# the running server/container should set ENV_MODE directly instead).
set -euo pipefail

MODE="${1:?Usage: run_mode.sh <local|prod>}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

case "$MODE" in
  local|prod) ;;
  *) echo "Unknown mode: $MODE (expected local|prod)" >&2; exit 1 ;;
esac

sed -i.bak "s/^ENV_MODE = .*/ENV_MODE = os.getenv(\"ENV_MODE\", \"$MODE\")/" "$REPO_ROOT/config/app.py"
rm -f "$REPO_ROOT/config/app.py.bak"
echo "ENV_MODE default set to: $MODE"
