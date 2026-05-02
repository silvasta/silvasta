from loguru import logger

from .manager import ConfigManager
from .paths import SstPaths
from .settings import SstSettings

_config_instance: ConfigManager | None = None


def get_config() -> ConfigManager:
    global _config_instance

    if _config_instance is None:
        logger.info("Setup ConfigManager...")

        _config_instance = ConfigManager(
            settings_cls=SstSettings,
            paths_cls=SstPaths,
            write_new_master_setting_file_if_missing=True,
        )
        logger.info("ConfigManager setup completed")
    else:
        logger.debug("provide cached config")

    return _config_instance
