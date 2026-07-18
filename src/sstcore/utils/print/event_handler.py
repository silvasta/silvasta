"""Handle __cli__ Event"""

from typing import Any

from ...contract.event import Event
from .compose import printer


def handle_cli_event(event: Event) -> None:
    """Bridge __cli__ events from EventBus to Printer"""
    # LATER: inject printer?

    target: Any = event.payload.get("target") or event.payload.get("obj")

    if target is not None:
        printer(target)  # Let the full mixin stack do its job
