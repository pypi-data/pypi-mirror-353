"""Chaturbate Events API Python wrapper.

A modern, type-safe Python client for the Chaturbate Events API with:
- Async/await support with proper resource management
- Comprehensive type hints and validation
- Robust error handling and retry logic
- Structured logging and debugging support
- Event filtering and streaming capabilities

Examples:
    Basic usage:
        >>> import asyncio
        >>> from chaturbate_events import ChaturbateEventsClient
        >>>
        >>> async def main():
        ...     async with ChaturbateEventsClient("broadcaster", "token") as client:
        ...         response = await client.get_events()
        ...         for event in response.events:
        ...             print(f"Event: {event.method}")
        >>>
        >>> asyncio.run(main())

    Event streaming:
        >>> async def stream_events():
        ...     async with ChaturbateEventsClient("broadcaster", "token") as client:
        ...         async for event in client.stream_events():
        ...             if event.method == "tip":
        ...                 print(f"Tip: {event.tip.tokens} tokens")
        >>>
        >>> asyncio.run(stream_events())

"""

import importlib.metadata

from .client import ChaturbateEventsClient
from .exceptions import (
    APIError,
    AuthenticationError,
    ChaturbateEventsError,
    ConfigurationError,
    NetworkError,
    ValidationError,
)
from .models import (
    BaseEvent,
    BroadcastStartEvent,
    BroadcastStopEvent,
    ChatMessageEvent,
    ColorGroup,
    Event,
    EventMethod,
    EventResponse,
    FanclubJoinEvent,
    FollowEvent,
    Gender,
    Media,
    MediaPurchaseEvent,
    Message,
    PrivateMessageEvent,
    RecentTips,
    RoomSubjectChangeEvent,
    SubGender,
    Tip,
    TipEvent,
    UnfollowEvent,
    User,
    UserEnterEvent,
    UserLeaveEvent,
)

__version__ = importlib.metadata.version(distribution_name="chaturbate_events")
__author__ = "MountainGod2"
__author_email__ = "admin@reid.ca"
__maintainer__ = "MountainGod2"
__maintainer_email__ = "admin@reid.ca"
__license__ = "MIT"
__url__ = "https://github.com/MountainGod2/chaturbate_events"
__description__ = "Chaturbate Events API Python wrapper."

__all__ = [
    # Exceptions
    "APIError",
    "AuthenticationError",
    # Models
    "BaseEvent",
    # Event Types
    "BroadcastStartEvent",
    "BroadcastStopEvent",
    "ChatMessageEvent",
    # Client
    "ChaturbateEventsClient",
    "ChaturbateEventsError",
    # Enums
    "ColorGroup",
    "ConfigurationError",
    "Event",
    "EventMethod",
    "EventResponse",
    "FanclubJoinEvent",
    "FollowEvent",
    "Gender",
    "Media",
    "MediaPurchaseEvent",
    "Message",
    "NetworkError",
    "PrivateMessageEvent",
    "RecentTips",
    "RoomSubjectChangeEvent",
    "SubGender",
    "Tip",
    "TipEvent",
    "UnfollowEvent",
    # Data Models
    "User",
    "UserEnterEvent",
    "UserLeaveEvent",
    "ValidationError",
]
