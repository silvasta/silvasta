"""
sstcore.core - Assemble the System!

Load and combine all Components in one System.

- Inject custom behaviour with System.bootstrap(cli_args)
- Wire and provide global access
                                                       DependencyLevel[2]??
"""

__all__: list = [
    "System",
]

from typing import Any, Self, Unpack

from ..port.config import Config
from ..port.event import EventBus
from ..port.event.emit import Emitter
from ..port.event.name import CoreEvent, EventName
from ..port.link import portlink
from ..port.printer import Print
from ..port.system import (
    BusLoader,
    CliSystem,
    ConfigLoader,
    SstSystem,
    SystemBootParam,
    SystemBootSpec,
)
from ..util.log import setup_minimal_logging
from ..util.print import printer as _printer
from .config import ConfigManager
from .event import Bus, EmitCore


@portlink(CliSystem)
@portlink(SstSystem)
class System:
    """Combine the Essentials to work together as one System"""

    def __init__(self, bus: EventBus, config: Config, printer: Print):
        self.bus: EventBus = bus
        self.config: Config = config
        self.printer: Print = printer
        self.emitter: Emitter = EmitCore(self.bus)  # ty:ignore

    def emit(self, event: EventName, sender: str, **payload: Any) -> None:
        """Provide direct bus access"""
        self.bus.emit(event, sender, **payload)

    @classmethod
    def boot(cls, **data: Unpack[SystemBootParam]) -> Self:
        """Assemble Config, wire Bus, ensure Print and launch the System"""

        param = SystemBootSpec(**data)

        setup_minimal_logging(level="DEBUG" if param.verbose else "WARNING")

        loader: ConfigLoader = param.config_loader or ConfigManager.bootstrap
        config: Config = loader(**param.cli_data.config_input)
        config.launch_log_setup(verbose=param.verbose, quiet=param.quiet)

        bus_loader: BusLoader = param.bus_loader or Bus.ready
        bus: EventBus = bus_loader()

        printer: Print = param.printer or _printer
        printer.info = config.project_info

        system: Self = cls(config=config, printer=printer, bus=bus)
        system.emit(event=CoreEvent.BUS_READY, sender="System")

        return system
