"""
Process __log__ Event

- bind to logger and let it write the json

"""

from typing import Any

from loguru import logger

from ...events.bus import Event
from ...events.dto import LogDTO
from ...events.protocol import LogSerializable


def process_log_event(event: Event):
    """Bridges events from EventBus to Loguru"""

    target: Any = event.payload.get("target") or event.payload.get("obj")

    # Base context to inject into every log from bus
    bind_context: dict[str, Any] = {
        "sender": event.sender,
        "event_name": event.name,
    }

    if isinstance(target, LogSerializable):
        dto: LogDTO = target.__log__()
        # Bind the raw object for the formatter, plus bus context
        logger.bind(raw_obj=target, **bind_context).log(
            dto.level.upper(), dto.message
        )
    else:
        # Fallback for standard strings/dicts passing through the bus
        logger.bind(**bind_context).log(
            event.payload.get("level", "INFO").upper(),
            str(target or event.payload),
        )
