"""
Define Fields for Enums

- Mounted to SstEnums or BuiltIns
"""

__all__: list[str] = [
    "EnumField",
    "BoundEnumField",
    "EnumFieldLoader",
]


from collections.abc import Mapping
from enum import Enum
from importlib import import_module
from types import ModuleType
from typing import Any, Protocol, overload, runtime_checkable

from ..empty import VOID, MayBe, MayNot

type _Bound[EnumT: Enum, ValueT] = BoundEnumField[EnumT, ValueT]


@runtime_checkable
class EnumFieldLoader[E: Enum, Value: Any](Protocol):
    def __call__(self) -> Mapping[E, Value]:
        """Prepare Enum Data for Field"""


class EnumField[ValueT]:
    """Typed, late-bindable descriptor usable on any Enum or IntFlag."""

    def __init__(
        self,
        *,
        # CHECK: str Loader?
        # CHECK: Enum for loader Parametrisation?
        loader: MayNot[EnumFieldLoader[Any, ValueT] | str] = None,
        default: MayBe[ValueT] = VOID,
    ) -> None:
        self._loader: MayNot[EnumFieldLoader[Any, ValueT] | str] = loader
        self._default: MayBe[ValueT] = default
        self._name: str = ""
        self._slots: dict[type[Any], BoundEnumField[Any, ValueT]] = {}

    def __set_name__(self, owner: type[Any], name: str) -> None:
        self._name: str = name
        self._slot_for(owner)

    def _slot_for[E: Enum](self, owner: type[E]) -> _Bound[E, ValueT]:
        """Provide per owner cached Field and load if needed"""
        if owner not in self._slots:
            self._slots[owner] = BoundEnumField(
                owner=owner,
                name=self._name,
                loader=self._loader,
                default=self._default,
            )
        return self._slots[owner]

    @overload
    def __get__[E: Enum](
        self, member: None, owner: type[E]
    ) -> _Bound[E, ValueT]: ...
    @overload
    def __get__(self, member: Enum, owner: type[Any]) -> ValueT: ...
    def __get__[E: Enum](
        self, member: E | None, owner: type[E]
    ) -> _Bound[E, ValueT] | ValueT:
        """Provide BoundEnumField for Field or extracted Value per Member"""
        slot: _Bound[E, ValueT] = self._slot_for(owner)
        return slot if member is None else slot.get(member)


class BoundEnumField[EnumT: Enum, ValueT]:
    """Per-Enum-class storage, lazy loader, and validator for an EnumField."""

    def __init__(
        self,
        owner: type[EnumT],
        name: str,
        loader: MayNot[EnumFieldLoader[EnumT, ValueT] | str] = None,
        default: MayBe[ValueT] = VOID,
    ) -> None:
        self.owner: type[EnumT] = owner
        self.name: str = name
        self._loader: MayNot[EnumFieldLoader[EnumT, ValueT] | str] = loader
        self._default: MayBe[ValueT] = default
        self._data: dict[EnumT, ValueT] = {}
        self._is_loaded: bool = loader is None

    @property
    def is_loaded(self) -> bool:
        # REMOVE: ?? or use?
        return self._is_loaded and bool(self._data)

    def __str__(self):
        return f"{self.owner.__name__}.{self.name}"

    def __repr__(self):
        return f"{self}[{self._loader=},{self._default=},{self._data=}]"

    def get(self, member: EnumT) -> ValueT:
        self._ensure_loaded()
        try:
            return self._data[member]
        except KeyError:
            if self._default is not VOID:
                return self._default
            raise RuntimeError(f"Missing Data for {member} on {self}") from None

    def register(
        self,
        mapping: Mapping[EnumT, ValueT] | None = None,
        /,
        **by_name: ValueT,
    ) -> None:
        """Populate metadata by Enum member mapping and/or member name kwargs."""
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
        self._is_loaded = True  # WARN: this looks very fragile...

    def validate(self) -> None:
        """Ensure 1-to-1 coverage between Enum members and registered values."""
        self._ensure_loaded()
        expected: set[EnumT] = set(self.owner)
        actual: set[EnumT] = set(self._data)

        if missing := expected - actual:
            names: str = ", ".join(m.name for m in missing)
            raise ValueError(f"{self} Missing for Members: {names}")

        if extra := actual - expected:
            raise ValueError(f"{self} Unknown Keys: {extra}")

    def _ensure_loaded(self) -> None:
        if self._is_loaded or (loader := self._loader) is None:
            # TODO: merge with is_loaded?
            return
        if isinstance(loader, str):
            _module_path, _attr_name = loader.split(":")
            mod: ModuleType = import_module(_module_path)
            self.register(getattr(mod, _attr_name))
            return
        elif isinstance(loader, EnumFieldLoader[EnumT, ValueT]):
            self.register(loader())
        else:
            raise TypeError(f"Unknown {loader=} for Field: {self}!")
