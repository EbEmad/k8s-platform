# Uptime Monitor 

A self-hosted uptime monitor and status page, built and operated live on YouTube while applying
DevOps practices end to end. Everything runs locally, so the total cloud cost is **$0**.

```
            ┌──────────┐   status page / API   ┌─────────────┐
 browser ──▶│   api    │──────────────────────▶│             │
            │ FastAPI  │                       │  Postgres   │
            └──────────┘                       │             │
            ┌──────────┐  checks URLs every Ns │             │
            │  worker  │──────────────────────▶│             │
            └──────────┘                       └─────────────┘
            ┌──────────┐
            │ migrate  │  one-shot: creates the schema before api/worker start
            └──────────┘
```

One image, three roles (`api`, `worker`, `migrate`).

## Quick start

Requirements: [uv](https://docs.astral.sh/uv/), Docker or Podman (with compose), make.

```bash
make install   # dependencies
make check     # lint + security scan + tests (same as CI)
make up        # full stack on http://localhost:8000
curl -X POST localhost:8000/api/monitors -H 'content-type: application/json' \
     -d '{"name": "Example", "url": "https://example.com"}'
make logs      # watch the worker check it
make clean     # stop and wipe data
```

Run `make` to list every target.

## Configuration

All configuration comes from environment variables (twelve-factor):

| Variable | Default | Purpose |
|---|---|---|
| `UPTIME_DATABASE_URL` | `postgresql+psycopg://uptime:uptime@localhost:5432/uptime` | SQLAlchemy URL |
| `UPTIME_CHECK_INTERVAL_SECONDS` | `30` | Time between check cycles |
| `UPTIME_CHECK_TIMEOUT_SECONDS` | `10` | Per-request timeout |
| `UPTIME_ADMIN_TOKEN` | *(empty)* | If set, creating or deleting monitors needs `Authorization: Bearer <token>` |

> ⚠️ Set `UPTIME_ADMIN_TOKEN` before exposing the app publicly. Otherwise anyone can make the
> worker request arbitrary URLs (SSRF).

## Endpoints

| Path | Purpose |
|---|---|
| `GET /` | Status page (htmx, refreshes every 10 s) |
| `GET /healthz` | Liveness: the process is up |
| `GET /readyz` | Readiness: the database is reachable |
| `GET/POST /api/monitors`, `DELETE /api/monitors/{id}` | Manage monitors |

