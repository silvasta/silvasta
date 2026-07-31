"""
Define Home Directories relative to the selected setup and system configuration

                                                       DependencyLevel[1]
"""

from ._homes import HomeSetup
from ._xdg import XdgDefaults, XdgHomes

__all__: list = [
    "HomeSetup",
    "XdgDefaults",
    "XdgHomes",
]
