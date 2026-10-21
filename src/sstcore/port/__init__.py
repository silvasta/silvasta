"""
Draw the Shape of the Core

- Resolve Dependency issues by inverting them
- Sketch and Annotate specialized objects
- Document the Library from the Central
                                         DependencyLevel.sstcore[0]
"""

__all__: list[str] = [
    "SstSystem",
    "CliSystem",
]
from .system import CliSystem, SstSystem
