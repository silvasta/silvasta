"""
Define the Shape of the System

-
"""

from pathlib import Path

__all__: list[str] = [
    "System",
    "SstSystem",
    "CliSystem",
    # Loader
    "SystemLoader",
    "ConfigLoader",
    "BusLoader",
]

from collections.abc import Callable
from typing import Any, Protocol, Self

from .config import Config
from .event import EventBus, EventName
from .printer import Printer

type SystemLoader = Callable[..., CliSystem]
type ConfigLoader = Callable[..., Config]
type BusLoader = Callable[..., EventBus]


class System(Protocol):
    """Level 0 - What any System must fulfill"""

    @property
    def bus(self) -> EventBus:
        """Cover and Distribute the Wires"""

    def emit(self, event: EventName, sender: str, **payload: Any) -> None:
        """Execute and Export the Call"""

    @classmethod
    def bootstrap(cls, *args, **kwargs) -> Self:
        """Be ready to launch"""


class SstSystem(System, Protocol):
    """Level 1 - The Essentials of the SstSystem"""

    @property
    def config(self) -> Config: ...
    @property
    def printer(self) -> Printer: ...
    @property
    def emitter(self): ...  # TODO: types

    @classmethod
    def bootstrap(cls) -> Self:
        """Silence Liskov and launch without input"""


class CliSystem(SstSystem, Protocol):
    """Level 2 - Console Pipeline Requirements"""

    @classmethod
    def bootstrap(
        cls,
        *,
        config_loader: ConfigLoader | None = None,
        bus_loader: BusLoader | None = None,
        printer: Printer | None = None,
        settings: Path | None = None,
        verbose: bool = False,
        quiet: bool = False,
        home: Any = None,
    ) -> Self: ...
