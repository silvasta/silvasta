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
from ...port.empty import MayNot
from ...port.link import portlink
from ...port.sigspect import LspViolation
from .. import reflect
from ..call.lsp import SigSpec
from ._base import WriteField
from ._decorate import CallableField, MaybeBound, SelfBound


@portlink(attach.CallingDescriptor)
class StrategyField[**In, Out](CallableField[In, Out]):
    """
    Base Engine for Dynamic Callable Fields

    - unit.field: return the direct Callable[In, Out] (or mounted Functor)
    - Owner.field.switch(fn) toggle the strategy for the entire class
    - unit.field = fn or Owner.field.switch(fn, unit) overrides for one instance
    - Owner.field.bound(unit): return a BoundStrategy inspector/controller
    """

    @overload
    def __init__(
        self,
        func: SelfBound[In, Out],
        *args,
        bind_to_self: Literal[True] = True,
        tolerance: LspViolation = LspViolation.ZERO,
        **kwargs,
    ) -> None: ...
    @overload
    def __init__(
        self,
        func: Callable[In, Out],
        *args,
        bind_to_self: Literal[False],
        tolerance: LspViolation = LspViolation.ZERO,
        **kwargs,
    ) -> None: ...
    @overload
    def __init__(
        self,
        func: None = None,
        *args,
        bind_to_self: bool = True,
        tolerance: LspViolation = LspViolation.ZERO,
        **kwargs,
    ) -> None: ...
    def __init__(
        self,
        func: MaybeBound[In, Out] | None = None,
        *args,
        bind_to_self: bool = True,
        tolerance: LspViolation = LspViolation.ZERO,
        **kwargs,
    ):
        """Overload for Method or Function"""

        self.tolerance: LspViolation = tolerance
        self.bind_to_self: bool = bind_to_self
        self.signature: SigSpec | None = None
        super().__init__(func, *args, bind_to_self=bind_to_self, **kwargs)

    # RENAME: per_unit_bound??
    def bound(self, unit: object) -> BoundStrategy[In, Out]:
        """Return an explicit BoundStrategy controller/inspector for `unit`."""
        return BoundStrategy(self, unit)

    def __call__(self, func: SelfBound[In, Out]) -> Self:
        """Bind method when used as parameterized decorator @StrategyField(...)"""
        # REMOVE: 1:1 copy of FieldDecorator??
        self.bind_target_func(func)
        return self

    @portlink.tap.watch
    def bind_target_func(
        self, func: Callable[Concatenate[Any, In], Out] | Callable[In, Out]
    ) -> None:
        super().bind_target_func(func)
        # CHECK: before or after bind_target_func?
        self.signature: SigSpec = self._create_sig(func)

    def _create_sig(
        self,
        func: Callable,
        /,
        *,
        bind_to_self: MayNot[bool] = None,
        tolerance: MayNot[LspViolation] = None,
    ) -> SigSpec:
        _bind = self.bind_to_self if bind_to_self is None else bind_to_self
        return SigSpec.detect(
            func,
            bind_to_self=_bind,
            tolerance=self.tolerance if tolerance is None else tolerance,
        )

    def validate(
        self,
        unit: object,
        value: Callable[..., Any],
        *,
        bind_to_self: MayNot[bool] = None,
    ) -> Callable[In, Out]:
        """Enforce signature rules for instance-level overrides (`unit.field = fn`)."""
        value: Callable[..., Any] = super().validate(unit, value)
        candidate: SigSpec = self._create_sig(value, bind_to_self=bind_to_self)
        # CHECK: when is self.signature=None possible?
        if self.signature is None or not self.signature.allows(other=candidate):
            raise self.raiser.Signature(
                self, unit, value=value, sig1=self.signature, sig2=candidate
            )
        return value

    def switch(
        self, func: Callable[..., Any], unit: object | None = None
    ) -> Self:
        """Swap class-level baseline (`unit=None`) or instance-level strategy."""
        # IMPORTANT: del old function??
        if unit is None:
            self.validate(type(self), func, bind_to_self=self.bind_to_self)
            self.bind_target_func(func)
        else:
            self.write(unit, func)
        return self

    def clone(
        self,
        func: Callable[..., Any] | None = None,
        *,
        bind_to_self: bool | None = None,
        tolerance: LspViolation | None = None,
    ) -> Self:
        _bind = self.bind_to_self if bind_to_self is None else bind_to_self
        return type(self)(
            self.target_func if func is None else func,
            bind_to_self=_bind,
            tolerance=self.tolerance if tolerance is None else tolerance,
            default=self.default,
            frozen=self.frozen,
        )


@portlink(attach.MorphingDescriptor)
class MorphingField[**In, Out](StrategyField[In, Out]):
    """Allows swapping methods with arbitrary new signatures via `.morph()`."""

    # REMOVE:
    # def __call__[**CallIn, CallOut](
    #     self, func: Callable[Concatenate[Any, CallIn], CallOut]
    # ) -> MorphingField[CallIn, CallOut]:
    #     self.bind(func)  # type: ignor
    #     return self  # type: ignor

    def morph(
        self, func: Callable[..., Any], unit: object | None = None
    ) -> Self:
        """Unsafe function exchange on the Class or Instance level."""
        target: object = type(self) if unit is None else unit
        # REMOVE: any bypassing of the MRO chain!!!
        CallableField.validate(self, target, func)
        if unit is None:
            self.bind_target_func(func)
        else:
            # REMOVE: any bypassing of the MRO chain!!!
            WriteField.write(self, unit, func)
        return self


class BoundStrategy[**In, Out]:
    """Obtain via OwnerClass.field.bound(unit)"""

    def __init__(self, field: StrategyField[In, Out], unit: Any):
        self.field: StrategyField[In, Out] = field
        self.unit: Any = unit
        self.__name__: str = reflect.funcname(self.func)

    @property
    def is_overridden(self) -> bool:
        """Does the instance hold a custom strategy override?"""
        return self.field._has_val(self.unit)

    @property
    def is_bound(self) -> bool:
        """Is the Unit passed as leading 'self' argument?"""
        if self.field._has_val(self.unit):
            return False
        return self.field.bind_to_self

    @property
    def func(self) -> Callable[..., Out]:
        """Currently active underlying Callable"""

        if self.field._has_val(self.unit):
            return self.field._get_val(self.unit)

        if self.field.target_func is not None:
            return self.field.target_func

        raise self.field.raiser.Function(
            self.field, self.unit, "Missing Target Function"
        )

    @property
    def signature(self) -> SigSpec:
        """Active SigSpec of the currently mounted callable."""
        if (
            not self.is_overridden
            and self.func is self.field.target_func
            and self.field.signature is not None
        ):
            return self.field.signature
        return SigSpec.detect(
            self.func,
            bind_to_self=self.is_bound,
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
