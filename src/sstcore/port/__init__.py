"""
Draw the Shape of the Core

- Resolve Dependency issues by inverting them
- Sketch and Annotate specialized objects
- Document the Library from the Central
                                         DependencyLevel.sstcore[0]
"""

__all__: list[str] = [  # TODO: activate __getattr__ when StubWriter done
    # "SstSystem",
    # "CliSystem",
    "SstError",
]


# NEXT: from .system import CliSystem, SstSystem
from ._error import SstError
