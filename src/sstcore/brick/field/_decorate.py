"""
Setup Minimal Components to Assemble individual Descriptors

                                                 DependencyLevel[2]
"""

__all__: list[str] = [
    "FieldDecorator",
    "DecoratedField",
]

from inspect import Signature, signature
from types import MethodType
from typing import Any, Self

from ...port import attach
from ...port.calling import Calling
from ...port.link import portlink
from ..labor import reflect
from ._base import ReadField
from ._extend import ValidField


@portlink(attach.DecoDescriptor)
class FieldDecorator[**In, Out](ValidField):
    """
    Decorate Method with or without Args

    Important:
    - Difference between acting on method and manipulating method!
      - one is to modify the behaviour of the callable
      - the other is to modify the callable itself (with/without decorator?)
    """

    target_func: Calling[In, Out] | None = None
    signature: Signature | None = None

    def __init__(
        self,
        func: Calling[In, Out] | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Initialize and optionally bind if used as @Field (no parens)."""
        super().__init__(*args, **kwargs)
        if func is not None:
            self.bind(func)

    def __call__(self, func: Calling[In, Out]) -> Self:
        """Invoked only when used as @Field(args) (with parens)."""
        self.bind(func)
        return self

    def __str__(self):
        return f"{self.target_func}[{self.signature}]"

    def bind(self, func: Calling) -> None:

        if not callable(func):
            raise TypeError(f"Target must be callable, got {type(func)}")

        self.target_func = func
        self.signature: Signature = signature(func)

        default_doc = f"Bound Function by {self}"
        self.__doc__: str = reflect.doc(func, default=default_doc)
        self.public_name: str = reflect.funcname(func)  # TODO: default value?

    def validate(
        self, unit: object, value: Calling[In, Out]
    ) -> Calling[In, Out]:
        """Finish the loop and return the value"""

        if not callable(value):
            raise self.raiser.Function(self, unit, value=value)

        if self._has_val(unit):
            raise self.raiser.WriteExists(self, unit, value=value)

        return super().validate(unit, value)


@portlink(attach.DecoDescriptor)
class DecoratedField[**In, Out](
    ReadField[Calling[In, Out]], FieldDecorator[In, Out]
):
    """FieldDecorator with default ReadField for direct usage"""

    def read(self, unit: object) -> Calling[In, Out]:
        if self._has_val(unit):
            return self._get_val(unit)

        if self.target_func is None:
            raise self.raiser.Function(
                self, unit, "Missing target_func to bind."
            )
        bound_method = MethodType(self.target_func, unit)
        self.write(unit, bound_method)

        return bound_method
