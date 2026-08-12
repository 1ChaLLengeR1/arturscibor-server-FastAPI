.PHONY: install run_app run_test clean

install:
	uv sync --all-extras

run_app:
	uv run uvicorn main:app --reload

run_test:
	uv run pytest -s -v

clean:
	rm -rf .venv uv.lock .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
