"""
Create loader for System and collect loader of all Components

- System
  + plus Mixin for easy application
- ConfigManager
- EventBus
                                                       DependencyLevel[3]
"""

__all__: list[str] = [
    "sst_config_loader",
    "sst_bus_loader",
    "sst_system_loader",
    "SystemMixin",
]


from pathlib import Path
from typing import Any, Protocol, Unpack

from ..port.config import Config
from ..port.event import BusRegistration, EventBus
from ..port.event.dto import CliDTO
from ..port.event.emit import Emit, Emitting, LogEmit
from ..port.event.name import EventName
from ..port.printer import Print, PrintInput
from ..port.system import (
    BusInput,
    BusLoader,
    CliSystem,
    CliSystemInput,
    ConfigInput,
    ConfigLoader,
    SystemLoader,
)
from ._core import System
from .config import ConfigManager, HomeSetup, SstPaths, SstSettings
from .event import Bus


def sst_config_loader(
    settings_cls=SstSettings,
    paths_cls=SstPaths,
    project_name: str = "sstcore",
    project_root: Path | None = None,
    home_setup: HomeSetup = HomeSetup.PROJECT,
) -> ConfigLoader:
    """Prepare Loader function ready to setup ConfigManager"""

    def config_loader(  # CLI input
        **spec: Unpack[ConfigInput],
        # setting_file: Path | None = None,
        # home_setup: HomeSetup = home_setup,
    ) -> Config:  # LATER: narrow by outer input...
        return ConfigManager.bootstrap(
            **ConfigInput(
                settings_cls=settings_cls,
                paths_cls=paths_cls,
                project_name=project_name,
                project_root=project_root,
                home_setup=home_setup,
                **spec,  # setting_file from CLI overrides!
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
    def printer(self) -> Print: ...
    @property
    def emit(self) -> Emitting: ...
    @property
    def log(self) -> LogEmit: ...
    @property
    def print(self) -> Print: ...


# TODO: @portlink(_SystemMixing)
class SystemMixin[C: Config = Config, E: Emit = Emit]:
    """Exfiltrate and Provide the Core Tools of the System"""

    def __init__(self, system: CliSystem) -> None:
        self.system: CliSystem[C, E] = system

    @property
    def config(self) -> C:
        return self.system.config

    @property
    def emitter(self) -> E:
        return self.system.emitter

    @property
    def printer(self) -> Print:
        return self.system.printer

    def emit(self, event: EventName, sender: str, **payload) -> None:
        return self.emitter(event, sender=sender, **payload)

    def log(
        self,
        event: EventName,
        sender: str,
        message: str,
        *,
        level: str = "INFO",
        **extra,
    ) -> None:  # TODO: fix order, message??
        return self.emitter.log(event, sender, message, level=level, **extra)

    def print(
        self, target: Any, /, *more: Any, **spec: Unpack[PrintInput]
    ) -> CliDTO:
        return self.printer(target, *more, **spec)
