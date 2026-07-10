"""
Assemble the System!

- Load and combine all global instances in 1 System

"""

from pathlib import Path
from typing import Any, Self

from loguru import logger

from sstcore.utils.log import LogSetupResult

from .config import ConfigManager
from .config.setup import ConfigLoader, sst_config_loader
from .events import BusRegistrationFunc, EventBus
from .events.register import register_default_event_handler
from .utils import Printer, printer, setup_logging
from .utils.log.setup import setup_minimal_logging


def fetch_system(*, _allow_uninitialized: bool = False) -> System:
    global _system
    if _system is None:
        if _allow_uninitialized:
            _system = System.bootstrap()
        else:
            raise RuntimeError("System not bootstrapped")
    return _system


_system: System | None = None


class System:
    """Hold the EventBus and related components"""

    def __init__(self, config: ConfigManager, printer: Printer, bus: EventBus):
        self.config: ConfigManager = config
        self.printer: Printer = printer
        self.bus: EventBus = bus

        self.printer.project_name = config.project_name
        self.printer.project_version = config.project_version

    @classmethod
    def bootstrap(
        cls,
        config_loader: ConfigLoader | None = None,
        setting_file: Path | None = None,
        verbose: bool = False,
        quiet: bool = False,
        use_default_bus_handler: bool = True,
        attach: BusRegistrationFunc | None = None,
        custom_printer: Printer | None = None,
    ) -> Self:
        """Assemble the EventBus and other components to the EventSystem"""

        # shadow bootstap noise but show minimal output if bootstap fails
        setup_minimal_logging("DEBUG" if verbose else "WARNING")

        loader: ConfigLoader = config_loader or sst_config_loader
        # create global singleton with sst_config_loader
        config: ConfigManager = loader(setting_file)

        log_result: LogSetupResult = setup_logging(
            log_level_override="DEBUG" if verbose else None,
            quiet=quiet,
            param=config.settings.log,
        )
        config.log_result = log_result  # LATER: better attach

        bus = EventBus()  # obviously no singleton, what if ever needed?
        if use_default_bus_handler:
            register_default_event_handler(bus)
        if attach:  # BusRegistrationFunc
            attach(bus)

        used_printer: Printer = custom_printer or printer
        # printer (so far) always exists as (stateles) global singleton

        system: Self = cls(config=config, printer=used_printer, bus=bus)
        # TODO: use the bus!
        logger.info(f"System ready for {printer.name_and_version}")

        return system

    def emit(self, event_name: str, sender: str, **payload: Any) -> None:
        """Increase convenience for bus access"""
        self.bus.emit(event_name, sender, **payload)
