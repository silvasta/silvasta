"""
Setup Minimal Components to Assemble individual Descriptors

- ValidField: Base for Validated WriteField (__set__)
- TypedField: Types for ValidField (__set__)
- ResetField: Soft Delete with Default (__del__)
                                                 DependencyLevel[0]
"""  # TODO: level

# RENAME: ideas:
# - validate
# - extend
# - refine

__all__: list[str] = [
    "ValidField",
    "TypedField",
    "ResetField",
    "RequiredField",
]

from typing import TYPE_CHECKING, Never

from ...port import attach
from ...port.attach import Types
from ..labor import clsname
from ._base import DeleteField, ReadField, WriteField


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


class RequiredField[FieldT](ReadField[FieldT], TypedField[FieldT]):
    """
    Annotate empty Field ready to fill before first access

    Example:
        class Renderer:
            device = RequiredField(types=str)

        r = Renderer()
        r.device = "GPU"   # Valid
        print(r.device)    # "GPU"
        r.device = 123     # TypeError: expected str, got int
    """


if TYPE_CHECKING:
    _valid: type[attach.ValidDescriptor] = ValidField
    _typed: type[attach.TypedDescriptor] = TypedField
    _reset: type[attach.DeleteDescriptor] = ResetField
    _injected: type[attach.WriteDescriptor] = RequiredField
    _injected: type[attach.ValidDescriptor] = RequiredField
