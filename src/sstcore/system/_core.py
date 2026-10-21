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

from dataclasses import asdict
from typing import Any, Self, Unpack

from ..port import CliSystem
from ..port.config import Config
from ..port.event import EventBus
from ..port.event.emit import Emitter
from ..port.event.name import CoreEvent, EventName
from ..port.link import portlink
from ..port.printer import Printer
from ..port.system import (
    BusLoader,
    ConfigLoader,
    SstSystem,
    SystemBootData,
    SystemBootParam,
)
from ..util.log import setup_minimal_logging
from ..util.print import PrinterFactory
from .config import ConfigManager
from .event import Bus, EmitCore


@portlink(CliSystem)
@portlink(SstSystem)
class System:
    """Combine the Essentials to work together as one System"""

    def __init__(self, bus: EventBus, config: Config, printer: Printer):
        self.bus: EventBus = bus
        self.config: Config = config
        self.printer: Printer = printer
        self.emitter: Emitter = EmitCore(self.bus)  # ty:ignore

    def emit(self, event: EventName, sender: str, **payload: Any) -> None:
        """Provide direct bus access"""
        self.bus.emit(event, sender, **payload)

    @classmethod
    def boot(cls, **data: Unpack[SystemBootParam]) -> Self:
        """Assemble Config, wire Bus, ensure Printer and launch the System"""

        param = SystemBootData(**data)

        setup_minimal_logging(level="DEBUG" if param.verbose else "WARNING")

        loader: ConfigLoader = param.config_loader or ConfigManager.bootstrap
        config: Config = loader(**asdict(param.cli_data))
        config.launch_log_setup(verbose=param.verbose, quiet=param.quiet)

        bus_loader: BusLoader = param.bus_loader or Bus.ready
        bus: EventBus = bus_loader()

        printer: Printer = param.printer or PrinterFactory.make()
        printer.info = config.project_info

        system: Self = cls(config=config, printer=printer, bus=bus)
        system.emit(event=CoreEvent.BUS_READY, sender="System")

        return system
