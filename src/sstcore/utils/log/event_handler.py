"""
Process __log__ Event

- bind event and context to logger, dump to json

"""

from typing import Any

from loguru import logger

from ...contract.event import Event
from ...contract.log import LogDTO, LogSerializable

# AI_TASK: find at least 1 proper handler setup, maybe somme options
# - the "log" in payload and early return is important for the new strategy
# - still the dispatch and bind of the inital handler should be considered


def handle_log_event(event: Event):
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


# NEXT: handle log
# NEXT: handle log
# NEXT: handle log


def _handle_log_event(event: Event) -> None:
    log = event.payload.get("log")
    if log is None:
        return  # # IMPORTANT:
    logger.opt(depth=...).log(
        log.level,
        "{sender} | {name} | {message}",
        sender=event.sender,
        name=event.name,
        message=log.message,
    )
    # optional: bind log.extra
