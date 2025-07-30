"""Exception classes for the Chaturbate Events API."""

from __future__ import annotations

from typing import Any


class ChaturbateEventsError(Exception):
    """Base exception for all Chaturbate Events API errors.

    Attributes:
        message: Human-readable error message
        details: Additional error details

    """

    __slots__ = ("details", "message")

    def __init__(self, message: str, *, details: dict[str, Any] | None = None) -> None:
        """Initialize the exception.

        Args:
            message (str): Human-readable error message
            details (dict[str, Any] | None): Additional error details

        """
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        """Return string representation of the exception."""
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({details_str})"
        return self.message


class APIError(ChaturbateEventsError):
    """Raised when the API returns an error response.

    Attributes:
        status_code: HTTP status code
        response_text: Raw response text

    """

    __slots__ = ("response_text", "status_code")

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        response_text: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the API error.

        Args:
            message (str): Human-readable error message
            status_code (int | None): HTTP status code
            response_text (str | None): Raw response text
            details (dict[str, Any] | None): Additional error details

        """
        super().__init__(message, details=details)
        self.status_code = status_code
        self.response_text = response_text


class AuthenticationError(APIError):
    """Raised when authentication fails."""


class NetworkError(ChaturbateEventsError):
    """Raised when network operations fail.

    Attributes:
        retry_count: Number of retries attempted
        last_error: The underlying network error

    """

    __slots__ = ("last_error", "retry_count")

    def __init__(
        self,
        message: str,
        *,
        retry_count: int = 0,
        last_error: Exception | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the network error.

        Args:
            message (str): Human-readable error message
            retry_count (int): Number of retries attempted
            last_error (Exception | None): The underlying network error
            details (dict[str, Any] | None): Additional error details

        """
        super().__init__(message, details=details)
        self.retry_count = retry_count
        self.last_error = last_error


class ConfigurationError(ChaturbateEventsError):
    """Raised when there are configuration issues."""


class ValidationError(ChaturbateEventsError):
    """Raised when data validation fails."""
