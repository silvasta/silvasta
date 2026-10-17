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
from ...port.link import portlink
from ..reflect import clsname
from ._base import UNSET, DeleteField, WriteField


@portlink(attach.DeleteDescriptor)
class ResetField[DefaultT](DeleteField):
    def __init__(self, *args, default: DefaultT, **kwargs) -> None:
        self.default: DefaultT = default
        super().__init__(*args, **kwargs)

    def remove(self, unit: object) -> None:
        if self.default is not UNSET:
            self._set_val(unit, self.default)
        else:
            super().remove(unit)


@portlink(attach.ValidDescriptor)
class ValidField[FieldT](WriteField[FieldT]):
    def validate(self, unit: object, value: FieldT) -> FieldT:
        """Finish the loop and return the value"""
        _ = unit
        return value

    def write(self, unit: object, value: FieldT) -> None:
        value: FieldT = self.validate(unit, value)
        super().write(unit, value)


@portlink(attach.TypedDescriptor)
class TypedField[AnnoT](ValidField[AnnoT]):
    def __init__(self, *args, types: type[AnnoT] | tuple[type, ...], **kwargs):
        self.types: type[AnnoT] | tuple[type, ...] = types
        super().__init__(*args, **kwargs)

    def raise_on_typing(self, unit: object, value: AnnoT) -> Never:
        # TODO: raiser, Validation error or new typed error
        _m = f"{self.name(unit)} expected {self.types!r}, got {clsname(value)}"
        raise TypeError(_m)

    def validate(self, unit: object, value: AnnoT) -> AnnoT:
        if not isinstance(value, self.types):
            self.raise_on_typing(unit, value)
        return super().validate(unit, value)
