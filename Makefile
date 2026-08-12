.PHONY: install run_app run_test clean migration_up migration_down migration_restart vault_encrypt vault_decrypt vault_view

ENV ?= local

install:
	uv sync --all-extras

run_app:
	uv run uvicorn main:app --reload

run_test:
	uv run pytest -s -v

clean:
	rm -rf .venv uv.lock .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +

migration_up:
	./infra/scripts/database/migration_up.sh $(ENV)

migration_down:
	./infra/scripts/database/migration_down.sh $(ENV)

migration_restart:
	./infra/scripts/database/restart.sh $(ENV)

vault_encrypt:
	infra/scripts/vault.sh encrypt

vault_decrypt:
	infra/scripts/vault.sh decrypt

vault_view:
	infra/scripts/vault.sh view
