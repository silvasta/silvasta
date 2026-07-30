"""
Create loader for System and collect loader of all Components

- System
- ConfigManager
- EventBus
                                                       DependencyLevel[3]
"""

__all__: list[str] = [
    "SystemLoader",
    "ConfigLoader",
    "BusLoader",
    "sst_system_loader",
    "sst_config_loader",
    "sst_bus_loader",
]


from collections.abc import Callable
from pathlib import Path

from ..utils import Printer
from ..utils.path import HomeSetup
from ._boot import BusLoader, ConfigLoader, sst_bus_loader, sst_config_loader
from ._core import System

type SystemLoader = Callable[..., System]


def sst_system_loader(  # intended for project configs
    config_loader: ConfigLoader | None = None,
    bus_loader: BusLoader | None = None,
    printer: Printer | None = None,
) -> SystemLoader:
    """Prepare Loader function ready to setup System"""

    def loader(  # intended for cli args or any other runtime override
        verbose: bool = False,
        quiet: bool = False,
        setting_file: Path | None = None,
        home: HomeSetup = HomeSetup.PROJECT,
    ) -> System:
        system: System = System.bootstrap(
            config_loader=config_loader,
            bus_loader=bus_loader,
            printer=printer,
            verbose=verbose,
            quiet=quiet,
            setting_file=setting_file,
            home=home,
        )

        return system

    return loader
