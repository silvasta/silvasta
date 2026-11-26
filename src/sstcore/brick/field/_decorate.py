"""
Setup Minimal Components to Assemble individual Descriptors

                                                 DependencyLevel[2]
"""

__all__: list[str] = [
    "FieldDecorator",
    "DecoratedField",
    "CallableField",
]

from collections.abc import Callable
from types import MethodType
from typing import Any, Concatenate, Literal, Self, overload

from ...port import attach
from ...port.link import portlink
from .. import reflect
from ._base import DeleteField, ReadField
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

    target_func: Callable[..., Out] | None = None
    bind_to_self: bool = False

    # AI: does this massive overload bring any benefit?
    @overload
    def __init__(
        self,
        func: Callable[Concatenate[Any, In], Out],
        *args: Any,
        bind_to_self: Literal[True] = True,
        **kwargs: Any,
    ) -> None: ...
    @overload
    def __init__(
        self,
        func: Callable[In, Out],
        *args: Any,
        bind_to_self: Literal[False],
        **kwargs: Any,
    ) -> None: ...
    @overload
    def __init__(
        self,
        func: None = None,
        *args: Any,
        bind_to_self: bool = True,
        **kwargs: Any,
    ) -> None: ...
    def __init__(
        self,
        func: Callable[..., Out] | None = None,
        *args: Any,
        bind_to_self: bool = True,
        **kwargs: Any,
    ) -> None:
        self.bind_to_self = bind_to_self
        super().__init__(*args, **kwargs)
        if func is not None:
            self.bind(func)

    def __call__(self, func: Callable[Concatenate[Any, In], Out]) -> Self:
        """Invoke only when used as hybrid decorator with args:= @Field(args)"""
        self.bind(func)
        return self

    def __set__(self, unit: object, value: Callable[..., Any]) -> None:
        # TEST: already helps, is that the solution?
        self.write(unit, value)

    def write(self, unit: object, value: Callable[..., Any]) -> None:
        # TEST: already helps, is that the solution?
        super().write(unit, value)

    def bind(self, func: Callable[..., Any]) -> None:
        if not callable(func):
            raise TypeError(f"Target must be callable, got {type(func)}")

        self.target_func = func

        default_doc = f"Function bound by: {reflect.clsname(self)}"
        self.__doc__: str = reflect.attr.doc(func, default=default_doc)

        if not hasattr(self, "public_name"):
            self.public_name: str = reflect.funcname(func)
            self.private_name: str = f"_{self.public_name}"

        default_doc = f"Function bound by: {self}"
        self.__doc__: str = reflect.attr.doc(func, default=default_doc)

        if not hasattr(self, "public_name"):
            self.public_name: str = reflect.funcname(func)
            self.private_name: str = f"_{self.public_name}"

    def validate(
        self, unit: object, value: Callable[..., Any]
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
            raise self.raiser.Function(
                self, unit, "Missing target_func to bind."
            )

        bound_method = MethodType(self.target_func, unit)
        self.write(unit, bound_method)
        return bound_method


@portlink(attach.DecoDescriptor)
class CallableField[**In, Out](
    ReadField[Callable[In, Out]], FieldDecorator[In, Out], DeleteField
):
    """
    Mount default fallback method to overwrite by Callable or Emitter object

    - without proxy wrapping (LogEmitter, DbEmitter, CliEmitter)

    """

    def read(self, unit: object) -> Callable[In, Out]:
        if self._has_val(unit):
            return self._get_val(unit)

        if self.target_func is None:
            raise self.raiser.Function(self, unit, "Missing Target to bind")

        if self.bind_to_self:
            return MethodType(self.target_func, unit)

        return self.target_func
