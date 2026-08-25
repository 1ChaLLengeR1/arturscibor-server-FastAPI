#!/usr/bin/env bash
# Usage: infra/scripts/database/restart.sh <local|stg|prd>
# Full schema reset: downgrade to base, drop everything, DELETE all
# existing Alembic version files, regenerate a single fresh migration via
# autogenerate, reapply, then reseed singleton rows (autogenerate only
# captures schema diffs, not the hand-written seed INSERTs the deleted
# migrations had — see update_database.sh) and the admin user (see
# seed_admin.sql).
set -euo pipefail

ENV_NAME="${1:?Usage: restart.sh <local|stg|prd>}"
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

cd "$REPO_ROOT"

echo "Downgrading to base..."
ENV_MODE="$ENV_NAME" uv run alembic downgrade base || true

export PGPASSWORD="$ARTURSCIBOR_BACKEND_DB_PASSWORD"
PSQL=(psql -h "$ARTURSCIBOR_BACKEND_DB_HOST" -p "$ARTURSCIBOR_BACKEND_DB_PORT" \
      -U "$ARTURSCIBOR_BACKEND_DB_USER" -d "$ARTURSCIBOR_BACKEND_DB_NAME" -v ON_ERROR_STOP=1)

echo "Dropping everything (database_down.sql)..."
"${PSQL[@]}" -f "$REPO_ROOT/database/psql/sql/database_down.sql"

echo "Deleting existing migration version files..."
rm -f "$REPO_ROOT"/alembic/versions/*.py

echo "Generating a fresh init migration from current models..."
ENV_MODE="$ENV_NAME" uv run alembic revision --autogenerate -m "init"

echo "Applying it..."
"$REPO_ROOT/infra/scripts/database/migration_up.sh" "$ENV_NAME"

echo "Reseeding singleton rows (autogenerate doesn't capture the old migrations' seed INSERTs)..."
"$REPO_ROOT/infra/scripts/database/update_database.sh" "$ENV_NAME"

echo "Seeding admin user (database/psql/sql/seed_admin.sql)..."
"${PSQL[@]}" -f "$REPO_ROOT/database/psql/sql/seed_admin.sql"
