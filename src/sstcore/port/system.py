"""
Define the Shape of the System

- Central Layer of the Core Orchestration

Combine Boot, Interface and Distribution:
- Bus: Handler and Emit
- Config: Settings and Paths
- Print: Nice UX and DX

System: The sst Director
                                   DependencyLevel.sstcore.port[10]
"""

__all__: list[str] = [
    "SstSystem",
    "CliSystem",
    "SystemLoader",
    "SystemLoading",
    #
    "CliSystemInput",
    "SystemLoaderInput",
    "SystemBootParam",
    "CliSystemSpec",
    "CliSystemTools",
    "SystemBootSpec",
    # config
    "ConfigLoader",
    "ConfigLoading",
    "ConfigSetupInput",
    "ConfigInput",
    "ConfigSpec",
    # bus
    "BusLoader",
    "BusInput",
    "BusSpec",
]

from pathlib import Path
from typing import Protocol, Self, TypedDict, Unpack

from .config import Config, Defaults, HomeSetup, Names, Paths, Settings
from .event import BusRegistration, EventBus
from .event.emit import Emit
from .printer import Print
from .structures import ParamSpec


class SstSystem(Protocol):
    """Any System must fulfill: ..."""

    @property
    def bus(self) -> EventBus:
        """- Provide Global Wiring"""

    @classmethod
    def boot(cls) -> Self:
        """- Boot without Input"""


class CliSystem[C = Config, E = Emit](SstSystem, Protocol):
    """The SstSystem provides ..."""

    @property
    def config(self) -> C: ...
    @property
    def printer(self) -> Print: ...
    @property
    def emitter(self) -> E: ...

    @classmethod
    def boot(cls, **data: Unpack[SystemBootParam]) -> Self:
        """Accept Changes and Provide the full Infrastructure"""


#  LINE: -- Loader -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class SystemLoader[
    SysT: SstSystem = SstSystem,
](Protocol):
    def __call__(self, **param: Unpack[CliSystemInput]) -> SysT:
        """Boot the System with or without provided args"""


class SystemLoading[
    SysT: CliSystem = CliSystem,
](Protocol):
    """Bind the tools to the system and make it ready to boot"""

    def __call__(
        self, **spec: Unpack[SystemLoaderInput]
    ) -> SystemLoader[SysT]: ...


class ConfigLoader[
    D: Defaults = Defaults,
    N: Names = Names,
    P: Paths = Paths,
    S: Settings = Settings,
](Protocol):
    def __call__(
        self, **options: Unpack[ConfigInput[P, S]]
    ) -> Config[D, N, P, S]:
        """Prepare the Configmanager bootstrap with all 4 components"""


class ConfigLoading[
    D: Defaults = Defaults,
    N: Names = Names,
    P: Paths = Paths,
    S: Settings = Settings,
](Protocol):
    """Bind static project config setup and return a CLI-ready ConfigLoader."""

    def __call__(
        self, **setup: Unpack[ConfigSetupInput[P, S]]
    ) -> ConfigLoader[D, N, P, S]: ...


class BusLoader(Protocol):
    def __call__(self, **options: Unpack[BusInput]) -> EventBus:
        """Prepare the Bus - Ready to Launch with all Subscribers"""


#  LINE: -- Typed Kwarg Input -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class CliSystemInput(TypedDict, total=False):
    """Govern the ArgSpace for the CLI System Setup"""

    verbose: bool
    quiet: bool
    settings: Path | None
    home: HomeSetup


class SystemLoaderInput(TypedDict, total=False):
    config_loader: ConfigLoader
    bus_loader: BusLoader
    printer: Print


class SystemBootParam(SystemLoaderInput, CliSystemInput):
    """Define Input with both layers of System Input"""


class ConfigSetupInput[P: Paths, S: Settings](TypedDict, total=False):
    """Static App-level Config declarations."""

    settings_cls: type[S]
    paths_cls: type[P]
    project_name: str | None
    project_root: Path | None


class ConfigInput[P: Paths, S: Settings](ConfigSetupInput[P, S], total=False):
    setting_file: Path | None
    home_setup: HomeSetup


class BusInput(TypedDict, total=False):
    bus_registration: BusRegistration | None
    use_default_registration: bool


#  LINE: -- ParamSpec DataClasses -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class CliSystemSpec(ParamSpec, kw_only=False):
    """Transfer validated System Input including Defaults."""

    verbose: bool = False
    quiet: bool = False
    settings: Path | None = None
    home: HomeSetup = HomeSetup.PROJECT

    @property
    def config_input(self) -> ConfigInput:
        """Map CLI arguments to ConfigInput"""
        return {
            "setting_file": self.settings,
            "home_setup": self.home,
        }


class CliSystemTools(ParamSpec, kw_only=False):
    config_loader: ConfigLoader | None = None
    bus_loader: BusLoader | None = None
    printer: Print | None = None


class SystemBootSpec(CliSystemSpec, CliSystemTools, kw_only=False):
    """Capture Param of both layers of System Params."""

    @classmethod
    def from_layers(
        cls,
        tools: CliSystemTools | None = None,
        cli: CliSystemSpec | None = None,
        **overrides: Unpack[SystemBootParam],
    ) -> Self:
        return cls.merge(tools, cli, **overrides)  # ty:ignore

    @property
    def cli_data(self) -> CliSystemSpec:
        """Provide separated CLI input data."""
        return self.extract(CliSystemSpec)

    @property
    def cli_tools(self) -> CliSystemTools:
        """Provide separated Tool Loaders."""
        return self.extract(CliSystemTools)


class ConfigSpec[P: Paths, S: Settings](ParamSpec, kw_only=False):
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


class BusSpec(ParamSpec, kw_only=False):
    bus_registration: BusRegistration | None = None
    use_default_registration: bool = True
