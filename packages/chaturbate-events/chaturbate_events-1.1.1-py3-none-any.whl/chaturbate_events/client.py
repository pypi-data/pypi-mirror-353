"""Modern async client for the Chaturbate Events API."""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Self
from urllib.parse import parse_qs, urljoin, urlparse

import httpx

from .exceptions import APIError, AuthenticationError, ChaturbateEventsError
from .models import BaseEvent, EventMethod, EventResponse
from .utils import create_http_client, retry_with_exponential_backoff

if TYPE_CHECKING:
    from collections.abc import AsyncIterator
    from types import TracebackType

# Configure logging
logger = logging.getLogger(__name__)

# Constants
MAX_API_TIMEOUT = 90
DEFAULT_API_TIMEOUT = 10
DEFAULT_HTTP_TIMEOUT = 30.0
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 1.0
DEFAULT_MAX_CONSECUTIVE_FAILURES = 10

# Type aliases
URL = str


class ChaturbateEventsClient:  # pylint: disable=too-many-instance-attributes
    """Modern async client for the Chaturbate Events API.

    This client provides a robust interface to the Chaturbate Events API with:
    - Automatic retry logic with exponential backoff
    - Comprehensive error handling
    - Structured logging support
    - Connection pooling and timeout management
    - Event filtering and streaming capabilities
    - Context manager support for proper resource cleanup

    Examples:
        >>> async with ChaturbateEventsClient("broadcaster", "token") as client:
        ...     response = await client.get_events()
        ...     for event in response.events:
        ...         print(f"Event: {event.method}")

        >>> # Stream events continuously
        >>> async with ChaturbateEventsClient("broadcaster", "token") as client:
        ...     async for event in client.stream_events():
        ...         if event.method == EventMethod.TIP:
        ...             print(f"Tip received: {event.tip.tokens} tokens")

    """

    BASE_URL = "https://eventsapi.chaturbate.com/"
    TESTBED_URL = "https://events.testbed.cb.dev/"

    def __init__(  # noqa: PLR0913  pylint: disable=too-many-arguments
        self,
        broadcaster: str,
        api_token: str,
        *,
        testbed: bool = False,
        timeout: float = DEFAULT_HTTP_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_delay: float = DEFAULT_RETRY_DELAY,
    ) -> None:
        """Initialize the client.

        Args:
            broadcaster: The broadcaster username
            api_token: The API token for authentication
            testbed: Whether to use the testbed environment
            timeout: HTTP request timeout in seconds
            max_retries: Maximum number of retries for failed requests
            retry_delay: Base delay between retries in seconds

        """
        if not broadcaster.strip():
            msg = "Broadcaster username cannot be empty"
            raise ValueError(msg)

        if not api_token.strip():
            msg = "API token cannot be empty"
            raise ValueError(msg)

        self.broadcaster = broadcaster.strip()
        self.api_token = api_token.strip()
        self.base_url = self.TESTBED_URL if testbed else self.BASE_URL
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # Internal state
        self._client: httpx.AsyncClient | None = None
        self._next_url: URL | None = None
        self._closed = False

        logger.info(
            "Initialized client for broadcaster '%s' (testbed=%s)",
            self.broadcaster,
            testbed,
        )

    async def __aenter__(self) -> Self:
        """Async context manager entry.

        Returns:
            Self: The client instance for use in the context.

        Raises:
            RuntimeError: If attempting to reuse a closed client.

        """
        if self._closed:
            msg = "Cannot reuse a closed client"
            raise RuntimeError(msg)

        await self._ensure_client()
        logger.debug("Entered async context manager")
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Async context manager exit.

        Args:
            exc_type (type[BaseException] | None): Exception type if an exception occurred.
            exc_val (BaseException | None): Exception value if an exception occurred.
            exc_tb (TracebackType | None): Exception traceback if an exception occurred.

        """
        await self.close()
        if exc_type is not None:
            logger.error(
                "Exception occurred in async context manager: %s - %s",
                exc_type.__name__,
                str(exc_val) if exc_val else "No message",
            )

    async def _ensure_client(self) -> None:
        """Ensure the HTTP client is initialized."""
        if self._client is None or self._client.is_closed:
            self._client = create_http_client(self.timeout)
            logger.debug("HTTP client initialized")

    async def close(self) -> None:
        """Close the HTTP client and mark as closed.

        Properly closes the httpx.AsyncClient and marks the client as closed
        to prevent further usage.

        """
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()
            logger.debug("HTTP client closed")

        self._client = None
        self._closed = True

    @property
    def is_closed(self) -> bool:
        """Check if the client is closed."""
        return self._closed or (self._client is not None and self._client.is_closed)

    def _build_initial_url(self, timeout: int | None = None) -> URL:
        """Build the initial events URL with optional timeout parameter."""
        url = urljoin(self.base_url, f"events/{self.broadcaster}/{self.api_token}/")
        if timeout is not None:
            url += f"?timeout={timeout}"
        return url

    async def _handle_http_status(self, response: httpx.Response) -> None:
        """Handle specific HTTP status codes."""
        if response.status_code == httpx.codes.NOT_FOUND:
            msg = "Invalid API token or broadcaster"
            raise AuthenticationError(msg)
        if response.status_code == httpx.codes.UNAUTHORIZED:
            msg = "Broadcaster or endpoint not found"
            raise AuthenticationError(msg)
        if response.status_code == httpx.codes.FORBIDDEN:
            msg = "Access forbidden - check permissions"
            raise AuthenticationError(msg)
        if response.status_code >= httpx.codes.BAD_REQUEST:
            try:
                error_data = response.json()
                error_msg = error_data.get("error", response.text)
            except (ValueError, KeyError):
                error_msg = response.text
            msg = f"HTTP {response.status_code}: {error_msg}"
            raise APIError(msg)

    async def _parse_response(self, response: httpx.Response) -> dict[str, object]:
        """Parse and validate the JSON response."""
        try:
            data = response.json()
            logger.debug("Received response with %d events", len(data.get("events", [])))
            return dict(data)
        except (ValueError, KeyError) as e:
            msg = f"Failed to parse JSON response: {e}"
            raise APIError(msg) from e

    async def _make_request(self, url: URL) -> dict[str, object]:
        """Make an HTTP request with retry logic."""
        await self._ensure_client()

        if not self._client or self._client.is_closed:
            msg = "HTTP client is not initialized or has been closed"
            raise ChaturbateEventsError(msg)

        async def _do_request() -> dict[str, object]:
            logger.debug("Making HTTP request: %s", url)
            response = await self._client.get(url)  # type: ignore[union-attr]
            await self._handle_http_status(response)
            return await self._parse_response(response)

        return await retry_with_exponential_backoff(
            _do_request,
            max_retries=self.max_retries,
            base_delay=self.retry_delay,
        )

    async def get_events(
        self, api_timeout: int | None = None, *, use_next_url: bool = True
    ) -> EventResponse:
        """Get the next batch of events.

        Args:
            api_timeout: Server timeout in seconds (0-90, default: 10)
            use_next_url: Whether to use the stored next_url from previous requests

        Returns:
            EventResponse containing events and next URL

        """
        if api_timeout is not None and not 0 <= api_timeout <= MAX_API_TIMEOUT:
            msg = "Timeout must be between 0 and 90 seconds"
            raise ValueError(msg)

        if use_next_url and self._next_url:
            url = self._next_url
            # Override timeout in existing URL if provided
            if api_timeout is not None:
                parsed = urlparse(url)
                query_params = parse_qs(parsed.query)
                query_params["timeout"] = [str(api_timeout)]
                query_string = "&".join(f"{k}={v[0]}" for k, v in query_params.items())
                url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{query_string}"
        else:
            url = self._build_initial_url(api_timeout)

        data = await self._make_request(url)
        response = EventResponse.model_validate(data)
        self._next_url = response.next_url
        return response

    async def stream_events(
        self,
        api_timeout: int | None = None,
        event_filter: set[EventMethod] | None = None,
        max_consecutive_failures: int = 10,
    ) -> AsyncIterator[BaseEvent]:
        """Stream events continuously.

        Args:
            api_timeout: Server timeout for each request (0-90, default: 10)
            event_filter: Set of event methods to filter for (default: None for all)
            max_consecutive_failures: Max consecutive failures before giving up

        Yields:
            Individual Event objects as they arrive

        """
        consecutive_failures = 0

        while True:
            try:
                response = await self.get_events(api_timeout=api_timeout)
                consecutive_failures = 0  # Reset on successful request

                for event in response.events:
                    if event_filter is None or event.method in event_filter:
                        yield event

            except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError) as e:
                consecutive_failures += 1
                if consecutive_failures >= max_consecutive_failures:
                    msg = f"Too many consecutive network failures ({consecutive_failures})"
                    raise ChaturbateEventsError(msg) from e

                logger.exception("Network error while streaming events, retrying...")
                await asyncio.sleep(self.retry_delay * min(consecutive_failures, 5))
                continue

    def reset_stream(self) -> None:
        """Reset the stream to start from the beginning."""
        self._next_url = None
