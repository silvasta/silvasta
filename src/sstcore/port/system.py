"""
Define the Shape of the System

- Central Layer of the Core Orchestration

Combine Boot, Interface and Distribution:
- EventBus: Handler and Emitter
- Config: Settings and Paths
- Printer: Nice UX and DX

System: The sst Director

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
from .event import EventBus
from .event.name import EventName
from .printer import Printer

type SystemLoader = Callable[..., CliSystem]
type ConfigLoader = Callable[..., Config]
type BusLoader = Callable[..., EventBus]


class System(Protocol):
    """
    Level 0 - Minimal Boundary

    Any System must fulfill:
    """

    @property
    def bus(self) -> EventBus:
        """Distribute global wiring"""

    def emit(self, event: EventName, sender: str, **payload: Any) -> None:
        """Provide and execute calls"""

    @classmethod
    def boot(cls, *args, **kwargs) -> Self:
        """Bind ready-to-use setup"""


class SstSystem(System, Protocol):
    """
    Level 1 - Library Essentials

    - Check individual Protocols for more information
    """

    @property
    def config(self) -> Config: ...
    @property
    def printer(self) -> Printer: ...

    # IMPORTANT:
    # IMPORTANT:
    # IMPORTANT:
    # IMPORTANT:
    # IMPORTANT:
    # @property
    # def emitter(self) -> Emitter: ...

    @classmethod
    def boot(cls) -> Self: ...


class CliSystem(SstSystem, Protocol):
    """
    Level 2 - Console Pipeline Requirements

    - Specification as used in: sst
    """

    @classmethod
    def boot(
        cls,
        *,
        config_loader: ConfigLoader | None = None,
        bus_loader: BusLoader | None = None,
        printer: Printer | None = None,
        settings: Path | None = None,
        verbose: bool = False,
        quiet: bool = False,
        home: Any = None,
    ) -> Self:
        """Accept Changes and Provide the full Infrastructure"""
