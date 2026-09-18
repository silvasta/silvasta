"""
Setup Minimal Components to Assemble individual Descriptors

- ValidField: Base for Validated WriteField (__set__)
- TypedField: Types for ValidField (__set__)
- ResetField: Soft Delete with Default (__del__)
                                                 DependencyLevel[0]
"""

__all__: list[str] = [
    "ValidField",
    "TypedField",
    "ResetField",
    "RequiredField",
    "DecoratedField",
]

from inspect import Signature, signature
from typing import TYPE_CHECKING, Any, Never

from ...port import attach
from ...port.attach import FieldLoader, Types
from ..labor import clsname
from ._base import DeleteField, FieldDecorator, ReadField, WriteField

# NEXT:


class ValidField[T](WriteField):
    def validate(self, unit: object, value: T) -> T:
        """Finish the loop and return the value"""
        return value

    def write(self, unit: object, value: T) -> None:
        value: T = self.validate(unit, value)
        super().write(unit, value)


class TypedField[T](ValidField[T]):
    def __init__(self, *args, types: Types[T], **kwargs) -> None:
        self.types: Types[T] = types
        super().__init__(*args, **kwargs)

    def raise_on_typing(self, unit: object, value: T) -> Never:
        _m = f"{self.name(unit)} expected {self.types!r}, got {clsname(value)}"
        raise TypeError(_m)

    def validate(self, unit: object, value: T) -> T:
        if not isinstance(value, self.types):
            self.raise_on_typing(unit, value)
        return super().validate(unit, value)


class ResetField[DefaulT](DeleteField):
    def __init__(self, *args, default: DefaulT, **kwargs) -> None:
        self.default: DefaulT = default
        super().__init__(*args, **kwargs)

    def remove(self, unit: object) -> None:
        self._set_val(unit, self.default)


#  LINE: -- Combos -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class RequiredField[T](ReadField[T], TypedField[T]):
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


# NEXT:
class DecoratedField[T](ValidField, ReadField[T], FieldDecorator):
    # TASK: check where to add signature,
    # - consider as well the reset case!
    def __init__(
        self,
        target: FieldLoader[T] | None = None,  # TODO: Callable?
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.signature: Signature | None = None
        super().__init__(target, *args, **kwargs)

    def raise_on_unbound(self, unit: object) -> Never:
        # LATER: combine with raise_on_missing?
        raise RuntimeError(f"{self.name(unit)} Missing Function!")

    def raise_on_signature(self, unit: object, bad_func: Any) -> Never:
        # LATER: check self.signature is None?
        _m = f"{self.name(unit)} expected {self.signature!r}, got {bad_func}"
        raise TypeError(_m)

    def validate(self, unit: object, value: T) -> T:
        """Finish the loop and return the value"""
        if not callable(value):
            raise TypeError(f"{self} needs Callable, got {value}")
        if not self.signature:  # Write here instead of another self.write
            self.signature: Signature = signature(value)
            # AI: maybe here catch the unit, ->self.unit?
        return super().validate(unit, value)

    def read(self, unit: object) -> T:
        # TODO:
        if self.target_input is None:
            self.raise_on_unbound(unit)
        return self.target_func(unit)


if TYPE_CHECKING:
    _deco: type[attach.DecoratingField] = DecoratedField
    _valid: type[attach.ValidDescriptor] = ValidField
    _typed: type[attach.TypedDescriptor] = TypedField
    _reset: type[attach.DeleteDescriptor] = ResetField
    _injected: type[attach.WriteDescriptor] = RequiredField
    _injected: type[attach.ValidDescriptor] = RequiredField
