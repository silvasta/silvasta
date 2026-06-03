from .defaults import SstDefaults
from .get_config import get_config
from .homes import HomeSetup
from .manager import ConfigManager, ConfigSetupParam, ConfigTypes
from .names import AutoParsedName, ParsedName, SstNames, StyledName
from .paths import SstPaths
from .settings import SstSettings


# IDEA: __call__ to get config?
def __getattr__(name):  # TEST:
    if name == "config":
        return get_config()
    raise AttributeError(name)


__all__: list = [
    "ConfigManager",
    "ConfigTypes",
    "get_config",
    "SstPaths",
    "SstSettings",
    "SstNames",
    "AutoParsedName",
    "ParsedName",
    "StyledName",
    "SstDefaults",
    "HomeSetup",
    "ConfigSetupParam",
]
