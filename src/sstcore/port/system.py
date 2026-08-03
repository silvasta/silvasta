"""
Define the Shape of the System

-
"""

from pathlib import Path

__all__: list[str] = [
    "System",
    "SstSystem",
    "CliSystem",
    # loader type definitions
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
    @property
    def bus(self) -> EventBus: ...
    def emit(self, event: EventName, sender: str, **payload: Any) -> None: ...

    @classmethod
    def bootstrap(cls, *args, **kwargs) -> Self: ...


class SstSystem(System, Protocol):
    @property
    def config(self) -> Config: ...
    @property
    def printer(self) -> Printer: ...
    @property
    def emitter(self): ...  # TODO: types

    @classmethod
    def bootstrap(cls) -> Self: ...


class CliSystem(SstSystem, Protocol):
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
