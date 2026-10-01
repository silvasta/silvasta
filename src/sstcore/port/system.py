"""
Define the Shape of the System

- Central Layer of the Core Orchestration

Combine Boot, Interface and Distribution:
- EventBus: Handler and Emitter
- Config: Settings and Paths
- Printer: Nice UX and DX

System: The sst Director
                                                 DependencyLevel[7]
                                                         printer(6)
"""
# - IMPORTANT: naming check Spec,Data,Inputs,... globally!!

__all__: list[str] = [
    "SstSystem",
    "CliSystem",
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


class SystemLoader[SysT: SstSystem](Protocol):
    def __call__(self, **cli_args: Unpack[CliSystemInput]) -> SysT:
        """Boot the System with the provided (optional?) args"""


class SystemLoading[SysT: CliSystem](Protocol):
    def __call__(
        self, **tool_spec: Unpack[CliSystemToolSpec]
    ) -> SystemLoader[SysT]:
        """Bind the tools to the system and make it ready to boot"""


# TASK: Protocol with TypedDict args?
type ConfigLoader = Callable[..., Config]
type BusLoader = Callable[..., EventBus]


class SstSystem(Protocol):
    """Any System must fulfill: ..."""

    @property
    def bus(self) -> EventBus:
        """- Provide Global Wiring"""

    @classmethod
    def boot(cls) -> Self:
        """- Boot without Input"""


class CliSystem(SstSystem, Protocol):
    """The SstSystem provides ..."""

    @property
    def config(self) -> Config: ...
    @property
    def printer(self) -> Printer: ...
    @property
    def emitter(self) -> Emitter: ...

    @classmethod
    def boot(
        # TASK: second TypedDict for loader?
        # - maybe with concat?
        cls,
        *,
        config_loader: ConfigLoader | None = None,
        bus_loader: BusLoader | None = None,
        printer: Printer | None = None,
        # **tool_spec: Unpack[CliSystemToolSpec],
        **cli_args: Unpack[CliSystemInput],
    ) -> Self:
        """Accept Changes and Provide the full Infrastructure"""


class CliSystemToolSpec(TypedDict, total=False):  # CHECK: total=True??
    config_loader: ConfigLoader
    bus_loader: BusLoader
    printer: Printer


class CliSystemInput(TypedDict, total=False):
    """Provide Typed Args for the System CLI Setup"""

    # CHECK: was needed for _attach_internal_callback...
    verbose: bool
    quiet: bool
    # settings: NotRequired[Path | None]  # CHECK:
    # settings: Path  # CHECK:
    settings: NotRequired[Path]  # CHECK:
    home: HomeSetup


@dataclass
class CliSystemTools:
    config_loader: ConfigLoader | None = None
    bus_loader: BusLoader | None = None
    printer: Printer | None = None


@dataclass
class CliSystemData:
    """Transfer validated System Input including Defaults"""

    verbose: bool = False
    quiet: bool = False
    settings: Path | None = None
    home: HomeSetup = HomeSetup.PROJECT


#  LINE: -- tests -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def _check_toolspec_binder(
    **tool_spec: Unpack[CliSystemToolSpec],
) -> CliSystemTools:
    return CliSystemTools(**tool_spec)


_x = _check_toolspec_binder()  # INFO: check IDE input view here


def _check_cli_input(**cli_args: Unpack[CliSystemInput]) -> CliSystemData:
    return CliSystemData(**cli_args)


_y = _check_cli_input()  # INFO: check IDE input view here
