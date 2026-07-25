"""
Process __log__ Event

- bind event and context to logger, dump to json

"""

from typing import Any

from loguru import logger

from ...contract.event import Event
from ...contract.log import LogDTO, LogSerializable


def handle_log_event(event: Event) -> None:
    """Process payload['log'] only; no-op for every other event."""

    log_payload: Any | None = event.payload.get("log")

    if log_payload is None:
        return

    if not isinstance(log_payload, LogSerializable):
        logger.bind(
            event_name=event.name,
            sender=event.sender,
        ).warning(
            "bus log= expected LogSerializable, got {type}",
            type=type(log_payload).__name__,
        )
        return

    dto: LogDTO = log_payload.__log__()

    logger.bind(
        log_payload_obj=log_payload,
        event_name=event.name,
        sender=event.sender,
        **dto.metrics,
        **dto.extra,
        # AI_QUESTION: ok I see the message and level are in the last block,
        # but the others, metrics,extras in the first.
        # - Briefly summarize the purpose of both,
        #   which critera decide what comes where?
    ).log(dto.level.upper(), dto.message)
