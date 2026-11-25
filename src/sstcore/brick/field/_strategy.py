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
from ...port.casting import LspViolation
from ...port.link import portlink
from .. import reflect
from ..call import SigSpec
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
        tolerance: LspViolation = LspViolation.ZERO,
        **kwargs: Any,
    ) -> None: ...
    @overload
    def __init__(
        self,
        func: Callable[In, Out],
        *args: Any,
        bind_to_self: Literal[False],
        tolerance: LspViolation = LspViolation.ZERO,
        **kwargs: Any,
    ) -> None: ...
    @overload
    def __init__(
        self,
        func: None = None,
        *args: Any,
        bind_to_self: bool = True,
        tolerance: LspViolation = LspViolation.ZERO,
        **kwargs: Any,
    ) -> None: ...
    def __init__(
        self,
        func: Callable[..., Out] | None = None,
        *args: Any,
        bind_to_self: bool = True,
        tolerance: LspViolation = LspViolation.ZERO,
        **kwargs: Any,
    ):
        """Decorate with or without Params"""
        self.bind_to_self: bool = bind_to_self
        super().__init__(func, *args, tolerance=tolerance, **kwargs)

    def bind(self, func: Callable[..., Out]) -> None:
        super().bind(func)
        if self.signature is not None:
            self.signature = SigSpec.detect(
                func,
                bind_to_self=self.bind_to_self,
                tolerance=self.tolerance,
            )

    def read(self, unit: object) -> BoundStrategy[In, Out]:
        # AI_TASK: here gets the ReadField.__get__ overload lost
        if self._has_val(unit):
            return BoundStrategy(self, unit, self._get_val(unit), bind=False)
        if self.target_func is not None:
            return BoundStrategy(
                self, unit, self.target_func, bind=self.bind_to_self
            )
        raise self.raiser.Function(self, unit, "Missing Target Function")

    def switch(self, func: Callable[..., Out]) -> Self:
        """Modify Class-Level baseline strategy while ensuring LSP consistency"""
        if not callable(func):
            raise self.raiser.Function(self, type(self), value=func)
        candidate: SigSpec = SigSpec.detect(
            func,
            bind_to_self=self.bind_to_self,
            tolerance=self.tolerance,
        )
        if self.signature is not None and candidate not in self.signature:
            raise self.raiser.Signature(self, type(self), value=func)
        self.bind(func)
        return self


@portlink(attach.CallingDescriptor)
class StrategyField[**In, Out](MethodFieldEngine[In, Out]):
    """Forces the override to match the default function's signature"""

    def validate(
        self, unit: object, value: Callable[In, Out]
    ) -> Callable[In, Out]:
        """Enforce strict signature rules for instance-level overrides"""

        value: Callable[In, Out] = super().validate(unit, value)

        if self.signature is None or value not in self.signature:
            raise self.raiser.Signature(self, unit, value=value)

        return value


@portlink(attach.MorphingDescriptor)
class MorphingField[**In, Out](MethodFieldEngine[In, Out]):
    """Allows swapping methods with arbitrary new signatures"""

    def morph(self, func: Callable[..., Any]) -> Self:
        """Unsafe Function Exchange on the Class Level"""
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

    @property
    def signature(self) -> SigSpec:
        """Active SigSpec of the currently mounted callable."""
        if (
            self.func is self.engine.target_func
            and self.engine.signature is not None
        ):
            return self.engine.signature
        return SigSpec.detect(
            self.func,
            bind_to_self=self.bind,
            tolerance=self.engine.tolerance,
        )

    @property
    def violation(self) -> LspViolation:
        """LSP violation flags of the active callable relative to the engine baseline."""
        if self.engine.signature is None:
            return LspViolation.ZERO
        return self.engine.signature >> self.signature

    def __call__(self, *args: In.args, **kwargs: In.kwargs) -> Out:
        if self.bind:
            return self.func(self.unit, *args, **kwargs)
        return self.func(*args, **kwargs)

    def __getattr__(self, name: str) -> Any:  # TEST:
        """Keep mounted callable objects (LogEmitter, …) intact"""
        return getattr(self.func, name)

    def switch(self, new_func: Callable[In, Out]) -> Self:
        """Swap function while ensuring LSP-consistency"""
        if (
            self.engine.signature is not None
            and new_func not in self.engine.signature
        ):
            raise self.engine.raiser.Signature(
                self.engine, self.unit, value=new_func
            )
        self.engine.write(self.unit, new_func)
        self.func = new_func
        self.bind = False
        return self

    def morph[**Bound, Opened](self, new_func: Callable[Bound, Opened]) -> Self:
        """Swap function while ignoring LSP-violations (MorphingField only)"""
        if not isinstance(self.engine, MorphingField):
            raise self.engine.raiser.Function(
                self.engine,
                self.unit,
                message=f"Morphing forbidden on {self}!",
                value=new_func,
            )
        self.engine.write(self.unit, new_func)  # ty: ignore
        self.func = new_func  # ty: ignore
        self.bind = False
        return self

    def reset(self) -> Self:
        """Restore the instance strategy back to the class-level baseline."""
        self.engine.remove(self.unit)
        if self.engine.target_func is not None:
            self.func = self.engine.target_func
            self.bind = self.engine.bind_to_self
        return self
