FROM python:3.14-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev --no-install-project

COPY . .

EXPOSE 8000

CMD ["uvicorn", "uptime.api:app", "--port", "8000", "--host", "0.0.0.0"]