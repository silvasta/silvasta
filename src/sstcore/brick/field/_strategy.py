"""
Exchange Callables on Classes

- StrategyField: strict signature-checked callable field
- MorphingField: signature-agnostic callable field

                                                 DependencyLevel[3]
"""

__all__: list[str] = [
    "StrategyField",
    "MorphingField",
    #
    "MethodFieldEngine",
    "BoundStrategy",
]

from collections.abc import Callable
from typing import Any, Concatenate, Literal, Self, overload

from ...port import attach
from ...port.link import portlink
from .. import reflect
from ..call._signature import _extract_signature, _pass_all_valid_sig
from ._base import DeleteField, ReadField
from ._decorate import FieldDecorator


@portlink(attach.DecoDescriptor)
class MethodFieldEngine[**In, Out](
    ReadField[Callable[In, Out]], FieldDecorator[In, Out], DeleteField
):
    """Base Engine for dynamic Callable fields."""

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
        self.bind_to_self: bool = bind_to_self
        super().__init__(func, *args, **kwargs)

    def bind(self, func: Callable[..., Out]) -> None:
        super().bind(func)
        if self.signature is not None:
            # AI: assume the _extract_signature will be available here
            self.signature = _extract_signature(
                func, bind_to_self=self.bind_to_self
            )

    def read(self, unit: object) -> BoundStrategy[In, Out]:
        if self._has_val(unit):
            return BoundStrategy(self, unit, self._get_val(unit), bind=False)
        if self.target_func is not None:
            return BoundStrategy(
                self, unit, self.target_func, bind=self.bind_to_self
            )
        raise self.raiser.Function(self, unit, "Missing target_func")

    def switch(self, func: Callable[In, Out]) -> Self:
        """Modify the Class-Level baseline strategy."""
        self.bind(func)
        return self


@portlink(attach.CallingDescriptor)
class StrategyField[**In, Out](MethodFieldEngine[In, Out]):
    """Forces the override to match the default function's signature."""

    def validate(
        self, unit: object, value: Callable[In, Out]
    ) -> Callable[In, Out]:
        """Enforce strict signature rules for instance-level overrides."""

        value: Callable[In, Out] = super().validate(unit, value)

        # AI: assume the _pass_all_valid_sig will be available here
        if self.signature is None or not _pass_all_valid_sig(
            value, baseline=self.signature
        ):
            raise self.raiser.Signature(self, unit, value=value)

        return value


@portlink(attach.MorphingDescriptor)
class MorphingField[**In, Out](MethodFieldEngine[In, Out]):
    """Allows swapping methods with arbitrary new signatures."""

    def morph(self, func: Callable[..., Any]) -> Self:
        """Unsafe Function Exchange on the Class Level."""
        self.bind(func)
        return self


class BoundStrategy[**In, Out]:
    """Proxy object that acts as a bound method and provides swap mutations."""

    def __init__(
        self,
        engine: MethodFieldEngine[In, Out],
        unit: Any,
        func: Callable[..., Out],
        bind: bool = True,
    ):
        self.engine: MethodFieldEngine[In, Out] = engine
        self.unit: Any = unit
        self.func: Callable[..., Out] = func
        self.bind: bool = bind

    @property
    def __name__(self) -> str:
        return reflect.funcname(self.func)

    def __call__(self, *args: In.args, **kwargs: In.kwargs) -> Out:
        if self.bind:
            return self.func(self.unit, *args, **kwargs)
        return self.func(*args, **kwargs)

    def __getattr__(self, name: str) -> Any:  # NEXT: decide on this
        # WARN: newly opened __getattr__, check typing!
        """Keep mounted callable objects (LogEmitter, …) intact."""
        return getattr(self.func, name)

    def switch(self, new_func: Callable[In, Out]) -> Self:
        """Swap function while ensuring LSP-consistency"""
        self.engine.write(self.unit, new_func)
        # CHECK: self.func: Callable[In, Out] = new_func
        self.func = new_func
        self.bind = False
        return self

    def morph[**Bound, Opened](self, new_func: Callable[Bound, Opened]) -> Self:
        # TASK: reassgin signature?
        # - at least track level of LSP-violatons
        """Swap function while ignoring LSP-violatons"""
        if not isinstance(self.engine, MorphingField):
            raise self.engine.raiser.Function(
                self.engine,
                self.unit,
                message=f"Morphing forbidden on {self}!",
                value=new_func,
            )
        # NEXT:
        # self.engine.write(self.unit, new_func)
        # self.func = new_func
        # CHECK: self.func: Callable[Bound, Opened] = new_func
        self.bind = False
        return self
