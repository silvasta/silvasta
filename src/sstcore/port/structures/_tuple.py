"""
Create immutable, identifiably container

                     DependencyLevel.sstcore.port.structures[0.1.1]
"""

__all__: list[str] = [
    "HashedTuple",
    "ParamSnap",
]


from collections.abc import Hashable, Mapping
from functools import partial
from typing import Any, NamedTuple, TypeIs

from ._map import frozendict


class ParamSnap(NamedTuple):
    """Capture and Visualize 1 Signature"""

    args: tuple[Any, ...]
    kwargs: dict[str, Any]

    def __str__(self):
        return f"args={self.args}, kwargs={self.kwargs}"

    def __repr__(self):
        return str(self)  # LATER: explain each (kw)arg


class _HashedTupleBase(NamedTuple):
    """Assign Attrs and Unlock __new__ for subclasses"""

    name: str
    value: Hashable


def is_hashittr(target: Hashable, /) -> TypeIs[tuple | frozenset | frozendict]:
    """Ensure and Annotate Target to be Hashable Iterable"""
    return isinstance(target, (tuple, frozenset, frozendict))


class HashedTuple(_HashedTupleBase):
    """Auto-Ensure Deterministic CacheKeys for Hashable Tuple"""

    def __new__(cls, name: str, value: Any, /, *, strict=True):
        """Make value Hashable before instantiation"""
        return tuple.__new__(cls, (name, cls.hash(value, strict=strict)))

    @staticmethod
    def accepts(target) -> bool:
        """Ultimate check if Hash can be generated"""
        try:
            hash(target)
            return True
        except TypeError:
            return False

    @staticmethod
    def hash(target: Any, /, *, strict=True) -> Hashable:
        """
        Transform Mutable and Nested Structures and Prove Hashability

        - Convert Set to FrozenSet and List to Tuple
        - Order any Map to deterministic FrozenDict
        - Final Attempt: Enforce Freeze
          - strict=False Generate some string without Raise

        """
        if HashedTuple.accepts(target):
            return target

        _hash = partial(HashedTuple.hash, strict=strict)

        match target:
            case list() | tuple():
                return tuple(_hash(value) for value in target)

            case set() | frozenset():
                return frozenset(_hash(value) for value in target)

            case Mapping():
                return frozendict(  # works with workaround for Python 3.14
                    {_hash(key): _hash(value) for key, value in target.items()}
                )
        return HashedTuple._fallback(target, strict=strict)

    @staticmethod
    def _fallback(target: Any, /, *, strict: bool = True) -> Hashable:
        """Make Target Hashable or Raise"""
        try:
            return tuple(HashedTuple.hash(x, strict=strict) for x in target)
        except TypeError as error:
            _target: str = HashedTuple._format(target)
            if not strict:
                return _target
            raise TypeError(f"Unhashable for Cache: {_target}") from error

    @staticmethod
    def _format(target):
        """Subhook for failed target in HashedTuple.hash"""
        return f"{type(target).__name__}::{target}"

    def __str__(self):
        return f"{type(self).__name__}{{{self.name}:{self._show}}}"

    @property
    def _show(self) -> str:
        """Subhook to format infos from HashedTuple.value"""
        length: str = f"[{len(self.value)}]" if is_hashittr(self.value) else ""
        return f"{type(self.value).__name__}{length}"
