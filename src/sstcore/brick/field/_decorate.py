"""
Setup Minimal Components to Assemble decorating Descriptors

                                                 DependencyLevel[2]
"""

__all__: list[str] = [
    "FieldDecorator",
    "DecoratedField",
    "CallableField",
]

from collections.abc import Callable
from types import MethodType
from typing import Any, Concatenate, Self

from ...port import attach
from ...port.empty import MayNot
from ...port.link import portlink
from .. import reflect
from ._base import DeleteField, ReadField
from ._extend import ValidField

type SelfBound[**In, Out] = Callable[Concatenate[Any, In], Out]
type MaybeBound[**In, Out] = SelfBound[In, Out] | Callable[In, Out]


@portlink(attach.DecoDescriptor)
class FieldDecorator[**In, Out](ValidField[Callable[In, Out]]):
    """
    Decorate Method with or without Args

    Important:
    - Difference between acting on method and manipulating method!
      - one is to modify the behaviour of the callable
      - the other is to modify the callable itself (with/without decorator?)
    """

    def __init__(
        self, func: MayNot[MaybeBound[In, Out]] = None, *args, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.target_func: MayNot[MaybeBound[In, Out]] = None
        if func is not None:
            self.bind_target_func(func)

    def __call__(self, func: SelfBound[In, Out]) -> Self:
        """Invoke only when used as hybrid decorator with args:= @Field(args)"""
        self.bind_target_func(func)
        return self

    # def __set__(self, unit: object, value: Callable[..., Any]) -> None:
    #     # TEST:  helps, is that the solution?
    #     self.write(unit, value)
    #
    # def write(self, unit: object, value: Callable[..., Any]) -> None:
    #     # TEST: already helps, is that the solution?
    #     super().write(unit, value)

    def bind_target_func(self, func: MaybeBound[In, Out]) -> None:
        """Install class-level callable: Entry point for decorator binding"""
        if not callable(func):
            raise self.raiser.Function(self, value=func)

        self.target_func: MaybeBound[In, Out] = func

        default_doc = f"Function bound by: {reflect.clsname(self)}"
        self.__doc__: str = reflect.attr.doc(func, default=default_doc)

        if not hasattr(self, "public_name"):
            self.public_name: str = reflect.funcname(func)
            self.private_name: str = f"_{self.public_name}"

    def validate(self, unit: object, value: Callable) -> Callable[In, Out]:
        if not callable(value):
            raise self.raiser.Function(self, unit, value=value)

        return super().validate(unit, value)


@portlink(attach.DecoDescriptor)
class DecoratedField[**In, Out](
    ReadField[Callable[In, Out]], FieldDecorator[In, Out]
):
    """FieldDecorator with ReadField for direct usage"""

    def validate(
        self, unit: object, value: Callable[In, Out]
    ) -> Callable[In, Out]:
        if self._has_val(unit):
            raise self.raiser.WriteExists(self, unit, value=value)
        return super().validate(unit, value)

    def read(self, unit: object) -> Callable[In, Out]:
        if not self._has_val(unit):
            if self.target_func is None:
                raise self.raiser.Function(self, unit, "Missing target_func")
            self.write(unit, MethodType(self.target_func, unit))
        return super().read(unit)


@portlink(attach.DecoDescriptor)
class CallableField[**In, Out](
    FieldDecorator[In, Out], ReadField[Callable[In, Out]], DeleteField
):
    def __init__(
        self,
        func: MayNot[MaybeBound[In, Out]] = None,
        *args,
        bind_to_self: bool = True,
        **kwargs,
    ) -> None:
        self.bind_to_self: bool = bind_to_self
        super().__init__(func, *args, **kwargs)

    def read(self, unit: object) -> Callable[In, Out]:
        if self._has_val(unit):
            return self._get_val(unit)

        if self.target_func is None:
            raise self.raiser.Function(self, unit, "Missing Target to bind")

        return (
            MethodType(self.target_func, unit)  # ty:ignore
            if self.bind_to_self
            else self.target_func
        )
