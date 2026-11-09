"""
Create loader for System and collect loader of all Components

- System
  + plus Mixin for easy application
- ConfigManager
- EventBus
                                                       DependencyLevel[3]
"""

from examples._Explan_Config_System_Cli import Defaults

__all__: list[str] = [
    "sst_config_loader",
    "sst_bus_loader",
    "sst_system_loader",
    "SystemMixin",
]


from pathlib import Path
from typing import Protocol, Unpack

from ..port.config import Config, Names, Paths, Settings
from ..port.event import BusRegistration, EventBus
from ..port.event.emit import Emit, Emitting, Log
from ..port.event.name import EventName
from ..port.link import portlink
from ..port.printer import Print
from ..port.system import (
    BusInput,
    BusLoader,
    CliSystem,
    CliSystemInput,
    ConfigInput,
    ConfigLateInput,
    ConfigLoader,
    SystemLoader,
)
from ._core import System
from .config import ConfigManager, HomeSetup
from .event import Bus

type S[D: Defaults, N: Names] = type[Settings[D, N]]
type P[D: Defaults, N: Names] = type[Paths[D, N]]


def sst_config_loader[D: Defaults, N: Names](
    settings_cls: S[D, N],
    paths_cls: P[D, N],
    project_name: str = "sstcore",
    project_root: Path | None = None,
    home_setup: HomeSetup = HomeSetup.PROJECT,
) -> ConfigLoader:
    """Prepare Loader function ready to setup ConfigManager"""

    def config_loader(  # CLI input
        **spec: Unpack[ConfigLateInput],
    ) -> Config:  # LATER: narrow by outer input...
        return ConfigManager.bootstrap(
            **ConfigInput[D, N](
                settings_cls=settings_cls,
                paths_cls=paths_cls,
                project_name=project_name,
                project_root=project_root,
                home_setup=home_setup,
                **spec,
            )
        )

    return config_loader


def sst_bus_loader(
    bus_registration: BusRegistration | None = None,
    use_default_registration=True,
) -> BusLoader:
    """Prepare Loader function ready to setup EventBus"""

    def bus_loader(**spec: Unpack[BusInput]) -> EventBus:
        return Bus.ready(  # LATER: narrow by outer input...
            **BusInput(
                **spec,  # no args in inner loader intended...
                bus_registration=bus_registration,
                use_default_registration=use_default_registration,
            )
        )

    return bus_loader


def sst_system_loader(**spec: Unpack[CliSystemInput]) -> SystemLoader:
    """Prepare Loader function ready to setup System"""

    def system_loader(**cli_args: Unpack[CliSystemInput]) -> CliSystem:
        return System.boot(**{**spec, **cli_args})

    return system_loader


class _SystemMixing(Protocol):
    @property
    def config(self) -> Config: ...
    @property
    def emitter(self) -> Emit: ...
    @property
    def print(self) -> Print: ...
    @property
    def emit(self) -> Emitting: ...
    @property
    def log(self) -> Log: ...


@portlink(_SystemMixing)
class SystemMixin[C: Config = Config, E: Emit = Emit]:
    """Exfiltrate and Provide the Core Tools of the System"""

    def __init__(self, system: CliSystem[C, E]) -> None:
        self.system: CliSystem[C, E] = system

    @property
    def config(self) -> C:
        return self.system.config

    @property
    def emitter(self) -> E:
        return self.system.emitter

    @property
    def print(self) -> Print:
        return self.system.printer

    def emit(self, event: EventName, sender: str, **payload) -> None:
        return self.emitter(event, sender=sender, **payload)

    def log(
        self,
        message: str,
        /,
        *,
        event: EventName,
        sender: str,
        level: str = "INFO",
        **extra,
    ) -> None:  # TODO: fix order, message??
        return self.emitter.log(event, sender, message, level=level, **extra)
