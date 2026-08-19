"""
Define the Shape of the Core

Check here:
- Blueprint of any important structure

Purpose:
- Dependency Resolution
- Definition and Typing
- Documentation
                                                       DependencyLevel[0]
"""

__all__: list[str] = [
    "System",
    "SstSystem",
    "CliSystem",
]

from .system import CliSystem, SstSystem, System
