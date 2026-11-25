"""
Exchange Callables on Classes

- StrategyField: strict signature-checked callable field
- MorphingField: signature-agnostic callable field
- BoundStrategy: opt-in inspector and controller view for a StrategyField on a unit

                                                 DependencyLevel[3]
"""

__all__: list[str] = [
    "StrategyField",
    "MorphingField",
    "BoundStrategy",
]

from collections.abc import Callable
from typing import Any, Concatenate, Literal, Self, overload

from ...port import attach
from ...port.casting import LspViolation
from ...port.link import portlink
from .. import reflect
from ..call import SigSpec
from ._base import WriteField
from ._decorate import CallableField


@portlink(attach.CallingDescriptor)
class StrategyField[**In, Out](CallableField[In, Out]):
    """
    Base Engine for Dynamic Callable Fields

    - unit.field: return the direct Callable[In, Out] (or mounted Functor)
    - Owner.field.switch(fn) toggle the strategy for the entire class
    - unit.field = fn or Owner.field.switch(fn, unit) overrides for one instance
    - Owner.field.bound(unit): return a BoundStrategy inspector/controller
    """

    signature: SigSpec | None = None

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
    ) -> None:
        self.tolerance: LspViolation = tolerance
        super().__init__(func, *args, bind_to_self=bind_to_self, **kwargs)

    def __call__[**CallIn, CallOut](
        self,
        func: Callable[Concatenate[Any, CallIn], CallOut],
    ) -> StrategyField[CallIn, CallOut]:  # ty:ignore
        """Bind method when used as parameterized decorator @StrategyField(...)"""
        self.bind(func)  # ty:ignore
        return self  # ty: ignore

    def bind(self, func: Callable[..., Out]) -> None:
        super().bind(func)
        self.signature = SigSpec.detect(
            func,
            bind_to_self=self.bind_to_self,
            tolerance=self.tolerance,
        )

    def validate_signature(
        self,
        unit: object,
        value: Callable[..., Any],
        *,
        bind_to_self: bool = False,
    ) -> Callable[In, Out]:
        """Validate callability and check SigSpec compatibility under self.tolerance."""
        value = super().validate(unit, value)
        candidate: SigSpec = SigSpec.detect(
            value,
            bind_to_self=bind_to_self,
            tolerance=self.tolerance,
        )
        if self.signature is None or candidate not in self.signature:
            raise self.raiser.Signature(self, unit, value=value)
        return value

    def validate(
        self, unit: object, value: Callable[..., Any]
    ) -> Callable[In, Out]:
        """Enforce signature rules for instance-level overrides (`unit.field = fn`)."""
        return self.validate_signature(unit, value, bind_to_self=False)

    def switch(
        self, func: Callable[..., Any], unit: object | None = None
    ) -> Self:
        """Swap class-level baseline (`unit=None`) or instance-level strategy."""
        if unit is None:
            self.validate_signature(
                type(self), func, bind_to_self=self.bind_to_self
            )
            self.bind(func)
        else:
            self.write(unit, func)
        return self

    def bound(self, unit: object) -> BoundStrategy[In, Out]:
        """Return an explicit BoundStrategy controller/inspector for `unit`."""
        return BoundStrategy(self, unit)


@portlink(attach.MorphingDescriptor)
class MorphingField[**In, Out](StrategyField[In, Out]):
    """Allows swapping methods with arbitrary new signatures via `.morph()`."""

    def __call__[**CallIn, CallOut](
        self, func: Callable[Concatenate[Any, CallIn], CallOut]
    ) -> MorphingField[CallIn, CallOut]:
        self.bind(func)  # type: ignore
        return self  # type: ignore

    def morph(
        self, func: Callable[..., Any], unit: object | None = None
    ) -> Self:
        """Unsafe function exchange on the Class or Instance level."""
        target: object = type(self) if unit is None else unit
        CallableField.validate(self, target, func)
        if unit is None:
            self.bind(func)
        else:
            WriteField.write(self, unit, func)
        return self


class BoundStrategy[**In, Out]:
    """Obtain via OwnerClass.field.bound(unit)"""

    def __init__(
        self,
        field: StrategyField[In, Out],
        unit: Any,
    ) -> None:
        self.field: StrategyField[In, Out] = field
        self.unit: Any = unit

    @property
    def is_overridden(self) -> bool:
        """Whether the instance holds a custom strategy override."""
        return self.field._has_val(self.unit)

    @property
    def func(self) -> Callable[..., Out]:
        """Currently active underlying callable for this unit."""
        if self.field._has_val(self.unit):
            return self.field._get_val(self.unit)
        if self.field.target_func is not None:
            return self.field.target_func
        raise self.field.raiser.Function(
            self.field, self.unit, "Missing Target Function"
        )

    @property
    def bind(self) -> bool:
        """Whether `unit` is passed as the leading `self` argument."""
        if self.field._has_val(self.unit):
            return False
        return self.field.bind_to_self

    @property
    def __name__(self) -> str:
        return reflect.funcname(self.func)

    @property
    def signature(self) -> SigSpec:
        """Active SigSpec of the currently mounted callable."""
        active_func = self.func
        if (
            not self.is_overridden
            and active_func is self.field.target_func
            and self.field.signature is not None
        ):
            return self.field.signature
        return SigSpec.detect(
            active_func,
            bind_to_self=self.bind,
            tolerance=self.field.tolerance,
        )

    @property
    def violation(self) -> LspViolation:
        """LSP violation flags of the active callable relative to the field baseline."""
        if self.field.signature is None:
            return LspViolation.ZERO
        return self.field.signature >> self.signature

    def __call__(self, *args: In.args, **kwargs: In.kwargs) -> Out:
        return self.field.read(self.unit)(*args, **kwargs)

    def switch(self, new_func: Callable[..., Any]) -> Self:
        """Swap instance function while ensuring LSP-consistency."""
        self.field.switch(new_func, self.unit)
        return self

    def reset(self) -> Self:
        """Restore the instance strategy back to the class-level baseline."""
        self.field.remove(self.unit)
        return self
