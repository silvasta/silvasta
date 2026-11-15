from collections.abc import Callable, Iterator, Mapping, MutableMapping
from enum import Enum
from typing import Any

from src.sstcore.port.empty import VOID
from src.sstcore.port.structures._cachemapg4 import (
    BoundEnumField,
    EnumFieldLoader,
)


class LazyMap[K, V](dict[K, V]):
    """Centralized lazy cache/registry.

    Absorbs the repeated "if key not in self: self[key] = create(...)" pattern
    seen in CachedDataclassMeta._cache and EnumField._slots.

    Two supported styles (both keep intent readable):
    1. Factory at construction (`map[key]` triggers __missing__).
    2. Context-specific factory (`get_or_create(key, lambda: ...)`).

    Follows structures philosophy (like FieldSet, HashedTuple, NormSet):
    - Small, focused, extensible via subclassing.
    - Can later grow validated registries, weakref support, hit-rate stats, etc.
    """

    def __init__(self, factory: Callable[[K], V] | None = None) -> None:
        super().__init__()
        self._factory = factory

    def __missing__(self, key: K) -> V:
        if self._factory is None:
            raise KeyError(key)
        value: V = self._factory(key)
        self[key] = value
        return value


class GateMap[K, V](MutableMapping[K, V]):
    """
    Dict whose read and write paths share one admission rule.

    Does not invent values. Call sites keep:

        if key not in store:
            store[key] = build(...)
        return store[key]

    Override admit() the way NormSet overrides normalize().
    admit() must be pure. Every new writer must go through __setitem__.
    """

    __slots__ = ("_data",)

    def __init__(self) -> None:
        self._data: dict[K, V] = {}

    def admit(self, key: Any) -> K:
        """Subhook. Return the storage key, or raise KeyError/TypeError."""
        return key

    def __getitem__(self, key: Any) -> V:
        return self._data[self.admit(key)]

    def __setitem__(self, key: Any, value: V) -> None:
        self._data[self.admit(key)] = value

    def __delitem__(self, key: Any) -> None:
        del self._data[self.admit(key)]

    def __contains__(self, key: object) -> bool:
        try:
            admitted: K = self.admit(key)
        except KeyError, TypeError:
            return False
        return admitted in self._data

    def __iter__(self) -> Iterator[K]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __str__(self) -> str:
        return f"{type(self).__name__}[{len(self)}]"


class MemberMap[E: Enum, V](GateMap[E, V]):
    """Store by member. Accept the member or its enum name."""

    __slots__ = ("owner", "label")

    def __init__(self, owner: type[E], label: str = "") -> None:
        super().__init__()
        self.owner: type[E] = owner
        self.label: str = label or owner.__name__

    def admit(self, key: Any) -> E:
        if type(key) is self.owner:
            return key
        if isinstance(key, str):
            try:
                return self.owner._member_map_[key]  # ty:ignore
            except KeyError:
                raise KeyError(
                    f"{self.label}: unknown member {key!r}"
                ) from None
        raise TypeError(
            f"{self.label}: expected {self.owner.__name__} or name, "
            f"got {type(key).__name__}"
        )

    def register(
        self, mapping: Mapping[E | str, V] | None = None, /, **by_name: V
    ) -> None:
        if mapping:
            for key, value in mapping.items():
                self[key] = value
        if by_name:
            for key, value in by_name.items():
                self[key] = value


class Enu[EnumT, ValueT]:
    # self._data: MemberMap[EnumT, ValueT] = MemberMap(owner, label=name)

    def register(self, mapping=None, /, **by_name: ValueT) -> None:
        self._data.register(mapping, **by_name)

    def get(self, member: EnumT) -> ValueT:
        self._ensure_loaded()
        try:
            return self._data[member]
        except KeyError:
            if self._fallback is not None:
                return self._fallback(member)
            if self._default is not VOID:
                return self._default
            raise RuntimeError(f"Missing Data for {member} on {self}") from None

    # self._bound: dict[type, BoundEnumField[Any, ValueT]] = {}

    def _bound_to[E: Enum](self, owner: type[E]) -> BoundEnumField[E, ValueT]:
        if owner not in self._bound:
            self._bound[owner] = BoundEnumField(
                owner=owner,
                name=self._name,
                loader=self._loader,
                default=self._default,
                fallback=self._fallback,
            )
        return self._bound[owner]

    # self._consumed: bool = loader is None

    def bind_loader(self, loader: EnumFieldLoader) -> EnumFieldLoader:
        self._loader = loader
        self._consumed = False
        return loader

    def _ensure_loaded(self) -> None:
        if self._consumed or (loader := self._loader) is None:
            return
        self._consumed = True  # poison first: a raising loader does not retry
        self.register(loader())
