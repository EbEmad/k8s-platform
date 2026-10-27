import asyncio
import logging
from dataclasses import asdict

import httpx
from sqlalchemy import select

from uptime.checker import check_url
from uptime.config import settings
from uptime.db import SessionLocal
from uptime.models import CheckResult, Monitor

log = logging.getLogger("uptime.worker")


async def run_once(client: httpx.AsyncClient) -> int:
    with SessionLocal() as session:
        monitors = session.scalars(select(Monitor)).all()

    outcomes = await asyncio.gather(*(check_url(client, m.url) for m in monitors))

    with SessionLocal() as session:
        for monitor, outcome in zip(monitors, outcomes, strict=True):
            session.add(CheckResult(monitor_id=monitor.id, **asdict(outcome)))
            log.info("%s %s -> %s", "UP  " if outcome.is_up else "DOWN", monitor.url, outcome)
        session.commit()
    return len(monitors)


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    log.info("worker started, interval=%ss", settings.check_interval_seconds)
    async with httpx.AsyncClient(
        timeout=settings.check_timeout_seconds, headers={"User-Agent": "uptime-monitor/0.1"}
    ) as client:
        while True:
            try:
                count = await run_once(client)
                log.info("checked %d monitors", count)
            except Exception:
                log.exception("check cycle failed")
            await asyncio.sleep(settings.check_interval_seconds)


if __name__ == "__main__":
    asyncio.run(main())