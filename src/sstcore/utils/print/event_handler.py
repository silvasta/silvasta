"""Handle __cli__ Event"""

from typing import Any

from ...contract.event import Event
from .compose import printer


def handle_cli_event(event: Event) -> None:
    """Bridge __cli__ events from the EventBus to the Printer"""

    cli_payload: Any | None = event.payload.get("cli")

    if cli_payload is None:
        return

    # TODO: hand in printer from bootstrap
    printer(cli_payload)
