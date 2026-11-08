"""
DEFINE

                     DependencyLevel.sstcore.port.structures[0.1.0]
"""

__all__: list[str] = [
    "ParamSnap",
]
from typing import Any, NamedTuple


class ParamSnap(NamedTuple):
    """Track the ongoing Actions"""

    args: tuple[Any, ...]
    kwargs: dict[str, Any]

    def __str__(self):
        return f"args={self.args}, kwargs={self.kwargs}"

    def __repr__(self):
        return str(self)  # LATER: explain each (kw)arg
