#!/usr/bin/env bash
# Usage: source infra/scripts/load_env.sh {local|prod}
# Loads env/{local|prod}.env into the current shell and sanity-checks the
# required ARTURSCIBOR_BACKEND_DB_* variables are present.
set -euo pipefail

ENV_NAME="${1:?Usage: load_env.sh {local|prod}}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ENV_FILE="$REPO_ROOT/env/${ENV_NAME}.env"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing $ENV_FILE" >&2
  exit 1
fi

set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

for var in ARTURSCIBOR_BACKEND_DB_HOST ARTURSCIBOR_BACKEND_DB_PORT ARTURSCIBOR_BACKEND_DB_USER \
           ARTURSCIBOR_BACKEND_DB_PASSWORD ARTURSCIBOR_BACKEND_DB_NAME; do
  if [[ -z "${!var:-}" ]]; then
    echo "Missing required variable: $var" >&2
    exit 1
  fi
done

echo "Loaded $ENV_FILE"
