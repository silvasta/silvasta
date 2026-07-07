"""
Handle CLI Event

- call printer.format

"""
# IDEA: move to __init__?? otherwise cli

from ...events.bus import Event


def handle_cli_event(event: Event):
    raise NotImplementedError
