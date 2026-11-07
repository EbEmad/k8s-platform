FROM  debian:trixie-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON=3.14 \
    UV_PYTHON_PREFERENCE=only-managed \
    UV_PYTHON_INSTALL_DIR=/python \
    PATH="/app/.venv/bin:$PATH"


WORKDIR /app

ENV UV_PROJECT_ENVIRONMENT="/app/.venv"

RUN uv python install \
    # psycopg[binary] needs libz, which distroless/cc doesn't ship
    && mkdir -p /runtime-libs \
    && cp -L /lib/$(uname -m)-linux-gnu/libz.so.1 /runtime-libs/ \
    && rm -rf /python/*/lib/python3.*/site-packages/pip* \
          /python/*/lib/python3.*/ensurepip

# Copy dependency definition files first
COPY pyproject.toml uv.lock ./


# Install dependencies into the virtual environment (.venv)
RUN uv sync --frozen --no-dev --no-install-project

# Copy the application source code
COPY . .

RUN uv sync --frozen --no-dev


FROM gcr.io/distroless/cc-debian13@sha256:58e12be899275afaa05f1b03051ab19037ed7f252528e57a3a9ad7e220a62578 AS runtime

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY --from=builder /python /python
COPY --from=builder /runtime-libs/ /usr/lib/
COPY --from=builder /app /app

USER nonroot

EXPOSE 8000
CMD ["uvicorn", "uptime.api:app", "--port", "8000", "--host", "0.0.0.0"]



