#!/usr/bin/env bash
# Usage: infra/scripts/database/update_database.sh <local|prd>
# Idempotently (re)seeds singleton rows that migrations only insert as a
# best-effort guard (`INSERT ... WHERE NOT EXISTS`) — `about_me` and
# `curriculum_vitae`. Needed after `migration_restart`, since its regenerated
# "init" migration comes from `alembic revision --autogenerate`, which only
# captures schema diffs, not the hand-written seed INSERTs baked into the
# migrations it replaces (see f8552ea2698b_aboutme_rework.py,
# 2f4a5056dc07_cv_section.py) — without this, the tables exist but are empty
# and the public GET endpoints 404.
set -euo pipefail

ENV_NAME="${1:?Usage: update_database.sh <local|prd>}"
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

echo "Seeding about_me singleton (no-op if it already exists)..."
"${PSQL[@]}" -c "INSERT INTO about_me (id, created_at, updated_at) \
  SELECT gen_random_uuid(), now(), now() WHERE NOT EXISTS (SELECT 1 FROM about_me);"

echo "Seeding curriculum_vitae singleton (no-op if it already exists)..."
"${PSQL[@]}" -c "INSERT INTO curriculum_vitae (id, created_at, updated_at) \
  SELECT gen_random_uuid(), now(), now() WHERE NOT EXISTS (SELECT 1 FROM curriculum_vitae);"

echo "Database up to date."
