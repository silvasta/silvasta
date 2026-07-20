"""
Hold and prepare Global Singleton ConfigManager instance.

- Provide protected access to initial setup (unlock with flag)
- Prepare ready-to-use loader for CLI, or any other purpose
- Handle infrastructure for project setups with custom loader
- Expose global Singleton: `config: ConfigManager = sst_config()`
  (easy access e.g.: `sst_config().paths.summary_file(.xml)`)

"""

__all__: list[str] = [
    "ConfigLoader",
    "sst_config_loader",
    "sst_config",
    "set_global_config",
    "create_config_manager",
]

from collections.abc import Callable
from pathlib import Path

from loguru import logger

from ..utils.path import HomeSetup
from .manager import ConfigManager, SstConfig
from .paths import SstPaths
from .settings import SstSettings

type ConfigLoader[Config: ConfigManager] = Callable[..., Config]


def sst_config_loader[Config: SstConfig](
    settings_cls=SstSettings,
    paths_cls=SstPaths,
    project_name: str = "sstcore",
    home_setup: HomeSetup = HomeSetup.PROJECT,
    project_root: Path | None = None,
    #
    use_global: bool = False,
) -> ConfigLoader[Config]:
    """Prepare Loader function ready to setup ConfigManager"""

    def loader(  # CLI input
        setting_file: Path | None = None,
        home: HomeSetup = home_setup,
    ) -> ConfigManager:
        return create_config_manager(
            settings_cls=settings_cls,
            paths_cls=paths_cls,
            setting_file=setting_file,
            project_name=project_name,
            project_root=project_root,
            home_setup=home,
            #
            use_global=use_global,
        )

    return loader


_config: ConfigManager | None = None


def sst_config(*, _allow_uninitialized: bool = False) -> ConfigManager:
    """Fetch Global ConfigManager Singleton"""

    global _config
    if _config is None:
        raise RuntimeError("No access to global _config without bootstrap!")
    logger.debug("provide cached _config")

    return _config


def create_config_manager[TSettings: SstSettings, TPaths: SstPaths](
    settings_cls: type[TSettings] | None,
    paths_cls: type[TPaths] | None,
    setting_file: Path | None = None,
    project_name: str = "",
    project_root: Path | None = None,
    home_setup: HomeSetup = HomeSetup.PROJECT,
    #
    use_global: bool = False,
) -> ConfigManager:
    """Load ConfigManager explicit as one-time initialization"""

    config: ConfigManager = ConfigManager(
        settings_cls=settings_cls or SstSettings,
        paths_cls=paths_cls or SstPaths,
        setting_file=setting_file,
        project_name=project_name,
        project_root=project_root,
        home_setup=home_setup,
    )
    logger.info("ConfigManager setup complete")
    if use_global:
        set_global_config(config)

    return config


def set_global_config(config: ConfigManager | None) -> None:
    """Register local System as new System or replace former"""

    global _config
    if _config is not None:
        logger.warning(f"Replacing existing global _config: {_config!r}")
    _config = config

    if _config is None:
        logger.info("Global config set to 'None'")
    else:
        logger.info(f"New config set as global: {_config!r}")
