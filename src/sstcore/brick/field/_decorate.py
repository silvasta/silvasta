"""
Setup Minimal Components to Assemble individual Descriptors

                                                 DependencyLevel[2]
"""

__all__: list[str] = [
    "FieldDecorator",
    "DecoratedField",
]

from collections.abc import Callable
from inspect import Signature, signature
from types import MethodType
from typing import Any, Concatenate, Self

from ...port import attach
from ...port.link import portlink
from .. import reflect
from ._base import ReadField
from ._extend import ValidField


@portlink(attach.DecoDescriptor)
class FieldDecorator[**In, Out](ValidField[Callable[In, Out]]):
    """
    Decorate Method with or without Args

    Important:
    - Difference between acting on method and manipulating method!
      - one is to modify the behaviour of the callable
      - the other is to modify the callable itself (with/without decorator?)
    """

    target_func: Callable[In, Out] | None = None
    signature: Signature | None = None

    def __init__(
        self,
        func: Callable[In, Out] | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Initialize and optionally bind if used as @Field (no parens)."""
        super().__init__(*args, **kwargs)
        if func is not None:
            self.bind(func)

    def __call__[**NewIn, NewOut](
        self, func: Callable[Concatenate[Any, NewIn], NewOut]
    ) -> Self:
        """Invoke only when used as hybrid decorator with args:= @Field(args)"""
        self.bind(func)
        return self

    def __str__(self):
        return f"{self.target_func}[{self.signature}]"

    def bind(self, func: Callable) -> None:

        if not callable(func):
            raise TypeError(f"Target must be callable, got {type(func)}")

        self.target_func: Callable[In, Out] = func
        self.signature: Signature = signature(func)

        default_doc = f"Bound Function by {self}"
        self.__doc__: str = reflect.doc(func, default=default_doc)

        if not hasattr(self, "public_name"):  # LATER: ensure NamedField works
            self.public_name: str = reflect.funcname(func)
            self.private_name: str = f"_{self.public_name}"

    def validate(
        self, unit: object, value: Callable[In, Out]
    ) -> Callable[In, Out]:
        """Finish the loop and return the value"""

        if not callable(value):
            raise self.raiser.Function(self, unit, value=value)

        return super().validate(unit, value)


@portlink(attach.DecoDescriptor)
class DecoratedField[**In, Out](
    ReadField[Callable[In, Out]], FieldDecorator[In, Out]
):
    """FieldDecorator with default ReadField for direct usage"""

    def validate(
        self, unit: object, value: Callable[In, Out]
    ) -> Callable[In, Out]:
        if self._has_val(unit):
            raise self.raiser.WriteExists(self, unit, value=value)
        return super().validate(unit, value)

    def read(self, unit: object) -> Callable[In, Out]:
        if self._has_val(unit):
            return self._get_val(unit)

        if self.target_func is None:
            text = "Missing target_func to bind."
            raise self.raiser.Function(self, unit, text)

        bound_method = MethodType(self.target_func, unit)
        self.write(unit, bound_method)

        return bound_method
