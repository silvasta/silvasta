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

from dataclasses import asdict, dataclass, fields
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


class CliSystem[C: Config, E: Emitter](SstSystem, Protocol):
    """The SstSystem provides ..."""

    @property
    def config(self) -> C: ...
    @property
    def printer(self) -> Printer: ...
    @property
    def emitter(self) -> E: ...

    @classmethod
    def boot(cls, **data: Unpack[SystemBootParam]) -> Self:
        """Accept Changes and Provide the full Infrastructure"""


#  LINE: -- System Boot -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class SystemLoader[SysT: SstSystem](Protocol):
    def __call__(self, **param: Unpack[CliSystemInput]) -> SysT:
        """Boot the System with or without provided args"""


class SystemLoading[SysT: CliSystem](Protocol):
    """Bind the tools to the system and make it ready to boot"""

    def __call__(
        self, **spec: Unpack[CliSystemToolSpec]
    ) -> SystemLoader[SysT]: ...


#  LINE: -- System Kwarg Input -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class CliSystemInput(TypedDict, total=False):
    """Govern the ArgSpace for the CLI System Setup"""

    verbose: bool
    quiet: bool
    settings: Path | None
    home: HomeSetup


class CliSystemToolSpec(TypedDict, total=False):
    config_loader: ConfigLoader
    bus_loader: BusLoader
    printer: Printer


class SystemBootParam(CliSystemToolSpec, CliSystemInput):
    """Define Input with both layers of System Input"""


#  LINE: -- System Param DTO -- -- - -- -- - -- -- - -- -- - -- -- - -- --


@dataclass
class CliSystemData:
    """Transfer validated System Input including Defaults"""

    verbose: bool = False
    quiet: bool = False
    settings: Path | None = None
    home: HomeSetup = HomeSetup.PROJECT


@dataclass
class CliSystemTools:
    config_loader: ConfigLoader | None = None
    bus_loader: BusLoader | None = None
    printer: Printer | None = None


@dataclass
class SystemBootData(CliSystemData, CliSystemTools):
    """Capture Param of both layers of System Params"""

    @classmethod
    def from_layers(
        cls,
        tools: CliSystemTools | None = None,
        cli: CliSystemData | None = None,
    ) -> Self:
        return cls(
            **asdict(tools or CliSystemTools()),
            **asdict(cli or CliSystemData()),
        )

    def extract_base[T](self, target_cls: type[T]) -> T:
        """Dynamically extract fields belonging to a base class"""
        _kwargs = {f.name: getattr(self, f.name) for f in fields(target_cls)}  # ty:ignore
        return target_cls(**_kwargs)

    @property
    def cli_data(self) -> CliSystemData:
        """Provide separated CLI input data"""
        return self.extract_base(CliSystemData)

    @property
    def cli_tools(self) -> CliSystemTools:
        """Provide separated Tool Loaders"""
        return self.extract_base(CliSystemTools)


#  LINE: -- Config -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class ConfigLoader[P: Paths, S: Settings](Protocol):
    # FIX: this is just for full input...
    # - bind by cli input, together with RENAME!!
    def __call__(self, **options: Unpack[ConfigInput[P, S]]) -> Config:
        """Prepare the Configmanager bootstrap with all 4 components"""


class ConfigInput[P: Paths, S: Settings](TypedDict, total=False):
    settings_cls: type[S]
    # AI: why here not None? why not everywhere or nowhere?
    paths_cls: type[P]
    setting_file: Path | None
    project_name: str | None
    project_root: Path | None
    home_setup: HomeSetup


@dataclass
class ConfigData[P: Paths, S: Settings]:
    settings_cls: type[S] | None = None
    paths_cls: type[P] | None = None
    setting_file: Path | None = None
    project_name: str | None = None
    project_root: Path | None = None
    home_setup: HomeSetup = HomeSetup.GLOBAL

    def paths(self, default: type[P]) -> type[P]:
        return default if self.paths_cls is None else self.paths_cls

    def settings(self, default: type[S]) -> type[S]:
        return default if self.settings_cls is None else self.settings_cls


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


def _check_cli_data(data: CliSystemData):  # FAIL: no additional check
    _check_cli_input(**asdict(data))


_y = _check_cli_input()  # INFO: check IDE input view here
