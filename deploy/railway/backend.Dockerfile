FROM ghcr.io/astral-sh/uv:0.13.1 AS uv

FROM python:3.12-slim

COPY --from=uv /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev --extra ai --extra mcp

COPY backend/app ./app
COPY backend/alembic.ini ./
COPY backend/alembic ./alembic

RUN uv sync --frozen --no-dev --extra ai --extra mcp \
    && useradd --create-home --uid 10001 appuser \
    && mkdir -p /data/chroma /data/embedding-cache \
    && chown -R appuser:appuser /data

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
