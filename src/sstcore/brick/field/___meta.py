"""
Assemble Class Based Descriptors

- EXPERIMENTAL
                                                 DependencyLevel[2]
"""

from enum import Enum

__all__: list[str] = [
    "MetaStateField",
]

from typing import Any, Never, Self

from ...port.attach import Types
from ..labor import clsname
from ._base import MetaBaseField


class _ReadField[FieldT](MetaBaseField):
    def __get__(
        self, unit: object | None, _owner: type | None = None
    ) -> FieldT | Self:
        """Dispatch by Caller: unit=instance or owner=type(instance)"""

        return self if unit is None else self.read(unit)

    def on_erroron_missing(self, unit: object) -> Never:
        # REMOVE: when on_error established
        raise AttributeError(f"{self.name(unit)} is Missing!")

    def new_on_error(self, _unit: object, _todo: Any) -> Never:
        raise self.on_error.ReadMissing(_todo)

    def read(self, unit: object) -> FieldT:
        if not self._has_val(unit):
            self.on_erroron_missing(unit)
        return self._get_val(unit)


class _WriteField[FieldT](MetaBaseField):
    def __set__(self, unit: object, value: FieldT) -> None:
        self.write(unit, value)

    def write(self, unit: object, value: FieldT) -> None:
        self._set_val(unit, value)


class _ValidField[FieldT](_WriteField):
    def validate(self, unit: object, value: FieldT) -> FieldT:
        """Finish the loop and return the value"""
        return value

    def write(self, unit: object, value: FieldT) -> None:
        value: FieldT = self.validate(unit, value)
        super().write(unit, value)


class _TypedField[FieldT](_ValidField[FieldT]):
    def __init__(self, *args, types: Types[FieldT], **kwargs) -> None:
        self.types: Types[FieldT] = types
        super().__init__(*args, **kwargs)

    def raise_on_typing(self, unit: object, value: FieldT) -> Never:
        _m = f"{self.name(unit)} expected {self.types!r}, got {clsname(value)}"
        raise TypeError(_m)

    def validate(self, unit: object, value: FieldT) -> FieldT:
        if not isinstance(value, self.types):
            self.raise_on_typing(unit, value)
        return super().validate(unit, value)


class MetaStateField[T: Enum](_TypedField[T], _ReadField[T]):
    """State graph evaluation for class-level namespaces"""
