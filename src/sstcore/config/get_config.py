from pathlib import Path

from loguru import logger

from ..utils import HomeSetup
from .manager import ConfigManager
from .paths import SstPaths
from .settings import SstSettings

# TODO: _config
_config_instance: ConfigManager | None = None


def get_config(*, _allow_uninitialized: bool = False) -> ConfigManager:
    """Provide Cached ConfigManager Singleton"""

    global _config_instance

    if _config_instance is None:
        logger.warning("Config accessed before Bootstrap!")

        if _allow_uninitialized:
            logger.warning("Load config with SstSettings and SstPaths")
            return sst_config_loader(SstSettings, SstPaths)

        raise RuntimeError("No access to config without bootstrap!")
    logger.debug("provide cached config")

    return _config_instance


def default_config_loader(setting_file: Path | None = None) -> ConfigManager:
    """Prepare Loader for DefaultConfig"""

    return sst_config_loader(
        settings_cls=SstSettings,
        paths_cls=SstPaths,
        setting_file=setting_file,
        project_name="sachmis",
    )


def sst_config_loader[TSettings: SstSettings, TPaths: SstPaths](
    settings_cls: type[TSettings],
    paths_cls: type[TPaths],
    setting_file: Path | None = None,
    project_name: str = "",
    project_root: Path | None = None,
    home_setup: HomeSetup = HomeSetup.PROJECT,
) -> ConfigManager:
    """Load ConfigManager explicit as one-time initialization"""

    global _config_instance

    if _config_instance is not None:
        logger.warning(
            "ConfigManager is already initialized, ignoring override!"
        )
        return _config_instance

    logger.info("Setup ConfigManager with explicit parameters...")

    _config_instance = ConfigManager(
        settings_cls=settings_cls,
        paths_cls=paths_cls,
        setting_file=setting_file,
        project_name=project_name,
        project_root=project_root,
        home_setup=home_setup,
    )
    logger.info("ConfigManager setup completed")

    return _config_instance
