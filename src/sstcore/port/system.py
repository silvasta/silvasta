"""
Define the Shape of the System

- Central Layer of the Core Orchestration

Combine Boot, Interface and Distribution:
- Bus: Handler and Emitter
- Config: Settings and Paths
- Printer: Nice UX and DX

System: The sst Director
                                                 DependencyLevel[7]
                                                         printer(6)
"""

# STRATEGY: naming check Spec,Data,Inputs,... globally!!

# IDEA: TypedDictInput->Spec
# DataClass(OrValidated)->Param, or just DTO?
# param = SystemBootDTO(**data:SystemBootParam)

__all__: list[str] = [
    "SstSystem",
    "CliSystem",
    # Loader
    "SystemLoader",
    "ConfigLoader",
    "BusLoader",
]

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, Self, TypedDict, Unpack

from .config import Config, HomeSetup, Paths, Settings
from .event import BusRegistration, EventBus
from .event.emit import Emitter
from .printer import Printer


class SstSystem(Protocol):
    """Any System must fulfill: ..."""

    @property
    def bus(self) -> EventBus:
        """- Provide Global Wiring"""

    @classmethod
    def boot(cls) -> Self:
        """- Boot without Input"""


class CliSystem[C: Config](SstSystem, Protocol):
    """The SstSystem provides ..."""

    @property
    def config(self) -> C: ...
    @property
    def printer(self) -> Printer: ...
    @property
    def emitter(self) -> Emitter: ...

    @classmethod
    def boot(
        # TASK: second TypedDict for loader?
        # - maybe with concat?
        cls,
        # *,
        # config_loader: ConfigLoader | None = None,
        # bus_loader: BusLoader | None = None,
        # printer: Printer | None = None,
        # # AI: concatenate or how could this work?
        # # **tool_spec: Unpack[CliSystemToolSpec],
        # **cli_args: Unpack[CliSystemInput],
        **data: Unpack[SystemBootParam],
    ) -> Self:
        """Accept Changes and Provide the full Infrastructure"""


#  LINE: -- System Boot -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class SystemLoader[SysT: SstSystem](Protocol):
    def __call__(self, **cli_args: Unpack[CliSystemInput]) -> SysT:
        """Boot the System with the provided (optional?) args"""


class CliSystemInput(TypedDict, total=False):
    """Govern the ArgSpace for the CLI System Setup"""

    verbose: bool
    quiet: bool
    settings: Path | None
    home: HomeSetup


@dataclass
class CliSystemData:
    """Transfer validated System Input including Defaults"""

    verbose: bool = False
    quiet: bool = False
    settings: Path | None = None
    home: HomeSetup = HomeSetup.PROJECT


class SystemLoading[SysT: CliSystem](Protocol):
    """Bind the tools to the system and make it ready to boot"""

    def __call__(
        self, **tool_spec: Unpack[CliSystemToolSpec]
    ) -> SystemLoader[SysT]: ...


class CliSystemToolSpec(TypedDict, total=False):  # CHECK: total=True??
    config_loader: ConfigLoader
    bus_loader: BusLoader
    printer: Printer


@dataclass
class CliSystemTools:
    config_loader: ConfigLoader | None = None
    bus_loader: BusLoader | None = None
    printer: Printer | None = None


class SystemBootParam(CliSystemToolSpec, CliSystemInput): ...


@dataclass
class SystemBootData(CliSystemData, CliSystemTools): ...


#  LINE: -- Config -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class ConfigLoader[P: Paths, S: Settings](Protocol):
    # class ConfigLoader[C: Config](Protocol):
    def __call__(self, **options: Unpack[ConfigInput[P, S]]) -> Config:
        # CHECK: -> Config[N: Names, D: Defaults, S: Settings, P: Paths] ??
        """Prepare the Configmanager bootstrap with all 4 components"""


class ConfigInput[P: Paths, S: Settings](TypedDict, total=False):
    settings_cls: type[S]
    paths_cls: type[P]
    setting_file: Path | None
    project_name: str | None
    project_root: Path | None
    home_setup: HomeSetup | None


#  LINE: -- Bus -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class BusLoader(Protocol):
    def __call__(self, **options: Unpack[BusInput]) -> EventBus:
        """Prepare the Bus - Ready to Launch with all Subscribers"""


class BusInput(TypedDict, total=False):
    bus_registration: BusRegistration | None
    use_default_registration: bool


@dataclass
class BusData:
    bus_registration: BusRegistration | None = None
    use_default_registration: bool = True


# LATER: remove
# LINE: -- tests -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def _check_toolspec_binder(
    **tool_spec: Unpack[CliSystemToolSpec],
) -> CliSystemTools:
    return CliSystemTools(**tool_spec)


_x = _check_toolspec_binder()  # INFO: check IDE input view here


def _check_cli_input(**cli_args: Unpack[CliSystemInput]) -> CliSystemData:
    return CliSystemData(**cli_args)


_y = _check_cli_input()  # INFO: check IDE input view here
