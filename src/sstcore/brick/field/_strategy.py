"""
Exchange Callables on Classes

- StrategyField:
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
from inspect import Parameter, Signature, _ParameterKind, signature
from typing import Any, Self

from ...port import attach
from ...port.calling import Calling
from ...port.link import portlink
from ._decorate import DecoratedField
from ._extend import ResetField


def strategy[F: Callable[..., Any]](func: F) -> F:
    """Mark the Field for StrategyField assembling"""
    func.__field_kind__ = StrategyField  # type: ignore
    return func


def morphing[F: Callable[..., Any]](func: F) -> F:
    """Mark the Field for MorphingField assembling"""
    func.__field_kind__ = MorphingField  # type: ignore
    return func


@portlink(attach.DecoDescriptor)
class MethodFieldEngine[**In, Out](DecoratedField[In, Out], ResetField):
    """Base Engine for dynamic Calling fields."""

    def __init__(
        self,
        func: Calling[In, Out],
        *args: Any,
        bind_to_self: bool = False,
        **kwargs: Any,
    ):
        """Map func to DecoratedField.target_func"""
        self.bind_to_self: bool = bind_to_self
        default: Any = kwargs.pop("default", (func, bind_to_self))
        super().__init__(func, *args, default=default, **kwargs)
        if func is not None and self.signature is not None:
            self.signature: Signature = _extract_signature(
                func, bind_to_self=bind_to_self
            )

    def write(self, unit: object, value: Calling[In, Out]) -> None:
        """Store an instance override as (func, bind=False).

        Replacements match the *public* signature, so they are not bound
        to the unit. The 2-tuple is the same shape as the field default
        `(target_func, binds_instance)` that reset writes back.
        """
        _value = self.validate(unit, value)
        # TASK: unsure if the tuple with the bool belongs to unit.__dict__
        # - when it is anyway False, why storing this information?
        self._set_val(unit, (_value, False))

    def read(self, unit: object) -> BoundStrategy[In, Out]:
        if self._has_val(unit):
            _func, _bind = self._get_val(unit)
        elif self.target_func is not None:
            _func, _bind = self.target_func, self.bind_to_self
        else:
            raise self.raiser.Function(self, unit, "Missing target_func")
        return BoundStrategy(self, unit, _func, bind=_bind)

    def switch(self, func: Calling[In, Out]) -> Self:
        """Modify the Class-Level baseline strategy."""
        self.bind(func)
        return self


@portlink(attach.CallingDescriptor)
class StrategyField[**In, Out](MethodFieldEngine[In, Out]):
    """Forces the override to match the default function's signature."""

    def validate(
        self, unit: object, value: Calling[In, Out]
    ) -> Calling[In, Out]:
        """Enforce strict signature rules for instance-level overrides."""

        if not callable(value):
            raise self.raiser.Function(self, unit, value=value)

        if self.signature is None:  # Fallback if un-bound properly
            raise self.raiser.Signature(self, unit, value=value)

        if not _valid_sig(value, baseline=self.signature):
            raise self.raiser.Signature(self, unit, value=value)

        return value


@portlink(attach.MorphingDescriptor)
class MorphingField[**In, Out](MethodFieldEngine[In, Out]):
    """Allows swapping methods with arbitrary new signatures."""

    def morph(self, func: Calling[..., Any]) -> Self:
        # LATER: check [B=In&Any,S=Out&|&&|Any]
        """Unsafe Function Exchange on the Class Level."""
        self.bind(func)
        return self

    def _write(self, unit: object, value: Calling[..., Any]) -> None:
        # IMPORTANT: is this needed (as MorphingField.write), wired proper otherwise???
        """Instance override; signature is not a contract."""
        _value = self.validate(unit, value)
        self._set_val(unit, (_value, False))

    def validate(self, unit: object, value: Calling) -> Calling:
        """Permit arbitrary Callings."""
        if not callable(value):
            raise self.raiser.Function(self, unit, value=value)
        return value


class BoundStrategy[**In, Out]:
    """Proxy object that acts as a bound method and provides swap mutations."""

    def __init__(
        self,
        engine: MethodFieldEngine[In, Out],
        unit: object,
        func: Calling[In, Out],
        bind: bool = True,
    ):
        self.engine: MethodFieldEngine[In, Out] = engine
        self.unit: Any = unit
        self.func: Calling[In, Out] = func
        self.bind: bool = bind

    @property
    def __name__(self) -> str:
        return self.func.__name__

    def __call__(self, *args: In.args, **kwargs: In.kwargs) -> Out:
        if self.bind:
            return self.func(self.unit, *args, **kwargs)
        return self.func(*args, **kwargs)

    def switch(self, new_func: Calling[In, Out]) -> Self:
        """Swap function while ensuring LSP-consitency"""
        self.engine.write(self.unit, new_func)
        self.func: Calling[In, Out] = new_func
        self.bind = False
        return self

    def morph[**Bound, Opened](self, new_func: Calling[Bound, Opened]) -> Self:
        """Swap function while ignoring LSP-violatons"""
        if not isinstance(self.engine, MorphingField):  # CHECK: needed?
            raise self.engine.raiser.Function(
                self.engine,  # LATER: raise from engine??
                self.unit,
                message="Morphing forbidden on StrategyField!",  # CHECK:
                value=new_func,
            )
        self.engine.write(self.unit, new_func)  # ty:ignore
        self.func: Calling[Bound, Opened] = new_func
        self.bind = False  # CHECK:
        return self


#  LINE: -- Signature Checks -- -- - -- -- - -- -- - -- -- - -- -- - -- --
#  MOVE: -- probably to brick.labor.***


def _extract_signature(func: Callable, *, bind_to_self: bool) -> Signature:
    sig: Signature = signature(func)
    if not bind_to_self:
        return sig
    params: list[Parameter] = list(sig.parameters.values())
    if params and params[0].kind in (
        Parameter.POSITIONAL_ONLY,
        Parameter.POSITIONAL_OR_KEYWORD,
    ):
        # CHECK: return sig instead of nop replace??
        params: list[Parameter] = params[1:]
    return sig.replace(parameters=params)


def _valid_sig(func: Callable, baseline: Signature) -> bool:
    try:
        new_sig: Signature = signature(func)
    except ValueError:
        return False
    # LATER: Extend list maybe by level
    # (Liskov Substitution checks)
    checks_ok: list[bool] = [
        _is_open_signature(baseline),
        _check_sig_param_length(new_sig, baseline),
    ]
    return all(checks_ok)


def _is_open_signature(sig: Signature) -> bool:
    """Placeholder (*args, **kwargs) is not a real contract."""
    kinds: list[_ParameterKind] = [p.kind for p in sig.parameters.values()]
    return kinds in (
        [],
        [Parameter.VAR_POSITIONAL],
        [Parameter.VAR_POSITIONAL, Parameter.VAR_KEYWORD],
    )


def _check_sig_param_length(sig1: Signature, sig2: Signature) -> bool:
    """Compare argument counts for strict strategy swapping."""
    sig1_clean: Signature = _strip_self(sig1)
    sig2_clean: Signature = _strip_self(sig2)
    return len(sig1_clean.parameters) == len(sig2_clean.parameters)


def _strip_self(sig: Signature) -> Signature:
    """Helper to remove 'self' from signature for fair comparison."""
    params: list[Parameter] = list(sig.parameters.values())
    if params and params[0].name in ("self", "cls"):
        return sig.replace(parameters=params[1:])
    return sig
