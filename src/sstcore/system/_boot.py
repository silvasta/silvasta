"""
Prepare Global instances for System or any other live process

- ConfigManager
- EventBus
                                                       DependencyLevel[1]
"""

__all__: list[str] = [
    "ConfigLoader",
    "BusLoader",
    "sst_config_loader",
    "sst_bus_loader",
]

from collections.abc import Callable
from pathlib import Path

from ..config import ConfigManager, SstPaths, SstSettings
from ..utils.path import HomeSetup
from .event import BusRegistrationFunc, EventBus, create_event_bus

type ConfigLoader = Callable[..., ConfigManager]
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
