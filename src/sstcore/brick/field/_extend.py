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

from typing import Never

from ...port import attach
from ...port.attach import Types
from ...port.link import portlink
from ..labor import clsname
from ._base import MISSING, DeleteField, WriteField


@portlink(attach.DeleteDescriptor)
class ResetField[DefaulT](DeleteField):
    def __init__(self, *args, default: DefaulT, **kwargs) -> None:
        self.default: DefaulT = default
        super().__init__(*args, **kwargs)

    def remove(self, unit: object) -> None:
        if self.default is not MISSING:
            self._set_val(unit, self.default)
        else:
            super().remove(unit)


@portlink(attach.ValidDescriptor)
class ValidField[FieldT](WriteField):
    def validate(self, unit: object, value: FieldT) -> FieldT:
        """Finish the loop and return the value"""
        return value

    def write(self, unit: object, value: FieldT) -> None:
        value: FieldT = self.validate(unit, value)
        super().write(unit, value)


@portlink(attach.TypedDescriptor)
@portlink(attach.ValidDescriptor)
class TypedField[FieldT](ValidField[FieldT]):
    def __init__(self, *args, types: Types[FieldT], **kwargs) -> None:
        self.types: Types[FieldT] = types
        super().__init__(*args, **kwargs)

    def raise_on_typing(self, unit: object, value: FieldT) -> Never:
        # TODO: raiser, Validation error or new typed error
        _m = f"{self.name(unit)} expected {self.types!r}, got {clsname(value)}"
        raise TypeError(_m)

    def validate(self, unit: object, value: FieldT) -> FieldT:
        if not isinstance(value, self.types):
            self.raise_on_typing(unit, value)
        return super().validate(unit, value)
