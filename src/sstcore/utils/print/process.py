"""
Handle CLI Event

- call printer.format

"""
# IDEA: move to __init__?? otherwise cli because no printer available

from ...events.bus import Event


def handle_cli_event(event: Event):
    raise NotImplementedError
