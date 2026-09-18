"""
Setup Minimal Components to Assemble individual Descriptors

                                                 DependencyLevel[0]
"""  # TODO: level

__all__: list[str] = [
    "FieldDecorator",
    "DecoratedField",
]

from inspect import Signature, signature
from typing import TYPE_CHECKING, Any, Never, Self

from ...port import attach
from ...port.calling import Calling
from ..labor import reflect
from ._base import ReadField
from ._specify import ValidField


class FieldDecorator[**In, Out](ValidField):
    def __init__(
        self,
        no_arg_deco_func: Calling[In, Out] | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Check if Decorator has Input -> Bind or Attach"""

        if no_arg_deco_func is None:
            raise NotImplementedError("Bind! Outer func", args, kwargs)
        else:
            self.bind(no_arg_deco_func)  # NEXT: write?

        self.signature: Signature | None = None  # CHECK: with bind

        super().__init__(*args, **kwargs)

    def __call__(self, with_arg_deco_func: Calling[In, Out]) -> Self:
        """Invoked only when used as @Field(args)"""
        self.deco_func: Calling = with_arg_deco_func  # PARAM: add generics
        self.bind(arg_deco_func)
        return self

    def __str__(self):
        return f"{self.deco_func}[{self.signature}]"

    def raise_on_unbound(self, unit: object) -> Never:
        # LATER: combine with raise_on_missing?
        raise RuntimeError(f"{self.name(unit)} Missing Function!")

    def raise_on_signature(self, unit: object, bad_func: Any) -> Never:
        message: str = (
            f"{self.name(unit)} expected {self.signature!r}, got {bad_func}"
            if self.signature is not None
            else f"{self.name(unit)} Missing Signature! Call: {bad_func=}"  # CHECK:
        )
        raise TypeError(message)

    def bind(self, func: Calling, override=False) -> None:
        # NEXT: which bind??
        self.__doc__: str | None = func.__doc__  # EXTRACT: brick.labor
        self.public_name: str = reflect.dig.func(func)  # TODO: default value?
        self.signature = signature(func)
        self.write(unit, func)

    def validate(
        self, unit: object, value: Calling[In, Out], reset=False
    ) -> Calling[In, Out]:
        """Finish the loop and return the value"""
        if self._has_val(unit) and not reset:  # IDEA: self.is_writable
            raise RuntimeError(f"Function already Exists! {self}]")
        if not callable(value):
            raise TypeError(f"Not Callable, {value=}! {self}")

        return super().validate(unit, value)


# NEXT: most likely collapse??
class DecoratedField[FieldT](ReadField[FieldT], FieldDecorator):
    # TASK: check if and what is needed at all
    def read(self, unit: object) -> FieldT:
        if not self._has_val(unit):
            if self.deco_func is None:
                self.raise_on_unbound(unit)
            self.write(unit, self.deco_func)  # materialize default
        return self._get_val(unit)


if TYPE_CHECKING:
    _deco: type[attach.DecoratingField] = DecoratedField
    _deco: type[attach.DecoratingField] = FieldDecorator
