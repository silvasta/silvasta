"""
Hold and prepare Global Singleton ConfigManager instance.

- Provide protected access to initial setup (unlock with flag)
- Prepare ready-to-use loader for CLI, or any other purpose
- Handle infrastructure for project setups with custom loader
- Expose global Singleton: `config: ConfigManager = sst_config()`
  (easy access e.g.: `sst_config().paths.summary_file(.xml)`)

Example for Projects:

```py
# sachmis.config.manager:
from sstcore.config import ConfigManager
from sstcore.config.loader import setup_config_manager, sst_config

from .defaults import Defaults
from .names import Names
from .paths import Paths
from .settings import Settings

type SachmisConfig = ConfigManager[Settings, Names, Defaults, Paths]

def config_loader(setting_file: Path | None = None) -> SachmisConfig:
    return setup_config_manager(
        settings_cls=Settings,
        paths_cls=Paths,
        setting_file=setting_file,
        project_name="sachmis",
    )
```
"""

from collections.abc import Callable
from pathlib import Path

from loguru import logger

from ..utils import HomeSetup
from .manager import ConfigManager
from .paths import SstPaths
from .settings import SstSettings

_config: ConfigManager | None = None

type ConfigLoader = Callable[[Path | None], ConfigManager]

# LATER: this pattern for EventBus or EventSystem?


def sst_config(*, _allow_uninitialized: bool = False) -> ConfigManager:
    """Fetch Global Singleton ConfigManager instance"""

    global _config

    if _config is None:
        logger.warning("Config accessed before Bootstrap!")

        if _allow_uninitialized:
            logger.warning("Load config with SstSettings and SstPaths")
            return setup_config_manager(SstSettings, SstPaths)

        raise RuntimeError("No access to config without bootstrap!")

    logger.debug("provide cached config")

    return _config


def sst_config_loader(
    setting_file: Path | None = None, project_name: str = "sstcore"
) -> ConfigManager:
    """Prepare Loader function ready to setup ConfigManager"""

    return setup_config_manager(
        settings_cls=SstSettings,
        paths_cls=SstPaths,
        setting_file=setting_file,
        project_name=project_name,
    )


def setup_config_manager[TSettings: SstSettings, TPaths: SstPaths](
    settings_cls: type[TSettings],
    paths_cls: type[TPaths],
    setting_file: Path | None = None,
    project_name: str = "",
    project_root: Path | None = None,
    home_setup: HomeSetup = HomeSetup.PROJECT,
) -> ConfigManager:
    """Load ConfigManager explicit as one-time initialization"""

    global _config

    if _config is not None:
        logger.warning(
            "ConfigManager is already initialized, ignoring override!"
        )
        return _config

    logger.info("Setup ConfigManager with explicit parameters...")

    _config = ConfigManager(
        settings_cls=settings_cls,
        paths_cls=paths_cls,
        setting_file=setting_file,
        project_name=project_name,
        project_root=project_root,
        home_setup=home_setup,
    )
    logger.info("ConfigManager setup completed")

    return _config
