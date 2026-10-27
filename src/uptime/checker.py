import time
from dataclasses import dataclass

import httpx

@dataclass
class CheckOutcome:
    is_up: bool
    status_code: int | None
    latency_ms: float | None
    error: str | None


async def check_url(client: httpx.AsyncClient, url: str) -> CheckOutcome:
    start = time.perf_counter()
    try:
        response = await client.get(url, follow_redirects=True)
    except httpx.HTTPError as exc:
        return CheckOutcome(False, None, None, f"{type(exc).__name__}: {exc}"[:500])
    latency_ms=round((time.perf_counter() - start) * 1000, 1)
    return CheckOutcome(response.status_code < 400, response.status_code, latency_ms, None)

