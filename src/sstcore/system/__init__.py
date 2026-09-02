"""
Install the System

Check:
- sstcore.system.boot for all Loaders
- sstcore.system.event for Bus and Emitter

For Scripts and small Projects:
- sstcore.system.globals for wireless setup
                                                       DependencyLevel[4]
"""

__all__: list[str] = [
    "System",
    "SstSystem",
]


from ._core import SstSystem, System
