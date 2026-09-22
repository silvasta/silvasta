"""
Directly operate at the targets 'Heart'

- Inspect (and modify?) object.__dict__

                             DependencyLevel.sstcore.brick.labor[0]
"""

__all__: list[str] = [
    "_dict",
]
from typing import Any

# TODO: Strategy for __dict__ operations
# - consider as well __slots__


def _dict(_target: Any, *, key: str) -> Any:
    """Direct __dict__ access"""
    return _target.__dict__[key]
