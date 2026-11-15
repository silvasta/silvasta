"""
Create Mapping Container with Key and Value

                     DependencyLevel.sstcore.port.structures[0.1.0]
"""

__all__: list[str] = [
    "frozendict",
    "CacheMap",
    "RegistryMap",
]

import sys
from collections.abc import Callable, Mapping
from enum import Enum
from importlib import import_module
from types import ModuleType
from typing import Any, Protocol, Self, overload, runtime_checkable

from ..empty import VOID, MayBe, MayNot

if sys.version_info >= (3, 15):
    from builtins import frozendict
else:

    class frozendict[K, V](Mapping[K, V]):  # noqa: N801
        ...  # (existing implementation)


class CacheMap[K, V](dict[K, V]):
    """
    Dict with key normalization and auto-populating __missing__ gate

    - C-speed lookup on cache hits
    - Delegate cache misses to factory hook and store result
    """

    def __init__(
        self,
        factory: MayNot[Callable[[K], V]] = None,
        /,
    ) -> None:
        super().__init__()
        self._factory: MayNot[Callable[[K], V]] = factory

    def __missing__(self, key: K) -> V:
        """Centralize the 'if not in -> load -> return' pattern"""
        if self._factory is None:
            raise KeyError(key)
        self[key] = value = self._factory(key)
        return value

    def resolve_key(self, key: Any, /) -> K:
        """Subhook to normalize or validate keys on registration"""
        return key

    def register(
        self,
        mapping: Mapping[Any, V] | None = None,
        /,
        **kwargs: V,
    ) -> Self:
        """Bulk-insert items from mapping and kwargs through resolve_key gate"""
        if mapping:
            for key, value in mapping.items():
                self[self.resolve_key(key)] = value
        for key, value in kwargs.items():
            self[self.resolve_key(key)] = value
        return self


class RegistryMap[K, V](CacheMap[K, V]):
    """
    Lazy-hydrating Registry with fallback and default resolution

    - Hydrate once on first miss, registration, or validation
    - Resolve unregistered keys via fallback callable or static default
    """

    def __init__(
        self,
        *,
        loader: MayNot[Callable[[], Mapping[Any, V]]] = None,
        default: MayBe[V] = VOID,
        fallback: MayNot[Callable[[K], V]] = None,
    ) -> None:
        super().__init__(fallback)
        self._loader: MayNot[Callable[[], Mapping[Any, V]]] = loader
        self._default: MayBe[V] = default

    @property
    def is_loaded(self) -> bool:
        """True when no loader is pending and data/fallback is available"""
        return self._loader is None and (
            bool(self) or self._default is not VOID or self._factory is not None
        )

    def bind_loader[L: Callable[[], Mapping[Any, Any]]](self, loader: L) -> L:
        """Attach or replace lazy loader (usable as decorator)"""
        self.clear()
        self._loader = loader
        return loader

    def _ensure_loaded(self) -> None:
        """Consume pending loader once and populate registry"""
        if (loader := self._loader) is not None:
            self._loader = None
            self.register(loader())

    def register(
        self,
        mapping: Mapping[Any, V] | None = None,
        /,
        **kwargs: V,
    ) -> Self:
        """Hydrate pending loader first so explicit entries always win"""
        self._ensure_loaded()
        return super().register(mapping, **kwargs)

    def __missing__(self, key: K) -> V:
        """Hydrate on first miss, then evaluate fallback or default"""
        if self._loader is not None:
            self._ensure_loaded()
            if key in self:
                return self[key]

        if self._factory is not None:
            return self._factory(key)
        if self._default is not VOID:
            return self._default

        raise RuntimeError(f"Missing data for {key!r} on {self}")

    def get(self, key: K, default: MayBe[V] = VOID) -> V:
        """Fetch value through __missing__ gate with optional call-site default"""
        try:
            return self[key]
        except KeyError, RuntimeError:
            if default is not VOID:
                return default
            raise


"""
Define Fields for Enums

- Mounted to SstEnums or BuiltIns
"""

__all__: list[str] = [
    "EnumField",
    "BoundEnumField",
    "EnumFieldLoader",
]


@runtime_checkable
class EnumFieldLoader[E: Enum, Value: Any](Protocol):
    def __call__(self) -> Mapping[E, Value]:
        """Prepare Enum Data for Field"""


