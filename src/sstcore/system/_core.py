"""
sstcore.core - Assemble the System!

Load and combine all Components in one System.

- Inject custom behaviour with System.bootstrap(kwargs)
- Wire and provide global access
                                                       DependencyLevel[2]
"""

__all__: list = [
    "System",
]

from pathlib import Path
from typing import Any, Self

from ..config import ConfigManager
from ..port.event import CoreEvent, EventName
from ..utils import Printer
from ..utils import printer as global_printer
from ..utils.log.setup import setup_minimal_logging
from ..utils.path import HomeSetup
from ._boot import BusLoader, ConfigLoader, sst_bus_loader, sst_config_loader
from .event import Emitter, EventBus


class System:
    """Combine the Essentials to work together as one System"""

    def __init__(
        self,
        config: ConfigManager,
        printer: Printer,
        bus: EventBus,
    ):
        self.config: ConfigManager = config
        self.printer: Printer = printer
        self.emitter = Emitter(bus)
        self.bus: EventBus = bus

        printer.set_project_info(*config.project_meta)

    def emit(self, event_name: EventName, sender: str, **payload: Any) -> None:
        """Provide direct bus access"""
        self.bus.emit(event_name, sender, **payload)

    @classmethod
    def bootstrap(
        cls,
        *,
        config_loader: ConfigLoader[ConfigManager] | None = None,
        bus_loader: BusLoader | None = None,
        printer: Printer | None = None,
        setting_file: Path | None = None,
        verbose: bool = False,
        quiet: bool = False,
        home: HomeSetup = HomeSetup.PROJECT,
    ) -> Self:
        """Assemble Config, wire Bus, ensure Printer and Compose to System"""

        setup_minimal_logging(level="DEBUG" if verbose else "WARNING")

        config_loader: ConfigLoader = config_loader or sst_config_loader()
        config: ConfigManager = config_loader(setting_file, home)

        config.launch_log_setup(verbose=verbose, quiet=quiet)

        bus_loader: BusLoader = bus_loader or sst_bus_loader()
        bus: EventBus = bus_loader()

        system_printer: Printer = printer or global_printer

        system: Self = cls(config=config, printer=system_printer, bus=bus)
        system.emit(event_name=CoreEvent.BUS_READY, sender="System")

        return system
