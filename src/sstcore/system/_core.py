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

from typing import TYPE_CHECKING, Any, Self, Unpack

from ..port.config import Config
from ..port.event import EventBus as EventBus
from ..port.event.emit import Emitter as Emitter_
from ..port.event.name import CoreEvent, EventName
from ..port.printer import Printer
from ..port.system import (
    BusLoader,
    ConfigLoader,
    SstSystem,
    SystemCliArgs,
    SystemCliInput,
)
from ..port.system import System as System_
from ..util.log import setup_minimal_logging
from ..util.print import printer as global_printer
from .config import ConfigManager
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
        self.emitter: Emitter_ = Emitter(self.bus)  # ty:ignore

    def emit(self, event: EventName, sender: str, **payload: Any) -> None:
        """Provide direct bus access"""
        self.bus.emit(event, sender, **payload)

    @classmethod
    def boot(
        cls,
        *,
        config_loader: ConfigLoader | None = None,
        bus_loader: BusLoader | None = None,
        printer: Printer | None = None,
        **cli_args: Unpack[SystemCliArgs],
    ) -> Self:
        """Assemble Config, wire Bus, ensure Printer and launch the System"""

        args = SystemCliInput(**cli_args)  # LATER: with cast.args decorator

        setup_minimal_logging(level="DEBUG" if args.verbose else "WARNING")

        config_loader: ConfigLoader = config_loader or ConfigManager.bootstrap
        config: Config = config_loader(
            setting_file=args.settings, home_setup=args.home
        )

        config.launch_log_setup(verbose=args.verbose, quiet=args.quiet)

        bus_loader: BusLoader = bus_loader or Bus.ready
        bus: EventBus = bus_loader()

        system_printer: Printer = printer or global_printer
        system_printer.set_info(config.project_info)

        system: Self = cls(config=config, printer=system_printer, bus=bus)
        system.emit(event=CoreEvent.BUS_READY, sender="System")

        return system


if TYPE_CHECKING:
    # base protocol
    _instance_check: System_ = System.boot()
    _class_check: type[System_] = System
    # only internals
    _instance_check: SstSystem = System.boot()
    _class_check: type[SstSystem] = System
