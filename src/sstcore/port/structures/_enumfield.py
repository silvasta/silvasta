"""
Define Fields for Enums

- Mounted to SstEnums or BuiltIns
"""

__all__: list[str] = [
    "EnumMemberMap",
    "EnumSlot",
    "EnumField",
    "EnumFieldMap",
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


# AI: this is enum map type 1, the member registry
class EnumMemberMap[E: Enum, V](LazyMap):
    """Store not shared Data for single Enum Member per Field or BoundField"""

    _registry: ClassVar[list[EnumMemberMap]] = []

    def __init__(
        self,
        owner: type[E],
        label: str = "",
        *,
        fallback: Loading[[E], V] | None = None,
        source: Loading[[], Mapping[Any, V]] | None = None,
        cache_fallback: bool = False,
        **tkw: Unpack[Loader.Input[V]],
    ) -> None:
        super().__init__(
            # FIX: something with self.source is wrong
            fallback,
            source=source,
            cache_fallback=cache_fallback,
            **tkw,
        )
        self.owner: type[E] = owner
        self.label: str = label or owner.__name__

    @property
    def is_ready(self) -> bool:
        return all(field.is_loaded for field in self.values())

    def locksmith(self, key: Any) -> E:
        if type(key) is self.owner:
            return key
        if isinstance(key, str):
            try:
                return self.owner._member_map_[key]  # ty:ignore
            except KeyError as error:
                raise GateRaiser.enum_member(self.label, key) from error
        raise GateRaiser.enum_type(
            self.label, self.owner.__name__, type(key).__name__
        )

    def validate(self):
        """Ensure all Enum Members on this Cls are Loaded and Valid"""
        for field in self.values():
            field.validate()

    @classmethod
    def validate_all(cls) -> None:
        """Ensure all Enum Fields are Loaded and Valid"""
        for field_map in cls._registry:
            field_map.validate()


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


# AI: unsure if this one is required, maybe merge with upper
class EnumSlot[EnumT: Enum, T](EnumMemberMap[EnumT, T]):
    """Per-Enum-class bound storage, lazy hydrator, and validator."""

    def __init__(
        self,
        owner: type[EnumT],
        name: str,
        *,
        source: Loader[[], Mapping[Any, T]] | None = None,
        fallback: Loader[[EnumT], T] | None = None,
    ) -> None:
        super().__init__(
            owner=owner,
            label=f"{owner.__name__}.{name}",
            source=source,
            fallback=fallback,
            cache_fallback=False,
        )
        self.name: str = name

    @property
    def is_loaded(self) -> bool:
        """True once no bulk source is pending and data or fallback exists."""
        # FIX: something with self.source is wrong
        source_done: bool = not self.source or self.source.is_ready
        return source_done and (bool(self._data) or bool(self.fallback))

    def bind_loader(
        self, fn: EnumFieldLoader[EnumT, T]
    ) -> EnumFieldLoader[EnumT, T]:
        """Attach or replace the bulk lazy loader (usable as a decorator)."""
        return self.source.bind(fn)

    def validate(self, *, strict: bool = False) -> None:
        """Hydrate and verify member coverage.

        Unknown keys always raise. Missing members raise unless a fallback or
        default is configured (pass strict=True to enforce 1-to-1 coverage).
        """
        self.hydrate()
        allowed: set[EnumT] = set(self.owner._member_map_.values())  # ty:ignore
        actual: set[EnumT] = set(self._data)

        if extra := actual - allowed:
            raise GateRaiser.enum_extra(self.label, extra)

        if strict or not self.fallback:
            required: set[EnumT] = set(self.owner)
            if missing := required - actual:
                names: str = ", ".join(m.name or str(m) for m in missing)
                raise GateRaiser.enum_missing(self.label, names)


# AI: the field to mount it
class EnumField[T]:
    """Setup independent Descriptor per EnumCls with Lazy data binding"""

    def __init__(
        self,
        *,
        source: MayNot[
            Loader[[], Mapping[Any, T]] | EnumFieldLoader[Any, T]
        ] = None,
        fallback: MayNot[Loader[[Any], T] | Loading[[Any], T]] = None,
        **tkw: Unpack[Loader.Input[T]],
    ) -> None:
        self._source: Loader[[], Mapping[Any, T]] = (
            source if isinstance(source, Loader) else Loader(source)
        )
        self._fallback: Loader[[Any], T] = (
            fallback.update(**tkw)
            if isinstance(fallback, Loader)
            else Loader(fallback, **tkw)
        )
        self._name: str = ""
        self._slots: LazyMap[Enum, EnumSlot[Any, T]] = LazyMap(
            self._make_slot, cache_fallback=True
        )

    def __set_name__(self, owner: type[Any], name: str) -> None:
        _ = owner
        self._name = name

    def _make_slot[E: Enum](self, owner: type[E]) -> EnumSlot[E, T]:
        return EnumSlot(
            owner=owner,
            name=self._name,
            source=self._source.clone(),
            fallback=self._fallback.clone(),
        )

    @overload
    def __get__[E: Enum](
        self, member: None, owner: type[E]
    ) -> EnumSlot[E, T]: ...
    @overload
    def __get__(self, member: Enum, owner: type[Any]) -> T: ...
    def __get__[E: Enum](
        self, member: E | None, owner: type[E]
    ) -> EnumSlot[E, T] | T:
        """Return EnumSlot on class access, or resolve member value."""
        slot: EnumSlot[E, T] = self._slots[owner]
        return slot if member is None else slot[member]

    @classmethod
    def imports(
        cls,
        path: ModulePath,
        *,
        call_it: bool = False,
        fallback: MayNot[Loading[[Any], T]] = None,
        **tkw: Unpack[Loader.Input[T]],
    ) -> Self:
        """Create lazy field via deferred 'module.path:Attr' resolution."""
        return cls.lazy(
            path.lazy_loader(call_if_callable=call_it),
            fallback=fallback,
            **tkw,
        )

    @classmethod
    def lazy(
        cls,
        loader: Loader[[], Mapping[Any, T]] | EnumFieldLoader[Any, T],
        *,
        fallback: MayNot[Loader[[Any], T] | Loading[[Any], T]] = None,
        **tkw: Unpack[Loader.Input[T]],
    ) -> Self:
        """Create lazy field backed by a zero-arg bulk table loader."""
        return cls(source=loader, fallback=fallback, **tkw)


# AI: this is enum map type 2, for the meta registry
class EnumFieldMap[E: Enum](MapGate[E, EnumSlot[Any, Any]]):
    """Per-EnumCls map of field_name -> EnumSlot with global registry."""

    _registry: ClassVar[list[EnumFieldMap]] = []

    def __init__(self, owner: type[Enum]) -> None:
        super().__init__(
            {
                name: getattr(owner, name)
                for base in reversed(owner.__mro__)
                for name, attr in vars(base).items()
                if isinstance(attr, EnumField)
            }
        )
        self.owner: type[Enum] = owner
        if self and len(owner) > 0:
            self._registry.append(self)

    @property
    def is_ready(self) -> bool:
        return all(slot.is_loaded for slot in self.values())

    def validate(self, *, strict: bool = False) -> None:
        """Hydrate and validate all EnumSlots attached to this Enum class."""
        for slot in self.values():
            slot.validate(strict=strict)

    @classmethod
    def validate_all(cls, *, strict: bool = False) -> None:
        """Hydrate and validate every registered EnumField across sstcore."""
        for field_map in cls._registry:
            field_map.validate(strict=strict)
