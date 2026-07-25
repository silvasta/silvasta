```py
"""
Wire the Event Infrastructure.

- Provide EventBus with loader, handler and if needed, global access

"""  # TODO: adapt, move to Bus

__all__: list[str] = [
    "System",
    "EventBus",
    "EventHandler",
    "BusRegistrationFunc",
    "sst_bus",
    "EmitFunctor",
    "Emitter",
]


from .bus import EventBus, EventHandler
from .core import System
from .emit import EmitFunctor, Emitter
from .register import BusRegistrationFunc
from .setup import sst_bus
```

```py
"""
Provide Infrastructure for Events

- EventBus: Route Events by name to registred EventHandler
- EventHandler: Process Event with optional Error handling

"""

__all__: list[str] = [
    "EventBus",
    "EventHandler",
]

import fnmatch
from collections.abc import Callable
from dataclasses import dataclass
from functools import lru_cache

from loguru import logger

from ..contract.event import Event, EventName, EventPattern


@dataclass(frozen=True)
class EventHandler:
    """Process Events emmited from the bus in observable Environment"""

    name: str
    func: Callable[[Event], None]
    fail_loud: bool = False

    def __str__(self) -> str:
        return f"EventHandler[{self.name}]"

    # LATER: think about generic
    # - synchronize with ErrorHandler

    def __call__(self, event: Event) -> None:
        """Execute handler function and manage fail if flag is set"""
        try:
            self.func(event)
        except Exception as error:
            if self.fail_loud:  # LATER: custom error?
                raise RuntimeError(f"Critical Fail: {self}") from error

            logger.error(f"{self} failed for '{event.name}': {error}")
            logger.debug(f"Traceback for {self}:", exc_info=True)


class EventBus:
    """Enable decoupled state propagation for synchronous Events"""

    def __init__(self) -> None:
        self._subscribers: dict[EventPattern, list[EventHandler]] = {}
        self._global_subscribers: list[EventHandler] = []

    def emit(self, event_name: EventName, sender: str, **payload) -> None:
        """Fire an Event to all global and event-specific subscribers"""

        event = Event(name=event_name, sender=sender, payload=payload)

        for handler in self._global_subscribers:
            handler(event)

        for handler in self._match_subscribers(event_name):
            handler(event)

    def subscribe(self, name: EventPattern, handler: EventHandler) -> None:
        """Attach handler as subscriber to specific event"""
        self._subscribers.setdefault(name, []).append(handler)

    def subscribe_all(self, handler: EventHandler) -> None:
        """Attach global handler as subscriber to all events"""
        self._global_subscribers.append(handler)

    @property
    def n_handler(self) -> int:
        return len(self._subscribers)

    @property
    def n_global_handler(self) -> int:
        return len(self._global_subscribers)

    def __str__(self) -> str:
        return type(self).__name__

    def __repr__(self) -> str:  # TEST:
        return f"{self}(  {self.n_global_handler} 󰌌 {self.n_handler} 󰍹 )"

    def _match_subscribers(
        self, event_name: EventName
    ) -> tuple[EventHandler, ...]:
        """Filter subscribers by event name and wildcard pattern"""

        subscribers: tuple[EventPattern, ...] = tuple(self._subscribers.keys())

        matched_handlers: list[EventHandler] = [
            handler
            for pattern in _get_patterns(event_name, subscribers)
            for handler in self._subscribers[pattern]
        ]

        return tuple(dict.fromkeys(matched_handlers))


@lru_cache(maxsize=256)
def _get_patterns(
    event_name: EventName, active_patterns: tuple[EventPattern, ...]
) -> tuple[EventPattern, ...]:
    """Match pattern and cache results decoupled from the Bus"""
    return tuple(
        pattern
        for pattern in active_patterns
        if fnmatch.fnmatch(event_name, pattern)
    )
```

```py
"""
Hold and prepare Global Singleton EventBus instance.

- Provide protected access to initial setup (unlock with flag)
- Prepare ready-to-use loader for CLI, or any other purpose
- Handle infrastructure for project setups with custom loader
- Expose global Singleton: `bus: EventBus = sst_bus()`

"""

from sstcore.contract.event import CoreEvent

__all__: list[str] = [
    "BusLoader",
    "sst_bus_loader",
    "sst_bus",
    "create_event_bus",
    "set_global_bus",
]
from collections.abc import Callable

from loguru import logger

from .bus import EventBus
from .register import BusRegistrationFunc, register_default_event_handler

type BusLoader = Callable[..., EventBus]


def sst_bus_loader(
    bus_registration: BusRegistrationFunc | None = None,
    use_default_registration=True,
    #
    use_global=False,
) -> BusLoader:
    """Prepare Loader function ready to setup EventBus"""

    def loader() -> EventBus:
        return create_event_bus(
            bus_registration=bus_registration,
            use_default_registration=use_default_registration,
            use_global=use_global,
        )

    return loader


_bus: EventBus | None = None


def sst_bus() -> EventBus:
    """Fetch Global EventBus Singleton"""

    global _bus
    if _bus is None:
        raise RuntimeError("No access to global _bus without bootstrap!")
    logger.debug("provide cached bus")

    return _bus


def create_event_bus(
    bus_registration: BusRegistrationFunc | None = None,
    use_default_registration=True,
    #
    use_global=False,
) -> EventBus:
    """Load EventBus explicit as one-time initialization"""

    bus = EventBus()

    if use_default_registration:
        register_default_event_handler(bus)

    if bus_registration:
        bus_registration(bus)

    # logger.info("EventBus setup complete")
    bus.emit(
        event_name=CoreEvent.BUS_DIAG,
        sender="BusSetup",
        log="EventBus setup complete",
    )

    if use_global:
        set_global_bus(bus)
    return bus


def set_global_bus(bus: EventBus | None) -> None:
    """Register local EventBus as new EventBus or replace former"""
    # TODO: emit?
    global _bus
    if _bus is not None:
        logger.warning(f"Replacing existing global _bus: {_bus!r}")
        # TODO: emit old And new?

    _bus = bus

    if _bus is None:
        # TODO: emit?
        logger.info("Global bus set to 'None'")
    else:
        # TODO: emit?
        logger.info(f"New bus set as global: {_bus!r}")
```

```py
"""
sstcore.core - Assemble the System!

Load and combine all singletons in one System.

- Use System.bootstrap(_custom_loaders_) for Non-Global Instance

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

**all**: list = [
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

def sst_system_loader( # intended for user
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

```
