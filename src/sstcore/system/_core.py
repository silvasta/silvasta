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
from typing import TYPE_CHECKING, Any, Self

from ..config import ConfigManager, HomeSetup
from ..port.config import Config
from ..port.event import EventBus as EventBus
from ..port.event.name import CoreEvent, EventName
from ..port.printer import Printer
from ..port.system import BusLoader, CliSystem, ConfigLoader, SstSystem
from ..port.system import System as System_
from ..utils.log import setup_minimal_logging
from ..utils.print import printer as global_printer
from .event import Emitter
from .event import EventBus as Bus


class System:
    """Combine the Essentials to work together as one System"""

    def __init__(
        self,
        bus: EventBus,
        config: Config,
        printer: Printer,
    ):
        self.bus: EventBus = bus
        self.config: Config = config
        self.printer: Printer = printer
        self.emitter = Emitter(self.bus)

    def emit(self, event: EventName, sender: str, **payload: Any) -> None:
        """Provide direct bus access"""
        self.bus.emit(event, sender, **payload)

    @classmethod
    def bootstrap(
        cls,
        *,
        config_loader: ConfigLoader | None = None,
        bus_loader: BusLoader | None = None,
        # WARN: printer empty!
        printer: Printer | None = None,
        settings: Path | None = None,
        verbose: bool = False,
        quiet: bool = False,
        home: HomeSetup = HomeSetup.PROJECT,
    ) -> Self:
        """Assemble Config, wire Bus, ensure Printer and Compose to System"""

        setup_minimal_logging(level="DEBUG" if verbose else "WARNING")

        config_loader: ConfigLoader = config_loader or ConfigManager.bootstrap
        config: Config = config_loader(setting_file=settings, home_setup=home)

        config.launch_log_setup(verbose=verbose, quiet=quiet)

        bus_loader: BusLoader = bus_loader or Bus.bootstrap
        bus: EventBus = bus_loader()

        system_printer: Printer = printer or global_printer
        system_printer.set_project_info(config.project_info)

        system: Self = cls(config=config, printer=system_printer, bus=bus)
        system.emit(event=CoreEvent.BUS_READY, sender="System")

        return system


if TYPE_CHECKING:
    # base protocol
    _instance_check: System_ = System.bootstrap()
    _class_check: type[System_] = System
    # only internals
    _instance_check: SstSystem = System.bootstrap()
    _class_check: type[SstSystem] = System
    # with externals (current implementation)
    _instance_check: CliSystem = System.bootstrap()
    _class_check: type[CliSystem] = System
