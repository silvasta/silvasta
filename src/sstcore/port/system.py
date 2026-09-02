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
from typing import Any, Protocol, Self, TypedDict, Unpack

from .config import Config, HomeSetup
from .event import EventBus
from .event.emit import Emitter
from .event.name import EventName
from .printer import Printer

type ConfigLoader = Callable[..., Config]
# LATER: Protocol with TypedDict args?
type BusLoader = Callable[..., EventBus]


class SystemLoader(Protocol):
    def __call__(self, **kwargs: Unpack[CliSystemArgs]) -> SstSystem: ...


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


# LATER: collapse levels?
class SstSystem(System, Protocol):
    """
    Level 1 - Library Essentials

    - Check individual Protocols for more information
    """

    @property
    def config(self) -> Config: ...
    @property
    def printer(self) -> Printer: ...
    @property
    def emitter(self) -> Emitter: ...

    @classmethod
    def boot(cls) -> Self: ...


class CliSystemArgs(TypedDict, total=False):
    """Provide typed arguments for the System CLI setup"""

    verbose: bool
    quiet: bool
    settings: Path | None
    home: HomeSetup


# LATER: collapse levels?
class CliSystem(SstSystem, Protocol):
    """
    Level 2 - Console Pipeline Requirements

    - Specification as used in: sst
    """

    @classmethod
    def boot(
        cls,
        *,
        # TASK: second TypedDict for loader?
        config_loader: ConfigLoader | None = None,
        bus_loader: BusLoader | None = None,
        printer: Printer | None = None,
        **cli_args: Unpack[CliSystemArgs],
    ) -> Self:
        """Accept Changes and Provide the full Infrastructure"""
