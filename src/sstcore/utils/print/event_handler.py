"""Handle __cli__ Event"""

from typing import Any

from ...contract.event import Event
from .compose import printer

# AI_TASK: find at least 1 proper handler setup, maybe somme options
# - the "cli" in payload and early return is important for the new strategy
# - still the printer usage (more detaild in print.core) should be considered


def handle_cli_event(event: Event) -> None:
    """Bridge __cli__ events from EventBus to Printer"""
    # LATER: inject printer?

    target: Any = event.payload.get("target") or event.payload.get("obj")

    if target is not None:
        printer(target)  # Let the full mixin stack do its job


# NEXT: handle cli
# NEXT: handle cli
# NEXT: handle cli


# handle_cli_event
def _handle_cli_event(event: Event) -> None:
    cli = event.payload.get("cli")
    if cli is None:
        return  # IMPORTANT:
    printer.render_dto(cli)  # FAIL:
