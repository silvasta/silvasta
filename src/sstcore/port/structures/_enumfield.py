"""
Define Fields for Enums

- Mounted to SstEnums or BuiltIns
"""

__all__: list[str] = [
    "EnumMemberMap",
    "EnumFieldMap",
    "EnumFieldLoader",
    "EnumField",
]


from collections.abc import Mapping
from enum import Enum
from typing import (
    Any,
    ClassVar,
    Protocol,
    Self,
    Unpack,
    overload,
    runtime_checkable,
)

from .._modulepath import ModulePath
from ..empty import MayNot
from ..primitives import Loader, Loading
from ._gate import GateRaiser, LazyMap, MapGate


@runtime_checkable
class EnumFieldLoader[E: Enum, Value: Any](Protocol):
    def __call__(self) -> Mapping[E, Value]:
        """Prepare Enum Data for Field"""


class EnumMemberMap[E: Enum, V](LazyMap[E, V]):
    """Store not shared Data for single Enum Member per Field or BoundField"""

    def __init__(
        self,
        owner: type[E],
        name: str = "",
        *,
        source: MayNot[Loading[[], Mapping[Any, V]]] = None,
        fallback: MayNot[Loading[[E], V]] = None,
        cache_fallback: bool = False,
        **tkw: Unpack[Loader.Input[V]],
    ) -> None:
        super().__init__(
            source=source,
            fallback=fallback,
            cache_fallback=cache_fallback,
            **tkw,
        )
        self.owner: type[E] = owner
        self.name: str = name
        self.label: str = f"{owner.__name__}.{name}" if name else owner.__name__

    def locksmith(self, key: Any) -> E:
        if isinstance(key, self.owner):
            return key
        if isinstance(key, str):
            try:
                return self.owner._member_map_[key]  # ty:ignore
            except KeyError as error:
                raise GateRaiser.enum_member(self.label, key) from error
        raise GateRaiser.enum_type(
            self.label, self.owner.__name__, type(key).__name__
        )

    def bind_loader(self, fn: EnumFieldLoader[E, V]) -> EnumFieldLoader[E, V]:
        """Attach or replace the bulk lazy loader (usable as a decorator)."""
        return self.source.bind(fn)

    def validate(self, *, strict: bool = False) -> None:
        """
        Hydrate and verify Member coverage - unknown keys always raise

        - Missing members raise unless a fallback or default is configured
          (pass strict=True to enforce 1-to-1 coverage).

        """
        self.hydrate()
        allowed: set[E] = set(self.owner._member_map_.values())  # ty:ignore
        actual: set[E] = set(self._data)

        if extra := {  # CHECK:
            m for m in (actual - allowed) if not isinstance(m, self.owner)
        }:
            names: str = ", ".join(str(m) for m in extra)
            raise GateRaiser.enum_extra(self.label, names)

        if strict or not self.fallback.is_ready:
            required: set[E] = set(self.owner)
            if missing := required - actual:
                names: str = ", ".join(m.name or str(m) for m in missing)
                raise GateRaiser.enum_missing(self.label, names)


class EnumField[T]:
    """Setup independent Descriptor per EnumCls with Lazy data binding"""

    def __init__(
        self,
        *,
        source: MayNot[
            Loader[[], Mapping[Any, T]] | EnumFieldLoader[Any, T]
        ] = None,
        fallback: MayNot[Loading[[Any], T]] = None,
        cache_fallback: bool = False,
        **tkw: Unpack[Loader.Input[T]],
    ) -> None:
        self._source: Loader[[], Mapping[Any, T]] = Loader.loading(source)
        self._fallback: Loader[[Any], T] = Loader.loading(fallback, **tkw)
        self._cache_fallback: bool = cache_fallback
        self._name: str = ""

        # AI: this was before, the EnumMemberMap should replace the LazyMap!
        # self._slots: LazyMap[type[Enum], EnumMemberMap[Any, T]] = LazyMap(
        #     self._make_slot,
        #     mode="item",
        #     cache_fallback=True,
        # )
        self._owner: type[Any] = Enum
        # AI_TASK: replacing exactly this _slots:dict by a Map was the purpose of the entire Map project
        # - analyze the _gate.MapGate->LazyMap->EnumMemberMap pipeline
        # - fix this issue below with the proper mapping
        self._slots: dict[type[Enum], EnumMemberMap[Any, T]] = {}

    def __set_name__(self, owner: type[Any], name: str) -> None:
        self._owner: type[Any] = owner
        self._name: str = name

    def __str__(self):
        return f"{self._owner.__name__}.{self._name}"

    def _make_slot[E: Enum](self, owner: type[E]) -> EnumMemberMap[E, T]:
        return EnumMemberMap(
            owner=owner,
            name=self._name,
            source=self._source.clone(),
            fallback=self._fallback.clone(),
            cache_fallback=self._cache_fallback,
        )

    @overload
    def __get__[E: Enum](
        self, member: None, owner: type[E]
    ) -> EnumMemberMap[E, T]: ...
    @overload
    def __get__(self, member: Enum, owner: type[Any]) -> T: ...
    def __get__[E: Enum](
        self, member: E | None, owner: type[E]
    ) -> EnumMemberMap[E, T] | T:
        """Return EnumMemberMap on class access, or resolve member value."""
        slot: EnumMemberMap[E, T] = self._slots[owner]
        return slot if member is None else slot[member]

    @classmethod
    def imports(
        cls,
        path: ModulePath,
        *,
        call_it: bool = False,
        fallback: MayNot[Loading[[Any], T]] = None,
        cache_fallback: bool = False,
        **tkw: Unpack[Loader.Input[T]],
    ) -> Self:
        """Create lazy field via deferred 'module.path:Attr' resolution."""
        return cls.lazy(
            path.lazy_loader(call_if_callable=call_it),
            fallback=fallback,
            cache_fallback=cache_fallback,
            **tkw,
        )

    @classmethod
    def lazy(
        cls,
        loader: Loader[[], Mapping[Any, T]] | EnumFieldLoader[Any, T],
        *,
        fallback: MayNot[Loading[[Any], T]] = None,
        cache_fallback: bool = False,
        **tkw: Unpack[Loader.Input[T]],
    ) -> Self:
        """Create lazy field backed by a zero-arg bulk table loader."""
        return cls(
            source=loader,
            fallback=fallback,
            cache_fallback=cache_fallback,
            **tkw,
        )


class EnumFieldMap[E: Enum](MapGate[str, EnumMemberMap[E, Any]]):
    """Per-EnumCls map of field_name -> EnumMemberMap with global registry."""

    _registry: ClassVar[list[EnumFieldMap]] = []

    def __init__(self, owner: type[E], /) -> None:
        self.owner: type[E] = owner
        super().__init__(
            {
                name: getattr(owner, name)
                for base in reversed(owner.__mro__)
                for name, attr in vars(base).items()
                if isinstance(attr, EnumField)
            }
        )
        if self and len(owner) > 0:
            self._registry.append(self)

    @property
    def is_ready(self) -> bool:
        return all(slot.is_loaded for slot in self.values())

    def validate(self, *, strict: bool = False) -> None:
        """Hydrate and validate all EnumMemberMaps attached to this Enum class."""
        for slot in self.values():
            slot.validate(strict=strict)

    @classmethod
    def validate_all(cls, *, strict: bool = False) -> None:
        """Hydrate and validate every registered EnumField across sstcore."""
        for field_map in cls._registry:
            print(f"{field_map=}")
            field_map.validate(strict=strict)
