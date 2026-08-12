.PHONY: install run_app run_test clean vault_encrypt vault_decrypt vault_view

install:
	uv sync --all-extras

run_app:
	uv run uvicorn main:app --reload

run_test:
	uv run pytest -s -v

clean:
	rm -rf .venv uv.lock .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +

vault_encrypt:
	infra/scripts/vault.sh encrypt

vault_decrypt:
	infra/scripts/vault.sh decrypt

vault_view:
	infra/scripts/vault.sh view
