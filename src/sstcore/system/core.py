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
- Active GlobalEye (similar to Passive EventBus) -> EventInterceptor
- fetch_system with custom singleton and loader (similar to config)

"""

__all__: list = [
    "System",
    "SystemLoader",
    "sst_system_loader",
    "sst_system",
    "set_global_system",
    "set_all_globals",
    "remove_all_globals",
]

from collections.abc import Callable
from pathlib import Path
from typing import Any, Self

from loguru import logger

from ..config import ConfigManager
from ..config.setup import ConfigLoader, set_global_config, sst_config_loader
from ..contract.event import CoreEvent, EventName
from ..utils import Printer
from ..utils import printer as global_printer
from ..utils.log.setup import setup_minimal_logging
from ..utils.path import HomeSetup
from .bus import EventBus
from .emit import Emitter
from .setup import BusLoader, set_global_bus, sst_bus_loader


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
        self.bus: EventBus = bus
        self.emitter = Emitter(bus=self.bus)

        printer.set_project_meta(*config.project_meta)

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
        #
        use_globals: bool = False,
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

        if use_globals:
            set_all_globals(system, config, bus)

        return system


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### setup
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


type SystemLoader = Callable[..., System]


def sst_system_loader(  # intended for user
    config_loader: ConfigLoader | None = None,
    bus_loader: BusLoader | None = None,
    printer: Printer | None = None,
    use_all_globals: bool = False,
) -> SystemLoader:
    """Prepare Loader function ready to setup System"""

    def loader(  # collected in SafeTyper
        verbose: bool = False,
        quiet: bool = False,
        setting_file: Path | None = None,
        home: HomeSetup = HomeSetup.PROJECT,
        # allow override from cli
        use_globals: bool = use_all_globals,
    ) -> System:
        system: System = System.bootstrap(
            config_loader=config_loader,
            bus_loader=bus_loader,
            printer=printer,
            verbose=verbose,
            quiet=quiet,
            setting_file=setting_file,
            home=home,
            #
            use_globals=use_globals,
        )
        return system

    return loader


_system: System | None = None


def sst_system() -> System:
    """Fetch Global System Singleton"""

    global _system
    if _system is None:
        raise RuntimeError("No access to global _system without bootstrap!")
    # TODO: emit?
    logger.debug("provide cached _system")

    return _system


def set_global_system(system: System | None) -> None:
    """Register local System as new System or replace former"""

    # TODO: emit?
    global _system
    if _system is not None:
        logger.warning(f"Replacing existing global _system: {_system!r}")

    _system = system

    if _system is None:
        logger.info("Global system set to 'None'")
    else:
        logger.info(f"New system set as global: {_system!r}")


def set_all_globals(
    system: System | None, config: ConfigManager | None, bus: EventBus | None
):
    set_global_system(system)
    set_global_config(config)
    set_global_bus(bus)


def remove_all_globals():
    set_all_globals(system=None, config=None, bus=None)
