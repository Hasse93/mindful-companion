"""Rate limiting as a FastAPI dependency (backed by the `limits` library).

Protects the Gemini quota (chat) and slows account-spam / brute-force (auth).
In-memory storage is fine for the single Hugging Face Space instance. Keyed by
the real client IP (X-Forwarded-For behind the HF proxy). Disabled in tests via
RATE_LIMIT_ENABLED=false.

Usage:
    @router.post("", dependencies=[Depends(rate_limit("15/minute"))])
"""
from __future__ import annotations

from collections.abc import Callable

from fastapi import HTTPException, Request, status
from limits import parse
from limits.storage import MemoryStorage
from limits.strategies import FixedWindowRateLimiter

from app.config import get_settings

_limiter = FixedWindowRateLimiter(MemoryStorage())


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "anon"


def rate_limit(limit: str) -> Callable[[Request], None]:
    """Build a dependency that allows `limit` (e.g. "15/minute") per client IP."""
    item = parse(limit)

    def dependency(request: Request) -> None:
        if not get_settings().rate_limit_enabled:
            return
        if not _limiter.hit(item, _client_ip(request)):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests — please slow down and try again shortly.",
            )

    return dependency
