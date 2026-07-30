"""
sstcore.core - Assemble the System!

Load and combine all singletons in one System.

- Use System.bootstrap(*custom_loaders*) for Non-Global Instance

- Inject custom behaviour with System.bootstrap(kwargs)

Zero effort access for scripts and small projects:
- Initialize Global singleton: System.bootstrap(use_globals=True)
- Access everywhere without wiring with sst_system()

Warning:
- Don't Mix both approaches except you know exactly what you are doing!

Ideas:
- Active global eye (similar to Passive EventBus) -> EventInterceptor

                                                       DependencyLevel[1]
"""

__all__: list = [
    "System",
    "SystemLoader",
    "sst_system_loader",
]

from collections.abc import Callable
from pathlib import Path
from typing import Any, Self

from ..config import ConfigManager
from ..port.event import CoreEvent, EventName
from ..utils import Printer
from ..utils import printer as global_printer
from ..utils.log.setup import setup_minimal_logging
from ..utils.path import HomeSetup
from .boot import BusLoader, ConfigLoader, sst_bus_loader, sst_config_loader
from .event import Emitter, EventBus

type SystemLoader = Callable[..., System]


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


# AI: so far not bad, still this loader together with the others would be nice,
# bot looks impossible as the System always needs the other loader,
# and the loader below always needs the system before...
# (some TYPE_CHECKING hacks are fine for the globals, probably not for the main system)
def sst_system_loader(  # intended for user project configs
    config_loader: ConfigLoader | None = None,
    bus_loader: BusLoader | None = None,
    printer: Printer | None = None,
) -> SystemLoader:
    """Prepare Loader function ready to setup System"""

    def loader(  # intended for cli or any other runtime override
        verbose: bool = False,
        quiet: bool = False,
        setting_file: Path | None = None,
        home: HomeSetup = HomeSetup.PROJECT,
    ) -> System:
        system: System = System.bootstrap(
            config_loader=config_loader,
            bus_loader=bus_loader,
            printer=printer,
            verbose=verbose,
            quiet=quiet,
            setting_file=setting_file,
            home=home,
        )

        return system

    return loader
