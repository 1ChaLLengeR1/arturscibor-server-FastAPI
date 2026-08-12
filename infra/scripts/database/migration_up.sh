#!/usr/bin/env bash
# Usage: infra/scripts/database/migration_up.sh <local|prod>
# Applies database/psql/sql/database_up.sql (extensions), then
# `alembic upgrade head`.
set -euo pipefail

ENV_NAME="${1:?Usage: migration_up.sh <local|prod>}"
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

export PGPASSWORD="$ARTURSCIBOR_BACKEND_DB_PASSWORD"
PSQL=(psql -h "$ARTURSCIBOR_BACKEND_DB_HOST" -p "$ARTURSCIBOR_BACKEND_DB_PORT" \
      -U "$ARTURSCIBOR_BACKEND_DB_USER" -d "$ARTURSCIBOR_BACKEND_DB_NAME" -v ON_ERROR_STOP=1)

echo "Checking connection to ${ARTURSCIBOR_BACKEND_DB_NAME}@${ARTURSCIBOR_BACKEND_DB_HOST}:${ARTURSCIBOR_BACKEND_DB_PORT}..."
"${PSQL[@]}" -c "SELECT 1;" > /dev/null

echo "Applying database_up.sql..."
"${PSQL[@]}" -f "$REPO_ROOT/database/psql/sql/database_up.sql"

echo "Running alembic upgrade head..."
cd "$REPO_ROOT"
ENV_MODE="$ENV_NAME" uv run alembic upgrade head
