"""Utility functions for the Chaturbate Events API client."""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, TypeVar

import httpx

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

logger = logging.getLogger(__name__)

T = TypeVar("T")


async def retry_with_exponential_backoff(
    func: Callable[[], Awaitable[T]],
    max_retries: int = 3,
    base_delay: float = 1.0,
    exceptions: tuple[type[Exception], ...] = (httpx.HTTPError,),
) -> T:
    """Retry a function with exponential backoff."""
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            return await func()
        except exceptions as e:
            last_exception = e
            if attempt < max_retries:
                delay = base_delay * (2**attempt)
                logger.warning(
                    "Retry attempt %d/%d failed, waiting %.2fs: %s",
                    attempt + 1,
                    max_retries + 1,
                    delay,
                    str(e),
                )
                await asyncio.sleep(delay)
                continue
            break

    if last_exception:
        raise last_exception

    msg = "Retry logic failed unexpectedly"
    raise RuntimeError(msg)


def create_http_client(timeout: float = 30.0) -> httpx.AsyncClient:
    """Create a configured HTTP client."""
    timeout_config = httpx.Timeout(
        connect=5.0,
        read=timeout,
        write=10.0,
        pool=5.0,
    )

    return httpx.AsyncClient(
        timeout=timeout_config,
        follow_redirects=True,
        limits=httpx.Limits(
            max_keepalive_connections=10,
            max_connections=100,
            keepalive_expiry=30.0,
        ),
        headers={
            "User-Agent": "chaturbate-events-python/1.0",
            "Accept": "application/json",
        },
    )
