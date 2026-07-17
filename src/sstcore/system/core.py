"""
sstcore.core - Assemble the System!

Load and combine all singletons in one System.

- Use System.bootstrap() for Non-Global Instance

- Inject custom behaviour with System.bootstrap(kwargs)

Zero effort access for scripts and small projects:
- Initialize Global singleton: fetch_system(_allow_uninitialized=False)
- Access everywhere without wiring with fetch_system()

Warning:
- Don't Mix both approaches except you know exactly what you are doing!

Note:
- This module will likely transform to a package with core.system module

Ideas:
- Active GlobalEye (similar to Passive EventBus) -> EventInterceptor
- fetch_system with custom singleton and loader (similar to config)

"""

__all__: list = [
    "System",
    "fetch_system",
]
from pathlib import Path
from typing import Any, Self

from ..config import ConfigManager
from ..config.setup import ConfigLoader, sst_config_loader
from ..utils import Printer
from ..utils import printer as global_printer
from ..utils.log import LogSetupResult
from ..utils.log.setup import setup_logging, setup_minimal_logging
from .event_bus import EventBus
from .register import BusRegistrationFunc, register_default_event_handler


# NEXT: name
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
    """Combine the Essentials to work together as System"""

    def __init__(
        self,
        config: ConfigManager,
        printer: Printer,
        bus: EventBus,
    ):
        self.config: ConfigManager = config
        self.printer: Printer = printer
        self.bus: EventBus = bus

        # TODO: function of printer? printer.set_...
        self.printer.project_name = config.project_name
        self.printer.project_version = config.project_version

    @classmethod
    def bootstrap(
        cls,
        *,
        config_loader: ConfigLoader | None = None,
        setting_file: Path | None = None,
        use_default_bus_handler: bool = True,
        attach: BusRegistrationFunc | None = None,
        printer: Printer | None = None,
        verbose: bool = False,
        quiet: bool = False,
    ) -> Self:
        """Assemble Config, wire Bus, ensure Printer and Compose to System"""

        # shadow bootstrap noise but show minimal output if bootstrap fails
        setup_minimal_logging("DEBUG" if verbose else "WARNING")

        loader: ConfigLoader = config_loader or sst_config_loader
        # create global singleton with sst_config_loader
        config: ConfigManager = loader(setting_file)

        log_result: LogSetupResult = setup_logging(
            log_level_override="DEBUG" if verbose else None,
            quiet=quiet,
            param=config.settings.log,
            # TODO: where to print? emit print+log here? check scroll
        )
        config.log_result = log_result  # LATER: better attach

        bus = EventBus()  # obviously no singleton, what if ever needed?
        if use_default_bus_handler:
            register_default_event_handler(bus)
        if attach:  # BusRegistrationFunc
            attach(bus)

        system_printer: Printer = printer or global_printer
        # printer (so far) always exists as (stateles) global singleton

        system: Self = cls(config=config, printer=system_printer, bus=bus)
        system.emit(event_name="sys.log", sender="System", msg="Setup Ready!")

        return system

    def emit(self, event_name: str, sender: str, **payload: Any) -> None:
        """Increase convenience for bus access"""
        self.bus.emit(event_name, sender, **payload)
