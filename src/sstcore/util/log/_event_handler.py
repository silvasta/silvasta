"""
Handle __log__: Event Bridge to Loguru

                                                       DependencyLevel[0]
"""

__all__: list[str] = [
    "handle_log_event",
]

from typing import TYPE_CHECKING, Any

from loguru import logger

from ...port.event import Event, EventHandler
from ...port.event.dto import LogDTO
from ...port.view import LogSerializable


def handle_log_event(event: Event) -> None:
    # TODO: this directly with Functor
    """Process payload['log'] only; no-op for every other event."""

    log_payload: Any | None = event.payload.get("log")

    if log_payload is None:
        return

    if not isinstance(log_payload, LogSerializable):
        logger.bind(
            event_name=event.name,
            sender=event.sender,
        ).warning(
            "bus expected LogSerializable with log=... got {type}",
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
    ).log(dto.level.upper(), dto.message)


if TYPE_CHECKING:
    _func_check: EventHandler = handle_log_event
