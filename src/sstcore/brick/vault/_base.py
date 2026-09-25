"""
ListRegistry - Main Variation of the Core Registry

-
"""

__all__: list[str] = [
    "BaseRegistry",
]

from collections.abc import Callable, Iterator, Mapping, Sequence
from typing import TYPE_CHECKING, Any, Literal, NoReturn, overload

from ...port.raising import SstCoreError
from ...port.register import Registry, RegistryDescriptor, VaultPolicy
from ..field import PolicyField
from ._extras import RegistryField

# type Vaults = list | tuple | dict
type Vaults = Sequence | Mapping


class RegistryError(SstCoreError): ...


_conflict = PolicyField(VaultPolicy, default=VaultPolicy.RAISE)

# IMPORTANT: the manual
# class BaseVault[Item, Vault: Vaults, U, A: Any]:
#     # Set default to a specific Enum member, not the class
#     on_conflict = MatchPolicyField(
#         VaultPolicy,
#         default=VaultPolicy.RAISE,
#         enum_match=default_conflict_handler)
#     def add(self, data: Item) -> Vault:
#         if self._is_conflict(data):
#             # Access the descriptor from the class to call match()
#             return type(self).on_conflict.match(unit=self, data=data)
#         # ... normal add logic ...


class BaseVault[Item, Vault: Vaults, U, A: Any]:
    """Provide initial Setup"""

    vault: Vault

    on_conflict = PolicyField(VaultPolicy, default=VaultPolicy.RAISE)

    def __init__(self, initial: Vault) -> None:
        self.vault: Vault = initial

    #  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    def _clear_all(self) -> None:
        raise NotImplementedError

    def _slice_action(self, s: slice) -> Any:
        raise NotImplementedError

    def _str_action(self, k: str) -> Any:
        raise NotImplementedError

    def _item_action(self, target: Item) -> Any:
        raise NotImplementedError

    def _int_action(self, i: int) -> Item | None:
        raise NotImplementedError

    def _sanitize(self, result: Vault | Item | None) -> Vault:
        raise NotImplementedError

    def _remove(self, targets: Vault) -> Vault:
        """Return all removed"""
        raise NotImplementedError

    def _append(self, items: Vault) -> Vault:
        """Return all duplicated"""
        raise NotImplementedError

    #  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    @overload
    def __getitem__(self, index: A) -> Vault: ...
    @overload
    def __getitem__(self, index: U) -> Item: ...
    def __getitem__(self, index: str | int | slice) -> Item | Vault:

        match index:
            case slice():
                return self._slice_action(index)
            case int():
                return self._int_action(index)
            case str():
                return self._str_action(index)

        raise RegistryError(f"Registry Index[{index}] failed!", index)

    def __len__(self) -> int:
        return len(self.vault)

    def __iter__(self) -> Iterator[Item]:
        yield from self.vault

    @classmethod
    def as_field(cls, **kwargs) -> RegistryDescriptor:
        return RegistryField(loader=cls, **kwargs)


class BaseRegistry[Item, Vault: Vaults, U, A: int | str](
    BaseVault[Item, Vault, U, A]
):
    _prefered: Literal["str", "int"]

    @property
    def _preference(self) -> Callable:
        id: str | int = "" if self._prefered == "str" else 1
        return self._match(id)

    def _release(self, id: int | str) -> Vault | Item | None:
        return self._match(id)(id)

    def _match(self, id: str | int | None, fire=False) -> Callable:
        match id:
            case str():
                return self._str_action
            case int():
                return self._int_action
        raise TypeError(f"Invalid type of {id=}: {type(id)}")

    #  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    def add(self, items: Vault, override: bool = False) -> Vault:
        if override:
            for item in items:
                if (_result := self._item_action(item)) is None:
                    _x = self._remove(item)
            return self._append(items)

    def _add(self, items: Vault, override: bool = False) -> Vault:
        # AI: I would have been surprised if this trick worked... but no
        # - any better ideas how to wire everything better throug add?
        # if override:
        #     type(self.vault)(
        #         self._remove(item)
        #         for item in items
        #         if self._item_action(item) is None
        #     )
        self._append(items)

    def clear(self, id: A | None = None) -> Vault:  # TODO: multiple ids?
        if not id:
            values: Vault = self.vault
            self._clear_all()
            return values
        to_remove: Vault = self.find(id)
        # AI: here preferably as well without multiple checks...
        self._remove(to_remove)
        return to_remove

    def find(self, id: A) -> Vault:  # TODO: multiple ids?
        result: Vault | Item | None = self._release(id)
        return self._sanitize(result)

    def count(self, id: A) -> int:
        return len(self.find(id))

    def get(self, uid: U) -> Item | NoReturn:
        if (item := self._preference(uid)) is None:
            raise TypeError(f"Invalid Key of Index: {id}")
        return item

    def __contains__(self, target: Item) -> bool:
        return target in self.vault  # FAIL:


if TYPE_CHECKING:
    _instance: Registry = BaseRegistry()
    _class: type[Registry] = BaseRegistry
