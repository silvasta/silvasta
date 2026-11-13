"""
Define Fields for Enums

- Mounted to SstEnums or BuiltIns
"""

__all__: list[str] = [
    "EnumField",
    "BoundEnumField",
    "EnumFieldLoader",
]


from collections.abc import Callable, Mapping
from enum import Enum
from importlib import import_module
from types import ModuleType
from typing import Any, Protocol, Self, overload, runtime_checkable

from ..empty import VOID, MayBe, MayNot


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
        # AI: here another definition of the Cache Pattern
        # - the name _slots is way more confusing than helpful
        # - 1 custom Mapping that absorbs this and _slot_for?
        # - a simple helper class that governs this logic and works reliable
        self._slots: dict[type[Any], BoundEnumField[Any, ValueT]] = {}

    def _slot_for[E: Enum](self, owner: type[E]) -> BoundEnumField[E, ValueT]:
        """Provide per owner cached Field and load if needed"""
        if owner not in self._slots:
            self._slots[owner] = BoundEnumField(
                owner=owner,
                name=self._name,
                loader=self._loader,
                default=self._default,
                fallback=self._fallback,
            )
        return self._slots[owner]

    def __set_name__(self, owner: type[Any], name: str) -> None:
        self._name: str = name
        self._slot_for(owner)  # REMOVE: ??

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
        slot: BoundEnumField[E, ValueT] = self._slot_for(owner)
        return slot if member is None else slot.get(member)

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
    def from_module(  # RENAME: 1 word: module, extracting, loading, importing, ...
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


class BoundEnumField[EnumT: Enum, ValueT]:
    """Per-Enum-class storage, lazy loader, and validator for EnumField"""

    def __init__(
        self,
        owner: type[EnumT],
        name: str,
        loader: MayNot[EnumFieldLoader[EnumT, ValueT]] = None,
        default: MayBe[ValueT] = VOID,
        fallback: MayNot[Callable[[EnumT], ValueT]] = None,
    ) -> None:
        self.owner: type[EnumT] = owner
        self.name: str = name
        self._loader: MayNot[EnumFieldLoader[EnumT, ValueT]] = loader
        self._default: MayBe[ValueT] = default
        self._fallback: MayNot[Callable[[EnumT], ValueT]] = fallback
        self._data: dict[EnumT, ValueT] = {}
        self._loader_ran: bool = loader is None  # CHECK: why?

    @property
    def is_loaded(self) -> bool:
        return self._loader_ran and (  # CHECK: why not 'loader is None' here?
            bool(self._data)
            or self._default is not VOID
            or self._fallback is not None
        )

    def __str__(self):
        return f"{self.owner.__name__}.{self.name}"

    def __repr__(self):
        return f"{self}[{self._loader=},{self._default=},{self._data=}]"

    def bind_loader(
        self, loader: EnumFieldLoader[EnumT, ValueT]
    ) -> EnumFieldLoader[EnumT, ValueT]:
        """Attach Lazy Loader externally (e.g. as decorator)"""
        self._loader: EnumFieldLoader[EnumT, ValueT] = loader
        self._loader_ran = False  # CHECK: is there no smart solution for this?
        return loader

    def get(self, member: EnumT) -> ValueT:
        """Fetch Member Data or Fallback or use Default or Raise"""
        self._ensure_loaded()
        try:
            return self._data[member]
        except KeyError:
            if self._fallback is not None:
                return self._fallback(member)
            if self._default is not VOID:
                return self._default
            raise RuntimeError(f"Missing Data for {member} on {self}") from None

    def register(
        self,
        mapping: Mapping[EnumT, ValueT] | None = None,
        /,
        **by_name: ValueT,
    ) -> None:
        """Update cached data by Enum member mapping or directly by  member name kwargs"""
        # AI: this functionality could as well be absorbed by the CacheMap
        # - define once how it works inside the centralized base
        # - expose it here with 1 or a few lines
        if mapping:
            self._data.update(mapping)
        if by_name:
            members: dict[str, EnumT] = self.owner._member_map_  # ty:ignore - better than cast
            for key, value in by_name.items():
                try:
                    member: EnumT = members[key]
                except KeyError:
                    raise KeyError(f"{self}: unknown member {key!r}") from None
                self._data[member] = value

    def validate(self) -> None:
        """Ensure 1-to-1 coverage between Enum members and registered values."""
        self._ensure_loaded()
        required: set[EnumT] = set(self.owner)
        allowed: set[EnumT] = set(self.owner._member_map_.values())  # ty:ignore - better than cast
        actual: set[EnumT] = set(self._data)

        if missing := required - actual:
            names: str = ", ".join(m.name or str(m) for m in missing)
            raise ValueError(f"{self} Missing for Members: {names}")

        if extra := actual - allowed:
            raise ValueError(f"{self} Unknown Keys: {extra}")

    def _ensure_loaded(self) -> None:
        if self._loader_ran or (loader := self._loader) is None:
            return
        self._loader_ran = True  # AI: this hould be done somehow better...
        self.register(loader())
