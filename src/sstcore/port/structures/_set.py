"""
Create immutable, identifiably container

                     DependencyLevel.sstcore.port.structures[0.1.0]
"""

__all__: list[str] = [
    "NormSet",
    "DunderSet",
    "KeySet",  # REMOVE:
    "FieldSet",
]


from collections.abc import Mapping, MutableMapping
from dataclasses import fields
from functools import cache
from typing import Any, ClassVar, Protocol, Self, TypeGuard

from .._types import _Stringable, _Stringables
from ..empty import MayNot


class _DataClass(Protocol):
    """Define the minimal Shape for typing a DataClass"""

    __dataclass_fields__: ClassVar[dict[str, Any]]


type DataClassOrType = _DataClass | type[_DataClass]


class NormSet(frozenset[str]):
    """
    Normalize Inputs on FrozenSet creation and lookups

    For any new data-retrieval methods added to NormSet:
      - Route through __contains__ to trigger subclass-specific validation!

    """

    _normstate: dict[str, Any]

    def __new__(cls, items: _Stringables = (), /, **kwargs) -> Self:
        _items = (cls.normalize(item, **kwargs) for item in items)
        unit: Self = super().__new__(cls, _items)
        unit._normstate = kwargs or {}
        return unit

    def __call__(
        self, item: _Stringable, /, default: MayNot[str] = None
    ) -> str | None:
        """Get normalized Item if it matches the Set"""
        return self._norm(item) if item in self else default

    def __contains__(self, target: Any) -> bool:
        """Does the Target fulfill the internal Conditions?"""
        return super().__contains__(self._norm(target))

    def _norm(self, item: _Stringable, /) -> str:
        """Inject NormState (kwargs) into classmethod normalizer"""
        return self.normalize(item, **self._normstate)

    @classmethod
    def normalize(cls, item: _Stringable, /) -> str:
        """Subhook for String Transformation"""
        return f"{item}"


class DunderSet(NormSet):
    @classmethod
    def normalize(cls, item: _Stringable, /) -> str:
        """Ensure storage in FrozenSet with '__dunder__' formatting"""
        return f"__{f'{item}'.strip('_')}__"


class KeySet(NormSet):  # REMOVE: when FieldSet is fine
    """Store Normalized Keys and match them against incoming Values"""

    def __new__(cls, items: _Stringables = (), /, prefix: str = "") -> Self:
        return super().__new__(cls, items, prefix=prefix)

    def __contains__(self, target: Any):
        if prefix := self._normstate.get("prefix"):
            if not f"{target}".startswith(prefix):
                return False
        return super().__contains__(target)

    @classmethod
    def normalize(cls, item: _Stringable, *, prefix: str = "") -> str:
        return f"{item}".removeprefix(prefix)


class FieldSet(NormSet):
    """
    Store canonical field names to match and extract inputs.

    - Cache field sets per DataClass type
    - Support dynamic prefix matching without mutating canonical names
    - Pluck from MutableMappings and Pull from partial DataClass instances

    """

    def __new__(cls, items: _Stringables = (), /, prefix: str = "") -> Self:
        return super().__new__(cls, items, prefix=prefix)

    def __contains__(self, target: Any) -> bool:
        if (prefix := self.prefix) and not f"{target}".startswith(prefix):
            return False
        return super().__contains__(target)

    @classmethod
    def normalize(cls, item: _Stringable, *, prefix: str = "") -> str:
        return f"{item}".removeprefix(prefix)

    @classmethod
    @cache
    def _absorb(cls, target: DataClassOrType) -> Self:
        """Cache canonical field names once per DataClass"""
        return cls(field.name for field in fields(target))

    @classmethod
    def absorb(cls, target: DataClassOrType, /, *, prefix: str = "") -> Self:
        """Retrieve cached FieldSet for a DataClass class or instance."""
        return cls._absorb(
            target if isinstance(target, type) else type(target)
        ).with_prefix(prefix)

    @property
    def prefix(self) -> str:
        return self._normstate.get("prefix", "")

    def with_prefix(self, prefix: str = "") -> Self:
        """FieldSet with new lookup prefix without re-stripping stored keys"""
        if prefix == self.prefix:
            return self
        unit: Self = frozenset.__new__(type(self), self)
        unit._normstate = {**self._normstate, "prefix": prefix}
        return unit

    #  LINE: -- Gate Keeper -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    def pluck(
        self,
        data: Mapping[str, Any],
        /,
        *,
        prefix: str = "",
        destroy: bool = True,
    ) -> dict[str, Any]:
        """Shallow Extract (and destroy) matching keys from mapping"""
        _gate = self.with_prefix(prefix) if prefix else self
        _extract = data.pop if destroy and _mutable(data) else data.__getitem__
        _keys = tuple(data) if destroy else data
        return {
            valid_key: _extract(raw_key)
            for raw_key in _keys
            if (valid_key := _gate(raw_key))
        }

    def pull(self, *specs: _DataClass) -> dict[str, Any]:
        """Shallow Collect matching field values from partial DataClass specs"""
        return {
            name: getattr(spec, name)
            for spec in specs
            for name in (self & self.absorb(spec))
        }


def _mutable(data: Mapping, /) -> TypeGuard[MutableMapping]:
    return isinstance(data, MutableMapping)
