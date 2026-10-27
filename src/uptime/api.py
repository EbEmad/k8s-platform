import secrets
from datetime import datetime
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field
from sqlalchemy import delete, select, text
from sqlalchemy.orm import Session

from uptime.config import settings
from uptime.db import get_session
from uptime.models import CheckResult, Monitor

app = FastAPI(title="Uptime Monitor")
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

SessionDep = Annotated[Session, Depends(get_session)]


def require_admin(authorization: Annotated[str, Header()] = "") -> None:
    if settings.admin_token and not secrets.compare_digest(
        authorization, f"Bearer {settings.admin_token}"
    ):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid or missing admin token")


class MonitorIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    url: AnyHttpUrl

class MonitorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    url: str
    created_at: datetime


class MonitorStatus(MonitorOut):
    is_up: bool | None = None
    last_checked_at: datetime | None = None
    latency_ms: float | None = None
    uptime_percent: float | None = None

def monitor_status(session: Session, monitor: Monitor, window: int = 100) -> MonitorStatus:
    recent = session.scalars(
        select(CheckResult)
        .where(CheckResult.monitor_id == monitor.id)
        .order_by(CheckResult.checked_at.desc(), CheckResult.id.desc())
        .limit(window)
    ).all()

    result=MonitorStatus.model_validate(monitor)
    if recent:
        result.is_up = recent[0].is_up
        result.last_checked_at = recent[0].checked_at
        result.latency_ms = recent[0].latency_ms
        result.uptime_percent = round(100 * sum(c.is_up for c in recent) / len(recent), 1)
    return result

def all_statuses(session: Session) -> list[MonitorStatus]:
    monitors = session.scalars(select(Monitor).order_by(Monitor.name)).all()
    return [monitor_status(session, m) for m in monitors]


@app.get("/healthz")
def healthz() -> dict[str, str]:
    """Liveness: the process is up."""
    return {"status": "ok"}

@app.get("/readyz")
def readyz(session: SessionDep) -> dict[str, str]:
    """Readiness: we can reach the database."""
    try:
        session.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "database unavailable") from exc
    return {"status": "ready"}

@app.get("/api/monitors")
def list_monitors(session: SessionDep) -> list[MonitorStatus]:
    return all_statuses(session)



@app.post(
    "/api/monitors", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)]
)
def create_monitor(payload: MonitorIn, session: SessionDep) -> MonitorOut:
    monitor = Monitor(name=payload.name, url=str(payload.url))
    session.add(monitor)
    session.commit()
    return MonitorOut.model_validate(monitor)


@app.delete(
    "/api/monitors/{monitor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
def delete_monitor(monitor_id: int, session: SessionDep) -> None:
    monitor = session.get(Monitor, monitor_id)
    if monitor is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "monitor not found")
    session.execute(delete(CheckResult).where(CheckResult.monitor_id == monitor_id))
    session.delete(monitor)
    session.commit()


@app.get("/", response_class=HTMLResponse)
def status_page(request: Request, session: SessionDep) -> HTMLResponse:
    return templates.TemplateResponse(request, "index.html", {"monitors": all_statuses(session)})




@app.get("/partials/monitors", response_class=HTMLResponse)
def monitors_partial(request: Request, session: SessionDep) -> HTMLResponse:
    return templates.TemplateResponse(
        request, "_monitors.html", {"monitors": all_statuses(session)}
    )




