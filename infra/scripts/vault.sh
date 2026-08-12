#!/usr/bin/env bash
# Usage: ANSIBLE_PASSWORD=... infra/scripts/vault.sh <encrypt|decrypt|view>
set -euo pipefail

ACTION="${1:?Usage: vault.sh <encrypt|decrypt|view>}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SECRETS_FILE="$REPO_ROOT/infra/ansible/secrets.yml"
: "${ANSIBLE_PASSWORD:?Set ANSIBLE_PASSWORD before running this script}"

VAULT_PASS_FILE="$(mktemp)"
trap 'rm -f "$VAULT_PASS_FILE"' EXIT
printf '%s' "$ANSIBLE_PASSWORD" > "$VAULT_PASS_FILE"

case "$ACTION" in
  encrypt) ansible-vault encrypt "$SECRETS_FILE" --vault-password-file "$VAULT_PASS_FILE" ;;
  decrypt) ansible-vault decrypt "$SECRETS_FILE" --vault-password-file "$VAULT_PASS_FILE" ;;
  view)    ansible-vault view "$SECRETS_FILE" --vault-password-file "$VAULT_PASS_FILE" ;;
  *) echo "Unknown action: $ACTION (expected encrypt|decrypt|view)" >&2; exit 1 ;;
esac
