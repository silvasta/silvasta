"""
Setup Minimal Components to Assemble individual Descriptors

- ResetField: Soft Delete with Default (__del__)

- ValidField: Base for Validated WriteField (__set__)
- TypedField: Types for ValidField (__set__)

                                                 DependencyLevel[1]
"""

__all__: list[str] = [
    "ValidField",
    "TypedField",
    "ResetField",
]

from typing import TYPE_CHECKING, Never, Self, overload

from ...port import attach
from ...port.attach import Types
from ..labor import clsname
from ._base import DeleteField, WriteField


class ResetField[DefaulT](DeleteField):
    def __init__(self, *args, default: DefaulT, **kwargs) -> None:
        self.default: DefaulT = default
        super().__init__(*args, **kwargs)

    def remove(self, unit: object) -> None:
        self._set_val(unit, self.default)


class ValidField[FieldT](WriteField):
    def validate(self, unit: object, value: FieldT) -> FieldT:
        """Finish the loop and return the value"""
        return value

    def write(self, unit: object, value: FieldT) -> None:
        value: FieldT = self.validate(unit, value)
        super().write(unit, value)


class TypedField[FieldT](ValidField[FieldT]):
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


if TYPE_CHECKING:
    _valid: type[attach.ValidDescriptor] = ValidField
    _typed: type[attach.TypedDescriptor] = TypedField
    _reset: type[attach.DeleteDescriptor] = ResetField


class _FixTypeField[FieldT]:
    def __init__(self, types: Types[FieldT]) -> None:
        self._types: Types[FieldT] = types

    def name(self, unit: object) -> str:
        return f"{type(unit).__name__}.{self.public_name}"

    def __set_name__(self, _owner: type, name: str) -> None:
        self.public_name: str = name
        self.private_name: str = f"_{name}"

    def __set__(self, unit: object, value: FieldT) -> None:
        if self.private_name in unit.__dict__:  # TODO: raiser
            raise AttributeError(
                f"{self.name(unit)} is frozen and cannot be reassigned!"
            )
        if not isinstance(value, self._types):  # TODO: raiser
            raise TypeError(
                f"Validation failed for {self.name(unit)}. "
                f"Expected {self._types}, got {type(value).__name__}."
            )
        unit.__dict__[self.private_name] = value

    @overload
    def __get__(self, unit: None, _owner: type | None = None) -> Self: ...

    @overload
    def __get__(self, unit: object, _owner: type | None = None) -> FieldT: ...
    def __get__(self, unit: object | None, _owner=None) -> FieldT | Self:
        if unit is None:
            return self
        if self.private_name not in unit.__dict__:  # TODO: raiser
            raise AttributeError(f"{self.name(unit)} is Missing! {self}")
        return unit.__dict__[self.private_name]
