# Chaturbate Events

Python wrapper for the Chaturbate Events API.

## Features

- Stream events in real-time
- Type-safe with Pydantic models
- Async/await support
- Event filtering
- Built-in retry logic

## Installation

```bash
pip install chaturbate-events
```

## Quick Start

```python
import asyncio
from chaturbate_events import ChaturbateEventsClient, TipEvent

async def main():
    async with ChaturbateEventsClient("username", "api_token") as client:
        async for event in client.stream_events():
            if isinstance(event, TipEvent):
                print(f"{event.user.username} tipped {event.tip.tokens} tokens")

asyncio.run(main())
```

## Event Types

Supported events:

- `TipEvent` - When someone tips tokens
- `ChatMessageEvent` / `PrivateMessageEvent` - Chat messages  
- `UserEnterEvent` / `UserLeaveEvent` - People joining or leaving
- `FollowEvent` / `UnfollowEvent` - New followers
- `FanclubJoinEvent` - Fanclub joins
- `MediaPurchaseEvent` - Media purchases
- `BroadcastStartEvent` / `BroadcastStopEvent` - Stream start/stop
- `RoomSubjectChangeEvent` - Topic changes

## Usage Examples

### Listen to all events
```python
async with ChaturbateEventsClient("broadcaster", "token") as client:
    async for event in client.stream_events():
        print(f"{event.method} from {event.user.username}")
```

### Only listen for specific events
```python
events = {EventMethod.TIP, EventMethod.CHAT_MESSAGE}
async for event in client.stream_events(event_filter=events):
    # Only tips and chat messages will come through
    pass
```

### Configuration
```python
client = ChaturbateEventsClient(
    broadcaster="username",
    api_token="token",
    testbed=False,        # Use production (set to True for testing)
    timeout=30.0,         # Connection timeout in seconds
    max_retries=3         # How many times to retry failed connections
)
```

## Requirements

- Python 3.12+
- Chaturbate API token

## Development

```bash
pip install -e ".[dev]"
pytest
ruff format && ruff check
```

## License

MIT License - see [LICENSE](LICENSE) file for details.