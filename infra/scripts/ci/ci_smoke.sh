#!/bin/bash
# Trzywarstwowy smoke obrazu produkcyjnego PRZED buildem/pushem na Docker Hub.
# Layer 1 - build obrazu, Layer 2 - import/mappery, Layer 3 - boot + probe /docs
# (brak /health w tym API, patrz api/router.py — /docs to wbudowany Swagger UI
# FastAPI, wystarczy jako dowód, że aplikacja realnie wstała i odpowiada).
set -e

IMAGE="arturscibor_backend_smoke:ci"
CONTAINER="arturscibor_backend_smoke"

DUMMY_ENV=(
  -e ARTURSCIBOR_BACKEND_DB_HOST=localhost
  -e ARTURSCIBOR_BACKEND_DB_PORT=5432
  -e ARTURSCIBOR_BACKEND_DB_USER=smoke
  -e ARTURSCIBOR_BACKEND_DB_PASSWORD=smoke
  -e ARTURSCIBOR_BACKEND_DB_NAME=smoke
  -e ARTURSCIBOR_BACKEND_SECRET_ADMIN_TOKEN=smoke
  -e ARTURSCIBOR_BACKEND_REFRESH_ADMIN_TOKEN=smoke
  -e ARTURSCIBOR_BACKEND_ACCESS_TOKEN_EXPIRE_HOURS=1
  -e ARTURSCIBOR_BACKEND_REFRESH_TOKEN_EXPIRE_HOURS=1
  -e ARTURSCIBOR_BACKEND_ALGORITHM=HS256
  -e ARTURSCIBOR_BACKEND_SERVER=http://localhost:8000
)

cleanup() {
  docker rm -f "$CONTAINER" >/dev/null 2>&1 || true
}
trap cleanup EXIT

echo "=== Layer 1: build obrazu produkcyjnego ==="
docker build -t "$IMAGE" -f infra/dockerfiles/production.dockerfile .

echo "=== Layer 2: import check (main + routery + modele) ==="
docker run --rm "${DUMMY_ENV[@]}" "$IMAGE" uv run python -c "import main; print('import ok')"

echo "=== Layer 3: boot uvicorna + probe /docs ==="
docker run -d --name "$CONTAINER" "${DUMMY_ENV[@]}" -p 8000:8000 "$IMAGE"

for _ in $(seq 1 30); do
  if curl -fsS http://localhost:8000/docs >/dev/null 2>&1; then
    echo "=== Smoke OK: /docs odpowiada ==="
    exit 0
  fi
  sleep 2
done

echo "!!! Backend nie wstał w 60 s - logi kontenera:"
docker logs "$CONTAINER"
exit 1
