"""
Process __log__ Event

- bind event and context to logger, dump to json

"""

from typing import Any

from loguru import logger

from ...contract.log import LogDTO, LogSerializable
from ...contract.system import EventProtocol


def handle_log_event(event: EventProtocol):
    """Bridge __log__ events from EventBus to Loguru"""

    target: Any = event.payload.get("target") or event.payload.get("obj")

    bind_context: dict[str, Any] = {
        "sender": event.sender,
        "event_name": event.name,
    }
    if isinstance(target, LogSerializable):
        dto: LogDTO = target.__log__()
        logger.bind(raw_obj=target, **bind_context).log(
            dto.level.upper(), dto.message
        )
    else:
        logger.bind(**bind_context).log(
            event.payload.get("level", "INFO").upper(),
            str(target or event.payload),
        )
