"""
Define the Shape of the Core

Check here:
- Blueprint of any important structure

Purpose:
- Dependency Resolution
- Definition and Typing
- Documentation
                                                 DependencyLevel[0]
"""  # TODO: doc

__all__: list[str] = [  # IMPORTANT: make this work again
    "System",
    "SstSystem",
]
from .system import SstSystem, System
