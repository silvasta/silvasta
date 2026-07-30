"""
Install the System

                                                       DependencyLevel[X]
"""

__all__: list[str] = [
    "System",
    "SystemLoader",
    "sst_system_loader",
]


from ._core import System, SystemLoader, sst_system_loader
