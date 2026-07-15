"""
Provide Configuration Pipeline with global access and json support

- ConfigManger: orchestrate the setup and provide global access
  - Settings: bind the components and bridge to json
  - Paths: assemble and ensure filesystem locations
  - Defaults: provide default values and parameter
  - Names: provide static and dynamic parsed names

- sst_config: access to global 'config' singleton (unlock or load setup first)

"""

__all__: list = [
    "ConfigManager",
    "SstSettings",
    "SstPaths",
    "SstDefaults",
    "SstNames",
    "sst_config",
]

from .defaults import SstDefaults
from .manager import ConfigManager
from .names import SstNames
from .paths import SstPaths
from .settings import SstSettings
from .setup import sst_config  # TODO: ConfigLoader?
