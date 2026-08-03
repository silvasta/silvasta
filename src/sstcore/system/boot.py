"""
Create loader for System and collect loader of all Components

- System
- ConfigManager
- EventBus
                                                       DependencyLevel[3]
"""

__all__: list[str] = [
    "sst_system_loader",
    "sst_config_loader",
    "sst_bus_loader",
]


from pathlib import Path

from ..config import ConfigManager, HomeSetup, SstPaths, SstSettings
from ..port.event import BusRegistration
from ..port.printer import Printer
from ..port.system import BusLoader, ConfigLoader, SystemLoader
from ._core import System
from .event import EventBus


def sst_system_loader(  # intended for project configs
    config_loader: ConfigLoader | None = None,
    bus_loader: BusLoader | None = None,
    printer: Printer | None = None,
) -> SystemLoader:
    """Prepare Loader function ready to setup System"""

    def loader(  # intended for cli args or any other runtime override
        verbose: bool = False,
        quiet: bool = False,
        settings: Path | None = None,
        home: HomeSetup = HomeSetup.PROJECT,
    ) -> System:
        system: System = System.bootstrap(
            config_loader=config_loader,
            bus_loader=bus_loader,
            printer=printer,
            settings=settings,
            verbose=verbose,
            quiet=quiet,
            home=home,
        )

        return system

    return loader


def sst_config_loader(
    settings_cls=SstSettings,
    paths_cls=SstPaths,
    project_name: str = "sstcore",
    project_root: Path | None = None,
    home_setup: HomeSetup = HomeSetup.PROJECT,
) -> ConfigLoader:
    """Prepare Loader function ready to setup ConfigManager"""

    def loader(  # CLI input
        setting_file: Path | None = None,
        home_setup: HomeSetup = home_setup,
    ) -> ConfigManager:
        return ConfigManager.bootstrap(
            settings_cls=settings_cls,
            paths_cls=paths_cls,
            project_name=project_name,
            project_root=project_root,
            #
            setting_file=setting_file,
            home_setup=home_setup,
        )

    return loader


def sst_bus_loader(
    bus_registration: BusRegistration | None = None,
    use_default_registration=True,
) -> BusLoader:
    """Prepare Loader function ready to setup EventBus"""

    def loader() -> EventBus:
        return EventBus.bootstrap(
            bus_registration=bus_registration,
            use_default_registration=use_default_registration,
        )

    return loader
