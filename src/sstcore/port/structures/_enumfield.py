"""
Define Fields for Enums

- Mounted to SstEnums or BuiltIns
"""

__all__: list[str] = [
    "EnumField",
    "BoundEnumField",
    "Loader",
]


from collections.abc import Mapping
from enum import Enum
from typing import Any, Protocol, Self, overload, runtime_checkable

from .._modulepath import ModulePath
from ..empty import VOID, MayBe, MayNot
from ..primitives._loader import Loader, Loading


@runtime_checkable
class EnumFieldLoadeer[E: Enum, Value: Any](Protocol):
    def __call__(self) -> Mapping[E, Value]:
        """Prepare Enum Data for Field"""


class LoaderProto[T](Loading[[Enum], T], Protocol): ...


class EnumField[T]:
    """Setup independent Descriptor per EnumCls with Lazy data binding"""

    # TODO: overload, either loader or default/fallback
    def __init__(
        self,
        *,
        # WARN: dispatch of Load Full Table and Load Single Enum
        loader: MayNot[Loader[[Enum], T]] = None,
        default: MayBe[T] = VOID,
        fallback: MayNot[Loader[[Enum], T]] = None,
    ) -> None:
        self._loader: Loader[[Enum], T] = (
            Loader(fallback, default=default) if loader is None else loader
        )
        self._name: str = ""
        self._slots: dict[type[Any], BoundEnumField[Any, T]] = {}  # NEXT:

    def __set_name__(self, owner: type, name: str) -> None:
        # LATER: owner?
        self._name: str = name

    @overload
    def __get__[E: Enum](
        self, member: None, owner: type[E]
    ) -> BoundEnumField[E, T]: ...
    @overload
    def __get__(self, member: Enum, owner: type[Any]) -> T: ...
    def __get__[E: Enum](
        self, member: E | None, owner: type[E]
    ) -> BoundEnumField[E, T] | T:
        """Provide BoundEnumField for EnumCls or extract Value for Member"""
        slot: BoundEnumField[E, T] = self._slot_for(owner)
        return slot if member is None else slot.get(member)

    @classmethod
    def imports(
        cls,
        path: ModulePath,
        *,
        call_it: bool = False,
        # TODO: loader or default/fallback
        default: MayBe[T] = VOID,
        fallback: MayNot[Loader[[Enum], T]] = None,
    ) -> Self:
        """Create Lazy Field by 'module.path:Attr' evaluation"""
        return cls.lazy(
            path.lazy_loader(call_if_callable=call_it),  # ty:ignore FIX:
            default=default,
            fallback=fallback,
        )

    @classmethod
    def lazy(
        cls,
        loader: Loader[[Enum], T],
        *,
        default: MayBe[T] = VOID,
        fallback: MayNot[Loader[[Enum], T]] = None,  # REMOVE: ??
    ) -> Self:
        """Create Lazy Field with Zero-Arg Loader"""
        return cls(loader=loader, default=default, fallback=fallback)

    def _slot_for[E: Enum](self, owner: type[E]) -> BoundEnumField[E, T]:
        """Provide per owner cached Field and load if needed"""
        if owner not in self._slots:
            self._slots[owner] = BoundEnumField(
                owner, self._name, loader=self._loader.clone()
            )
        return self._slots[owner]


class BoundEnumField[EnumT: Enum, T]:  # RENAME: this is acually not a Field...
    """Per-Enum-class storage, lazy loader, and validator for EnumField"""

    def __init__(
        self, owner: type[EnumT], name: str, loader: Loader[[EnumT], T]
    ) -> None:
        self.owner: type[EnumT] = owner
        self.name: str = name
        # WARN: dispatch of Load Full Table and Load Single Enum
        self._loader: Loader[[EnumT], T] = loader
        self._data: dict[EnumT, T] = {}  # NEXT: CacheMap

    def __str__(self):
        return f"{self.owner.__name__}.{self.name}"

    def __repr__(self):
        return f"{self}[{self._loader=},{self._data=}]"

    @property
    def is_loaded(self) -> bool:
        # REMOVE: why on this here??
        return self._loader.is_done and (bool(self._data))  # ty:ignore FIX:

    def bind_loader(self, loader: Loader[[EnumT], T]) -> Loader[[EnumT], T]:
        # REMOVE: why on this here??
        """Attach Lazy Loader externally (e.g. as decorator)"""
        self._loader: Loader[[EnumT], T] = loader
        return loader

    def get(self, member: EnumT) -> T:
        """Fetch Member Data or Fallback or use Default or Raise"""
        if member not in self._data and not self._ensure_loaded(member):
            raise RuntimeError(f"Missing Data for {member} on {self}")
        return self._data[member]

    def register(
        self,
        mapping: Mapping[EnumT, T] | None = None,
        /,
        **by_name: T,
    ) -> None:
        """Update cached data by Enum member mapping or directly by  member name kwargs"""
        # NEXT: CacheMap
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

    def validate(self) -> None:  # IDEA: return bool?
        """Ensure 1-to-1 coverage between Enum members and registered values."""
        # CHECK:self._ensure_loaded()
        required: set[EnumT] = set(self.owner)
        allowed: set[EnumT] = set(self.owner._member_map_.values())  # ty:ignore - better than cast
        actual: set[EnumT] = set(self._data)

        if missing := required - actual:
            names: str = ", ".join(m.name or str(m) for m in missing)
            raise ValueError(f"{self} Missing for Members: {names}")

        if extra := actual - allowed:
            raise ValueError(f"{self} Unknown Keys: {extra}")

    def _ensure_loaded(self, member) -> bool:
        # TODO: check with registry, add somehow there
        if (resolved := self._loader.try_resolve(member)) is not VOID:  # ty:ignore FIX:
            self._data[member] = resolved
            return True
        return False
