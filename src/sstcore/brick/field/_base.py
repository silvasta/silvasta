"""
Define the Atomic Components of the Fields

- NamedField: root

- WriteField: __set__
- OnlyReadField: raise
- ReadField: __get__
- DeleteField: __del__
                                                 DependencyLevel[0]
"""  # FIX: level: bump all or consider _raise as DependencyLevel[-1]?

__all__: list[str] = [
    "NamedField",
    "WriteField",
    "OnlyReadField",
    "ReadField",
    "DeleteField",
]

from typing import TYPE_CHECKING, Any, Never, Self, overload

from ...port import attach
from ...port.raising import Raiser
from ..labor import reflect
from ._raise import FieldRaiser


class NamedField:
    """Provide Utils for all Fields"""

    raiser: type[Raiser] = FieldRaiser
    # TODO: select raiser/on_error
    # IDEA: this as getter? (as well for others) with bad message on set?
    on_error = FieldRaiser

    def __init__(self, *args, **kwargs):
        """Close the chain: super()"""

    def __set_name__(self, owner: type, name: str) -> None:
        _owner = owner
        self.public_name: str = name
        self.private_name: str = f"_{name}"

    def name(self, unit: object) -> str:
        return f"{reflect.clsname(unit)}.{self.public_name}"

    def _get_val(self, unit: object) -> Any:  # NEXT: FieldT???
        return unit.__dict__[self.private_name]

    def _set_val(self, unit: object, value: Any) -> None:
        unit.__dict__[self.private_name] = value

    def _del_val(self, unit: object) -> None:
        del unit.__dict__[self.private_name]

    def _has_val(self, unit: object) -> bool:
        return self.private_name in unit.__dict__


class _IdeaFieldAccess(NamedField):
    # IDEA: access mixin -> class BaseField(NamedField,FieldAccess):...
    @property
    def can_reset(self) -> bool:
        return False

    @property
    def can_load(self) -> bool:  # CHECK: if not redundant
        return False

    def is_readable(self, unit) -> bool:
        return self.can_load or self._has_val(unit)

    def is_writable(self, unit) -> bool:
        return self.can_load or not self._has_val(unit)


class WriteField[FieldT](NamedField):
    def __set__(self, unit: object, value: FieldT) -> None:
        self.write(unit, value)

    def write(self, unit: object, value: FieldT) -> None:
        self._set_val(unit, value)


class OnlyReadField(NamedField):
    # IDEA: replace by attribute and error option
    # if self._has_val(unit) and not reset:
    #     raise RuntimeError(
    #         f"Alredy exists! {self.default_func}[{self.signature}]"
    #     )
    def __set__(self, unit: object, reject: object) -> Never:
        raise AttributeError(f"{self.name(unit)} is not Writable! {reject=}")


class ReadField[FieldT](NamedField):
    @overload
    def __get__(self, unit: None, owner: type | None) -> Self: ...
    @overload
    def __get__(self, unit: object, owner: type | None) -> FieldT: ...
    def __get__(
        self, unit: object | None, _owner: type | None = None
    ) -> FieldT | Self:
        """Dispatch by Caller: unit=instance or owner=type(instance)"""

        return self if unit is None else self.read(unit)

    def on_erroron_missing(self, unit: object) -> Never:
        # REMOVE: when on_error established
        raise AttributeError(f"{self.name(unit)} is Missing!")

    def new_on_error(self, _unit: object, _todo: Any) -> Never:
        raise self.on_error.ReadMissing(_todo)  # ty:ignore

    def read(self, unit: object) -> FieldT:
        if not self._has_val(unit):
            self.on_erroron_missing(unit)
        return self._get_val(unit)


class DeleteField(NamedField):
    def __delete__(self, unit: object) -> None:
        self.remove(unit)

    def remove(self, unit: object) -> None:
        if self._has_val(unit):
            self._del_val(unit)


if TYPE_CHECKING:
    _base: type[attach.Descriptor] = NamedField
    _read: type[attach.ReadDescriptor] = ReadField
    _delete: type[attach.WriteDescriptor] = WriteField
    _write: type[attach.DeleteDescriptor] = DeleteField