class EnumField[ValueT]:
    """Setup independent Descriptor per EnumCls with Lazy data binding"""

    def __init__(
        self,
        *,
        default: MayBe[ValueT] = VOID,
        fallback: MayNot[Callable[[Any], ValueT]] = None,
    ) -> None:
        self._default: MayBe[ValueT] = default
        self._fallback: MayNot[Callable[[Any], ValueT]] = fallback
        self._loader: MayNot[EnumFieldLoader[Any, ValueT]] = None
        self._name: str = ""
        self._bindings: CacheMap[type[Any], BoundEnumField[Any, ValueT]] = (
            CacheMap(self._bind)
        )

    def _bind[E: Enum](self, owner: type[E]) -> BoundEnumField[E, ValueT]:
        """Factory for CacheMap to create per-owner BoundEnumField on miss"""
        return BoundEnumField(
            owner=owner,
            name=self._name,
            loader=self._loader,
            default=self._default,
            fallback=self._fallback,
        )

    def __set_name__(self, owner: type[Any], name: str) -> None:
        _ = owner
        self._name = name

    @overload
    def __get__[E: Enum](
        self, member: None, owner: type[E]
    ) -> BoundEnumField[E, ValueT]: ...
    @overload
    def __get__(self, member: Enum, owner: type[Any]) -> ValueT: ...
    def __get__[E: Enum](
        self, member: E | None, owner: type[E]
    ) -> BoundEnumField[E, ValueT] | ValueT:
        """Provide BoundEnumField for EnumCls or extract Value for Member"""
        binding: BoundEnumField[E, ValueT] = self._bindings[owner]
        return binding if member is None else binding[member]

    @classmethod
    def lazy(
        cls,
        loader: EnumFieldLoader[Any, ValueT],
        *,
        default: MayBe[ValueT] = VOID,
        fallback: MayNot[Callable[[Any], ValueT]] = None,
    ) -> Self:
        """Create Lazy Field with Zero-Arg Loader"""
        field: Self = cls(default=default, fallback=fallback)
        field._loader = loader
        return field

    @classmethod
    def locate(  # or `load`
        cls,
        target: str,
        *,
        default: MayBe[ValueT] = VOID,
        fallback: MayNot[Callable[[Any], ValueT]] = None,
    ) -> Self:
        """Create Lazy Field by 'module.path:ATTR' evaluation"""
        _module_path, _sep, _attr_name = target.partition(":")
        if not _sep or not _module_path or not _attr_name:
            raise ValueError(
                f"Expected 'module.path:ATTR' target, got {target!r}"
            )

        def _import_loader() -> Mapping[Any, ValueT]:
            mod: ModuleType = import_module(_module_path)
            obj: Any = getattr(mod, _attr_name)
            return obj() if callable(obj) else obj

        return cls.lazy(_import_loader, default=default, fallback=fallback)


class BoundEnumField[EnumT: Enum, ValueT](RegistryMap[EnumT, ValueT]):
    """Per-Enum-class storage, lazy loader, and validator for EnumField"""

    def __init__(
        self,
        owner: type[EnumT],
        name: str,
        loader: MayNot[EnumFieldLoader[EnumT, ValueT]] = None,
        default: MayBe[ValueT] = VOID,
        fallback: MayNot[Callable[[EnumT], ValueT]] = None,
    ) -> None:
        super().__init__(loader=loader, default=default, fallback=fallback)
        self.owner: type[EnumT] = owner
        self.name: str = name

    def __str__(self) -> str:
        return f"{self.owner.__name__}.{self.name}"

    def __repr__(self) -> str:
        return (
            f"{self}[loader={self._loader}, "
            f"default={self._default}, data={super().__repr__()}]"
        )

    def resolve_key(self, key: EnumT | str, /) -> EnumT:
        """Accept Enum member directly or resolve by member name"""
        if isinstance(key, self.owner):
            return key
        try:
            return self.owner._member_map_[key]  # ty:ignore
        except KeyError:
            raise KeyError(f"{self}: unknown member {key!r}") from None

    def validate(self) -> None:
        """Ensure 1-to-1 coverage between Enum members and registered values."""
        self._ensure_loaded()
        required: set[EnumT] = set(self.owner)
        allowed: set[EnumT] = set(self.owner._member_map_.values())  # ty:ignore
        actual: set[EnumT] = set(self)

        if missing := required - actual:
            names: str = ", ".join(m.name or str(m) for m in missing)
            raise ValueError(f"{self} Missing for Members: {names}")

        if extra := actual - allowed:
            raise ValueError(f"{self} Unknown Keys: {extra}")
