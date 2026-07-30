"""
Prepare Global instances for System or any other live process

- ConfigManager
- EventBus
                                                       DependencyLevel[X]
"""

__all__: list[str] = [
    "sst_config_loader",
    "ConfigLoader",
    "BusLoader",
    "sst_bus_loader",
    "create_event_bus",
]

from collections.abc import Callable
from pathlib import Path

from ..config import ConfigManager, SstPaths, SstSettings
from ..port.event import CoreEvent
from ..utils.path import HomeSetup
from .event import (
    BusRegistrationFunc,
    EventBus,
    register_default_event_handler,
)

type ConfigLoader[config: ConfigManager] = Callable[..., config]
type BusLoader = Callable[..., EventBus]


def sst_config_loader(
    settings_cls=SstSettings,
    paths_cls=SstPaths,
    project_name: str = "sstcore",
    home_setup: HomeSetup = HomeSetup.PROJECT,
    project_root: Path | None = None,
) -> ConfigLoader:
    """Prepare Loader function ready to setup ConfigManager"""

    def loader(  # CLI input
        setting_file: Path | None = None,
        home: HomeSetup = home_setup,
    ) -> ConfigManager:
        return ConfigManager(
            settings_cls=settings_cls,
            paths_cls=paths_cls,
            setting_file=setting_file,
            project_name=project_name,
            project_root=project_root,
            home_setup=home,
        )

    return loader


def sst_bus_loader(
    bus_registration: BusRegistrationFunc | None = None,
    use_default_registration=True,
) -> BusLoader:
    """Prepare Loader function ready to setup EventBus"""

    def loader() -> EventBus:
        return create_event_bus(
            bus_registration=bus_registration,
            use_default_registration=use_default_registration,
        )

    return loader


def create_event_bus(
    bus_registration: BusRegistrationFunc | None = None,
    use_default_registration=True,
) -> EventBus:
    """Load EventBus explicit as one-time initialization"""

    bus = EventBus()

    if use_default_registration:
        register_default_event_handler(bus)

    if bus_registration:
        bus_registration(bus)

    bus.emit(
        event_name=CoreEvent.BUS_DIAG,
        sender="BusSetup",
        log="EventBus setup complete",
    )

    return bus
