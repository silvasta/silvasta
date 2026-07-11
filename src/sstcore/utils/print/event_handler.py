"""
Handle CLI Event

- call printer.format

"""

from typing import Any

from ..view.protocol import EventProtocol
from . import printer  # WARN: printer?


def handle_cli_event(event: EventProtocol) -> None:
    """Bridge __cli__ events from EventBus to Printer"""

    target: Any = event.payload.get("target") or event.payload.get("obj")

    if target is not None:
        printer(target)  # Let the full mixin stack do its job
