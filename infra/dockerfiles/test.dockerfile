FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --all-extras --no-install-project

COPY . .
RUN uv sync --frozen --all-extras

CMD ["uv", "run", "pytest", "-v", "-s"]
