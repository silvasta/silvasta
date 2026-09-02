"""
Define the Shape of the System

- Central Layer of the Core Orchestration

Combine Boot, Interface and Distribution:
- EventBus: Handler and Emitter
- Config: Settings and Paths
- Printer: Nice UX and DX

System: The sst Director

"""

__all__: list[str] = [
    "System",
    "SstSystem",
    # Loader
    "SystemLoader",
    "ConfigLoader",
    "BusLoader",
]

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import NotRequired, Protocol, Self, TypedDict, Unpack

from .config import Config, HomeSetup
from .event import EventBus
from .event.emit import Emitter
from .printer import Printer

type ConfigLoader = Callable[..., Config]
# LATER: Protocol with TypedDict args?
type BusLoader = Callable[..., EventBus]


class SystemLoader(Protocol):
    # AI: Input spectrum must be No DTO!
    def __call__(self, **cli_args: Unpack[SystemCliArgs]) -> SstSystem:
        """Check if the Callable (object) provides a System"""


class System(Protocol):
    """Any System must fulfill: ..."""

    @property
    def bus(self) -> EventBus:
        """... Provide Global Wiring"""

    @classmethod
    def boot(cls) -> Self:
        """... Boot without Input"""


class SstSystem(System, Protocol):
    """The SstSystem provides ..."""

    @property
    def config(self) -> Config: ...
    @property
    def printer(self) -> Printer: ...
    @property
    def emitter(self) -> Emitter: ...

    @classmethod
    def boot(
        cls,
        *,
        # TASK: second TypedDict for loader?
        # - maybe with concat?
        config_loader: ConfigLoader | None = None,
        bus_loader: BusLoader | None = None,
        printer: Printer | None = None,
        **cli_args: Unpack[SystemCliArgs],
    ) -> Self:
        """Accept Changes and Provide the full Infrastructure"""


# IDEA: for collecting the loaders
class _SystemPreparing(Protocol):
    def __call__(self, **components: Unpack[_SystemLoaders]) -> SstSystem:
        """Check if the Callable (object) provides a System"""


# IDEA: for collecting the loaders
class _SystemLoaders(TypedDict, total=False):
    config_loader: ConfigLoader
    bus_loader: BusLoader
    printer: Printer


# IDEA: for collecting the loaders
@dataclass
class _SystemComponents:
    config_loader: ConfigLoader | None = None
    bus_loader: BusLoader | None = None
    printer: Printer | None = None


def _test_sync_loader_components(
    **components: Unpack[_SystemLoaders],
) -> _SystemComponents:
    return _SystemComponents(**components)


class SystemCliArgs(TypedDict, total=False):
    """Provide Typed Args for the System CLI Setup"""

    verbose: bool
    quiet: bool
    settings: NotRequired[
        Path | None
    ]  # None was needed for _attach_internal_callback...
    home: HomeSetup


@dataclass
class SystemCliInput:  # TODO: or SystemCliData? (pattern like StaticMetaData)
    """Transfer validated System Input including Defaults"""

    verbose: bool = False
    quiet: bool = False
    settings: Path | None = None
    home: HomeSetup = HomeSetup.PROJECT

    # @classmethod
    # REMOVE: directly use cls.__call__ as constructor
    # def load(cls, **args: Unpack[SystemCliArgs]) -> Self:
    #     return cls(**args)


def _test_sync_args_input(**cli_args: Unpack[SystemCliArgs]) -> SystemCliInput:
    return SystemCliInput(**cli_args)
