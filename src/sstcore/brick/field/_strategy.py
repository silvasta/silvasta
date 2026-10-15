"""
Exchange Callables on Classes

- StrategyField:
                                                 DependencyLevel[3]
"""

__all__: list[str] = [
    "StrategyField",
    # "strategy",
    "MorphingField",
    # "morphing",
    #
    "MethodFieldEngine",
    "BoundStrategy",
]

from collections.abc import Callable
from inspect import Parameter, Signature, _ParameterKind, signature
from typing import Any, Concatenate, Self, overload

from ...port import attach
from ...port.link import portlink
from .. import reflect
from ._decorate import DecoratedField
from ._extend import ResetField

# REMOVE: when replacement looks proper
# def strategy[Owner, **In, Out](
#     func: Callable[Concatenate[Owner, In], Out],
# ) -> attach.CallingDescriptor[In, Out]:
#     """Attach StrategyField to a method, stripping `self` for bound calls."""
#     return StrategyField(func, bind_to_self=True)
# REMOVE: when replacement looks proper
# def morphing[Owner, **In, Out](
#     func: Callable[Concatenate[Owner, In], Out],
# ) -> attach.MorphingDescriptor[In, Out]:
#     """Attach MorphingField to a method, stripping `self` for bound calls."""
#     return MorphingField(func, bind_to_self=True)


@portlink(attach.DecoDescriptor)
class MethodFieldEngine[**In, Out](DecoratedField[In, Out], ResetField):
    """Base Engine for dynamic Callable fields."""

    def __init__(
        self,
        func: Callable[..., Out] | None = None,
        *args: Any,
        bind_to_self: bool = True,  # Default True for class methods!
        **kwargs: Any,
    ):
        self.bind_to_self: bool = bind_to_self
        super().__init__(func, *args, **kwargs)

    def bind(self, func: Callable[..., Out]) -> None:
        super().bind(func)
        if self.signature is not None:
            self.signature = _extract_signature(
                func, bind_to_self=self.bind_to_self
            )

    def write(self, unit: object, value: Callable[In, Out]) -> None:
        """Store an instance override directly as a callable (never bound to self)."""
        _value = self.validate(unit, value)
        self._set_val(unit, _value)

    def read(self, unit: object) -> BoundStrategy[In, Out]:
        if self._has_val(unit):
            return BoundStrategy(self, unit, self._get_val(unit), bind=False)
        if self.target_func is not None:
            return BoundStrategy(
                self, unit, self.target_func, bind=self.bind_to_self
            )
        raise self.raiser.Function(self, unit, "Missing target_func")

    # AI: still needed?
    def switch(self, func: Callable[In, Out]) -> Self:
        """Modify the Class-Level baseline strategy."""
        self.bind(func)
        return self


@portlink(attach.CallingDescriptor)
class StrategyField[**In, Out](MethodFieldEngine[In, Out]):
    """Forces the override to match the default function's signature."""

    # AI_QUESTION: is this needed here at this level??
    @overload
    def __init__(
        self,
        func: Callable[Concatenate[Any, In], Out],
        *args: Any,
        bind_to_self: bool = True,
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
        super().__init__(func, *args, bind_to_self=bind_to_self, **kwargs)

    # def __call__(self, func: Callable[Concatenate[Any, In], Out]) -> Self:
    #     self.bind(func)
    #     return self

    def validate(
        self, unit: object, value: Callable[In, Out]
    ) -> Callable[In, Out]:
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

    def morph(self, func: Callable[..., Any]) -> Self:
        """Unsafe Function Exchange on the Class Level."""
        self.bind(func)
        return self

    def validate(self, unit: object, value: Callable) -> Callable:
        """Permit arbitrary Callables"""
        if not callable(value):
            raise self.raiser.Function(self, unit, value=value)
        return value


class BoundStrategy[**In, Out]:
    """Proxy object that acts as a bound method and provides swap mutations."""

    def __init__(
        self,
        engine: MethodFieldEngine[In, Out],
        unit: object,
        func: Callable[In, Out],
        bind: bool = True,
    ):
        self.engine: MethodFieldEngine[In, Out] = engine
        self.unit: Any = unit
        self.func: Callable[In, Out] = func
        self.bind: bool = bind

    @property
    def __name__(self) -> str:
        return reflect.funcname(self.func)

    # AI: check still proper?
    def __call__(self, *args: In.args, **kwargs: In.kwargs) -> Out:
        if self.bind:
            return self.func(self.unit, *args, **kwargs)
        return self.func(*args, **kwargs)

    # AI: check still needed?
    def switch(self, new_func: Callable[In, Out]) -> Self:
        """Swap function while ensuring LSP-consistency"""
        self.engine.write(self.unit, new_func)
        self.func: Callable[In, Out] = new_func
        self.bind = False
        return self

    def morph[**Bound, Opened](
        self, new_func: Callable[Bound, Opened]
    ) -> Self:
        """Swap function while ignoring LSP-violatons"""
        if not isinstance(self.engine, MorphingField):  # CHECK: needed?
            raise self.engine.raiser.Function(
                self.engine,  # LATER: raise from engine??
                self.unit,
                message="Morphing forbidden on StrategyField!",  # CHECK:
                value=new_func,
            )
        self.engine.write(self.unit, new_func)  # ty:ignore
        self.func: Callable[Bound, Opened] = new_func
        self.bind = False  # CHECK:
        return self


#  LINE: -- Signature Checks -- -- - -- -- - -- -- - -- -- - -- -- - -- --
#  MOVE: -- probably to brick.call._inspect


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
