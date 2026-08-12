#!/usr/bin/env bash
# Usage: infra/scripts/database/migration_down.sh <local|prod>
# DESTRUCTIVE: drops every table this project owns (database_down.sql).
# Asks for confirmation before running against anything other than local.
set -euo pipefail

ENV_NAME="${1:?Usage: migration_down.sh <local|prod>}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
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

if [[ "$ENV_NAME" != "local" ]]; then
  read -r -p "This will DROP ALL TABLES in '${ARTURSCIBOR_BACKEND_DB_NAME}' (env: ${ENV_NAME}). Type the environment name to confirm: " CONFIRM
  if [[ "$CONFIRM" != "$ENV_NAME" ]]; then
    echo "Aborted." >&2
    exit 1
  fi
fi

export PGPASSWORD="$ARTURSCIBOR_BACKEND_DB_PASSWORD"
PSQL=(psql -h "$ARTURSCIBOR_BACKEND_DB_HOST" -p "$ARTURSCIBOR_BACKEND_DB_PORT" \
      -U "$ARTURSCIBOR_BACKEND_DB_USER" -d "$ARTURSCIBOR_BACKEND_DB_NAME" -v ON_ERROR_STOP=1)

echo "Checking connection to ${ARTURSCIBOR_BACKEND_DB_NAME}@${ARTURSCIBOR_BACKEND_DB_HOST}:${ARTURSCIBOR_BACKEND_DB_PORT}..."
"${PSQL[@]}" -c "SELECT 1;" > /dev/null

echo "Applying database_down.sql (dropping all tables)..."
"${PSQL[@]}" -f "$REPO_ROOT/database/psql/sql/database_down.sql"
