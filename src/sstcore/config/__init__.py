"""
Provide Configuration Pipeline with global access and json support

- ConfigManger: orchestrate the setup and provide global access
  - Settings: bind the components and bridge to json
  - Paths: assemble and ensure filesystem locations
  - Defaults: provide default values and parameter
  - Names: provide static and dynamic parsed names

                                                       DependencyLevel[X]
"""

__all__: list = [
    "ConfigManager",
    "SstSettings",
    "SstPaths",
    "SstDefaults",
    "SstNames",
]

from ._defaults import SstDefaults
from ._manager import ConfigManager
from ._names import SstNames
from ._paths import SstPaths
from ._settings import SstSettings
