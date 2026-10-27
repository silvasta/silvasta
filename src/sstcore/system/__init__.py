"""
Install the System

- boot: all Loaders
- event: Bus and Emitter

For Scripts and small Projects:
- globals: wireless setup

                                         DependencyLevel.sstcore[5]
"""

__all__: list[str] = [
    "System",
    "SstSystem",
]


from ._core import SstSystem, System
