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
from ._base import DeleteField, ReadField, WriteField
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

    def __call__[**CallIn, CallOut](
        self, func: Callable[Concatenate[Any, CallIn], CallOut]
    ) -> MethodFieldEngine[CallIn, CallOut]:
        """Bind method when used as parameterized decorator @MethodFieldEngine(...)"""
        self.bind(func)
        return self

    def bind(self, func: Callable[..., Out]) -> None:
        super().bind(func)
        if self.signature is not None:
            self.signature = SigSpec.detect(
                func,
                bind_to_self=self.bind_to_self,
                tolerance=self.tolerance,
            )

    def read(self, unit: object) -> BoundStrategy[In, Out]:
        if not self._has_val(unit) and self.target_func is None:
            raise self.raiser.Function(self, unit, "Missing Target Function")
        return BoundStrategy(self, unit)

    def validate_signature(
        self,
        unit: object,
        value: Callable[..., Any],
        *,
        bind_to_self: bool = False,
    ) -> Callable[In, Out]:
        """Validate callable and check SigSpec compatibility under self.tolerance."""
        value = super().validate(unit, value)
        candidate: SigSpec = SigSpec.detect(
            value,
            bind_to_self=bind_to_self,
            tolerance=self.tolerance,
        )
        if self.signature is None or candidate not in self.signature:
            raise self.raiser.Signature(self, unit, value=value)
        return value

    def switch(
        self, func: Callable[..., Any], unit: object | None = None
    ) -> Self:
        """Swap class-level baseline or instance-level strategy with LSP validation."""
        if unit is None:
            self.validate_signature(
                type(self), func, bind_to_self=self.bind_to_self
            )
            self.bind(func)
        else:
            self.validate_signature(unit, func, bind_to_self=False)
            # FIX: why is here WriteField?? otherwise just skip DecoDescriptor that anyway causes so much conflicts
            WriteField.write(self, unit, func)
        return self

    def morph(
        self, func: Callable[..., Any], unit: object | None = None
    ) -> Self:
        """Unsafe strategy replacement (permitted only on MorphingField)."""
        target: object = type(self) if unit is None else unit
        raise self.raiser.Function(
            self,
            target,
            message=f"Morphing forbidden on {self}!",
            value=func,
        )


@portlink(attach.CallingDescriptor)
class StrategyField[**In, Out](MethodFieldEngine[In, Out]):
    """Forces the override to match the default function's signature"""

    def __call__[**CallIn, CallOut](
        self, func: Callable[Concatenate[Any, CallIn], CallOut]
    ) -> StrategyField[CallIn, CallOut]:
        """Bind method when used as parameterized decorator @StrategyField(...)"""
        self.bind(func)
        return self

    def validate(
        self, unit: object, value: Callable[..., Any]
    ) -> Callable[In, Out]:
        """Enforce signature rules for instance-level overrides"""
        return self.validate_signature(unit, value, bind_to_self=False)


@portlink(attach.MorphingDescriptor)
class MorphingField[**In, Out](MethodFieldEngine[In, Out]):
    """Allows swapping methods with arbitrary new signatures"""

    def __call__[**CallIn, CallOut](
        self, func: Callable[Concatenate[Any, CallIn], CallOut]
    ) -> MorphingField[CallIn, CallOut]:
        """Bind method when used as parameterized decorator @MorphingField(...)"""
        self.bind(func)
        return self

    def morph(
        self, func: Callable[..., Any], unit: object | None = None
    ) -> Self:
        """Unsafe Function Exchange on the Class or Instance Level"""
        target: object = type(self) if unit is None else unit
        super().validate(target, func)
        if unit is None:
            self.bind(func)
        else:
            WriteField.write(self, unit, func)
        return self


class BoundStrategy[**In, Out]:
    """Proxy object that acts as a bound method and provides swap mutations."""

    def __init__(
        self,
        engine: MethodFieldEngine[In, Out],
        unit: Any,
        func: Callable[..., Out] | None = None,
        bind: bool | None = None,
    ) -> None:
        _ = func, bind
        self.engine: MethodFieldEngine[In, Out] = engine
        self.unit: Any = unit

    @property
    def is_overridden(self) -> bool:
        """Whether the instance holds a custom strategy override."""
        return self.engine._has_val(self.unit)

    @property
    def func(self) -> Callable[..., Out]:
        """Currently active callable for this unit."""
        if self.engine._has_val(self.unit):
            return self.engine._get_val(self.unit)
        if self.engine.target_func is not None:
            return self.engine.target_func
        raise self.engine.raiser.Function(
            self.engine, self.unit, "Missing Target Function"
        )

    @property
    def bind(self) -> bool:
        """Whether `unit` should be passed as the leading `self` argument."""
        if self.engine._has_val(self.unit):
            return False
        return self.engine.bind_to_self

    @property
    def __name__(self) -> str:
        return reflect.funcname(self.func)

    @property
    def signature(self) -> SigSpec:
        """Active SigSpec of the currently mounted callable."""
        active_func = self.func
        if (
            not self.is_overridden
            and active_func is self.engine.target_func
            and self.engine.signature is not None
        ):
            return self.engine.signature
        return SigSpec.detect(
            active_func,
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

    # REMOVE: if not absolutely required
    # def __getattr__(self, name: str) -> Any:
    #     """Keep mounted callable objects (LogEmitter, …) intact"""
    #     return getattr(self.func, name)

    def switch(self, new_func: Callable[..., Any]) -> Self:
        """Swap function while ensuring LSP-consistency"""
        self.engine.switch(new_func, self.unit)
        return self

    def morph(self, new_func: Callable[..., Any]) -> Self:
        """Swap function while ignoring LSP-violations (MorphingField only)"""
        self.engine.morph(new_func, self.unit)
        return self

    def reset(self) -> Self:
        """Restore the instance strategy back to the class-level baseline."""
        self.engine.remove(self.unit)
        return self
