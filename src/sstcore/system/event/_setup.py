"""
Setup the EventBus and attach Handler from defaults or provided function

                                                       DependencyLevel[2]
"""

from ...port.event import CoreEvent
from ._bus import EventBus
from ._register import BusRegistrationFunc, register_default_event_handler


def create_event_bus(
    bus_registration: BusRegistrationFunc | None = None,
    use_default_registration=True,
) -> EventBus:
    """Load EventBus explicit as one-time initialization"""

    bus = EventBus()

    if use_default_registration:
        register_default_event_handler(bus)

    if bus_registration:
        bus_registration(bus)

    bus.emit(
        event_name=CoreEvent.BUS_DIAG,
        sender="BusSetup",
        log="EventBus setup complete",
    )

    return bus
